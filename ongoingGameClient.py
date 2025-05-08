import pygame
from ongoingGameServer import OngoingGameServer
#from ongoingGameWindow import OngoingGameWindow
from client import Client
import socket
from threading import Thread
import json
from os import path as filePath

import piecesMoves as pMoves

class OngoingGameClient:

    def __init__(self, addr, join=False):
 
        self.__incodetable = ("0123456789abcdefghijklmnopqrstuvwxyz","%%","[],.()","-")

        pygame.init() # Инициализируем pygame
        self.__pause = True # Стоит ли игра на паузе
        self.__state = 0 # Состояние клиента (и сервера)
        self.__player = [] # Массив игроков
        self.__demoPieces = [{},{}] # Фигуры на стадии подготовки
        self.__playerReady = [False,False] # Кнопка готов
        self.__playerSurrender = [False,False] # Кнопка сдаться
        self.__textChat = [] # История текстового чата
        self.__battleMoves = [] # Ходы в этой битве

        self.__currentLVL = 0 # Текущий уровень игры
        self.__levels = [] # Уровни игры
        
        self.__movequeue = [0,1] # Очередь для ходов
        self.__currentmove = -1 # Текущий ход (индекс объекта self.__movequeue),
        # Где -1 означает ничей ход
        
        # Максимальный размер доски, её строки и столбцы
        self.__desk = [0,0] # Доска
        self.__index = [] # Массивы доски и её связей
        self.__piecetypes = [] # Типы фигур
        self.__pieces = [] # Фигуры

        self.last_set_objects = ["none",0,0,0,0,0,0,0] # Последний набор объектов от сервера
        self.update_board = False
        self.last_set_interface = ["none",0,0,0,0] # Последний набор вторичных от сервера
        self.update_interface = False
        self.battleMoves = [] # Все ходы последнего матча
        self.textChat = [] # Все сообщения чата
        
        #
        #
        #
        #
        #
        
        self.__createPieceTypes() # 1 - Создаём типы фигур
        self.__createPlayers() # 2 - Создаём игроков
        self.__createLevels() # 3 - Создаём уровни

        #
        
        self.joined = join # Нужен ли сервер, False - синглплеер, True - мультиплеер
        
        # Создание битвы
        self.__firstBattle()
        

        # ОБОЛОЧКА СЕРВЕРА
        self.serverAdress = addr
        if join: # Подключаемся
            self.serverObject = 0
        else: # Или создаём сервер
            self.serverObject = OngoingGameServer(addr)

        # КЛИЕНТ
        self.clientObject = Client(addr) # Создаём клиент

        # ЦИКЛ
        Thread(target=self.infiniteLoop).start()
        
    def __printDeck(self): # Показывает доску в отладке
        return True
        s = []
        n = 0
        r = 0
        for h in range(self.__desk[1]):
            s.append("")
            for w in range(self.__desk[0]):
                #print(self.__index[h][w])
                if self.__index[h][w]<0:
                    s[len(s)-1] += "  -  "
                else:
                    s[len(s)-1] += " "+str(self.__pieces[self.__index[h][w]]["ptid"])+"_"+str(self.__pieces[self.__index[h][w]]["ownerid"])+" "
                    
        print("")
        for i in range(self.__desk[1]-1,-1,-1):
            print("i="+str(i)+"   "+s[i])
        print("")

        
    #
    ##
    ###
    ####
    ##### Уровень игры
    
    def __createLevels(self):
        path = "json//levels.json"
        if filePath.exists(path):
            with open(path,'r') as file:
                levels = json.load(file)["levels"]
                #print(levels)
        else:
            #print("Path ''json//levels.json'' not found, __createLevels")
            return False
        for l in levels:
            desk = (levels[l]["desk"]["width"],levels[l]["desk"]["height"])
            player = (levels[l]["player"]["width"],levels[l]["player"]["height"])
            self.__createLevel(levels[l]["id"],l,levels[l]["gold"],desk,player,levels[l]["pieces"])
        
    def __createLevel(self,lvlid,name,gold,desk,player,pieces):
        lvl = self.__gameLevel(lvlid,name,gold,desk,player,pieces)
        self.__levels.append(lvl)
        return lvl
    
    class __gameLevel:
        def __init__(self,lvlid,name,gold,desk,player,pieces):
            self.id = lvlid
            self.name = name
            self.gold = gold
            self.desk = desk
            self.player = player
            self.pieces = pieces

    #####
    ####
    ###
    ##
    #
    


    #
    ##
    ###
    ####
    ##### Типы фигур
        
    def __createPieceTypes(self):#,gamenames,displaynames,pcosts,ucosts,movefuncs,purchs):
        path = "json//types.json"
        if filePath.exists(path):
            with open(path,'r') as file:
                types = json.load(file)["types"]
                #print(pieces)
        else:
            print("Path ''json//types.json'' not found, __createPieceTypes")
            return False
        for t in types:
            pt = {}
            for attr in types[t]:
                pt[attr] = types[t][attr]
            self.__piecetypes.append(pt)
        return True
    
    #####
    ####
    ###
    ##
    #


    
    #
    ##
    ###
    ####
    ##### Игрок
    # Создает игроков

    def __createPlayers(self):
        for i in range(5):
            self.__player.append({"id":i,
                                  "controller":-1,
                                  "color":0,
                                  "team":[],
                                  "pawndirection":i<3,
                                  "onpassan":[],
                                  "premoves":[],
                                  "gold":[0,0],
                                  "piecesnum":[[],[]],
                                  "upgrades":[[],[]],
                                  "name":"Игрок "+str(len(self.__player))
                                  })
        self.__player[0]["team"].extend((0,1,4))
        self.__player[1]["team"].extend((0,1,4))
        self.__player[2]["team"].extend((2,3,4))
        self.__player[3]["team"].extend((2,3,4))
        self.__player[4]["team"].extend((0,1,2,3,4))
        pMoves.setTeams([(0,1,4),(0,1,4),(2,3,4),(2,3,4)]) # Обновляет команды для функций движения фигур
        for p in self.__player:
            for t in self.__piecetypes:
                p["piecesnum"][0].append(0)
                p["piecesnum"][1].append(0)
                p["upgrades"][0].append(False)
                p["upgrades"][1].append(False)
            p["piecesnum"][0][5] = 1 # Король
            p["piecesnum"][1][5] = 1

    def __addOnpassan(self,pid,moverid,squeres):
        self.__player[pid]["onpassan"].extend((moverid,squeres))
            
    def __clearOnpassan(self,pid):
        self.__player[pid]["onpassan"].clear()
            
    def __addPremove(self,pid,move):
        self.__player[pid]["premoves"].append(move)
            
    def __removeFirstPremove(self,pid):
        if len(self.__player[pid][["premoves"]])>0:
            self.__player[pid][["premoves"]].pop(0)
            
    def __clearPremoves(self,pid):
        self.__player[pid][["premoves"]].clear()
            
    #####
    ####
    ###
    ##
    #


    
    #
    ##
    ###
    ####
    ##### Фигура
    
    # Создает фигуру
    def __createPiece(self,ownerid,ptid,ind,ability=True):
        if type(ptid)!=int: # Неправильный тип
            print("Type is not int, __createPiece")
            return False
        if (ptid>=0 and ptid<len(self.__piecetypes)) and (ind>=0 and ind<self.__desk[0]*self.__desk[1]) and (ownerid>=0 and ownerid<len(self.__player)):
            if pMoves.isIndexEmpty(ind,self.__index):
                # Создаём фигуру
                mover = {"id":len(self.__pieces),
                         "ownerid":ownerid,
                         "alive":True,
                         "ptid":ptid,
                         "oldptid":ptid,
                         "index":ind,
                         "ability":ability,
                         "lastmove":0,
                         "pawndirection":self.__player[ownerid]["pawndirection"]
                         }
                self.__index[ind//self.__desk[0]][ind%self.__desk[0]] = mover["id"] # Добавляем фигуру на доску
                self.__pieces.append(mover) # Добавляем фигуру в список фигур
                
                return mover

            else:
                print("an error with placement of a new piece, index "+str(ind)+", __createPiece")
                return False
        else:
            print("an error with atributes of a new piece, __createPiece")
            return False
        print("wtf, __createPiece")
        return False

        
        
    def promotePiece(self, mover, newtype): # Превращение в другую фигуру
        mover["type"] = newtype
        mover["name"] = self.__piecetypes["name"]
        mover["ability"] = False
        mover["lastmove"] = 4
            
    #####
    ####
    ###
    ##
    #



    ##################################################################
    ##################################################################

    def __firstBattle(self):
        self.__initLevel(self.__currentLVL)
        self.__printDeck() # Выводит доску в консоль
        return True
        
    def __endBattle(self):
        self.__clearDeck()
        self.__firstBattle()
        return True

    def __initLevel(self, num):
        lvl = self.__levels[num]
        self.__createDesk(lvl.desk[0],lvl.desk[1])
        return True
    
    def __createDesk(self,width=8,height=8):
        self.__desk.clear()
        self.__desk.extend((width,height))
        count = 0
        self.__index.clear() # Массивы доски и её связей
        for h in range(self.__desk[1]):
            self.__index.append([])
            for w in range(self.__desk[0]):
                self.__index[h].append(-1)
        return True
                
    def __clearDeck(self):
        self.__index.clear() # Массивы доски и её связей
        self.__desk.clear() # Доска
        self.__desk.extend((0,0))
        self.__pieces.clear()
        return True
        
    def __removePrePieces(self):
        self.__demoPieces.clear()
        self.__demoPieces = extend(({},{}))
        return True

    def __endCampain(self):
        self.__pause = True
        return True
        
    ##################################################################
    ##################################################################
      

    def __addTextInt(self, mov, mes, names):
        for s in mov:
            self.battleMoves.append(mov)
        for s in mes:
            self.textChat.append(mes)
        self.__player[0]["name"] = names[0]
        self.__player[1]["name"] = names[1]
        return True
    
    def __updateInt(self,prev):
        for i in range(len(prev)):
            self.__demoPieces[i].clear() # Удаляем пре-фигуры
            for h in prev[i]:
                self.__demoPieces[i][h] = {} # Добавляем h пре-фигуры
                for w in prev[i][h]:
                    self.__demoPieces[i][h][w] = prev[i][h][w]
        return True

        
    def __updatePlayers(self, dePlayers):
        #
        # 0   1    2    3     4               5                     6
        #                               0      1         0      1      2          3          4           5
        # id cont color pd   team         onpassan      gold1 gold0 pieces1   upgrades1   pieces0   upgrades0
        # int int int  bool [int,...] [int, [int,...]]  [int, int, [int,...], [int,...], [int,...], [int,...]]
        #                                    []     
        for i in range(len(dePlayers)):
            p = self.__player[i]
            d = dePlayers[i]
            ###
            p["id"] = d[0]
            p["controller"] = d[1]
            p["color"] = d[2]
            p["pawndirection"] = d[3]
            p["team"] = d[4].copy()
            p["onpassan"] = d[5].copy()
            p["gold"][1] = d[6][0]
            p["gold"][0] = d[6][1]
            p["piecesnum"][1] = d[6][2].copy()
            p["upgrades"][1] = d[6][3].copy()
            p["piecesnum"][0] = d[6][4].copy()
            p["upgrades"][0] = d[6][5].copy()
        return True

    def __updatePieces(self, dePieces):
        if len(dePieces)<len(self.__pieces): # Если у сервера фигур меньше, чем надо,
            self.__pieces.clear() # Пересоздадим их полностью
        ###
        for h in self.__index: # Чистим доску
            for w in h:
                h[w] = -1
        ###
        for i in range(len(dePieces)):
            if i<len(self.__pieces):
                self.__pieces[i]["id"] = dePieces[i][0] # ID фигуры
                self.__pieces[i]["ptid"] = dePieces[i][1] # ID типа фигуры
                self.__pieces[i]["oldptid"] = dePieces[i][2] # Изначальный ID типа фигуры
                self.__pieces[i]["index"] = dePieces[i][3] # Индекс точки, к примеру 63
                self.__pieces[i]["ownerid"] = dePieces[i][4] # Индекс владельца, к примеру 1
                self.__pieces[i]["ability"] = dePieces[i][5] # Наличие уникального хода, к примеру рокировка
                self.__pieces[i]["lastmove"] = dePieces[i][6] # Последнее действие, используется другими фигурами
                self.__pieces[i]["pawndirection"] = dePieces[i][7] # Направление движения (только для фигур-пешек)
                self.__pieces[i]["alive"] = dePieces[i][8] # Жив ли                
                self.__index[self.__pieces[i]["index"]//self.__desk[0]][self.__pieces[i]["index"]%self.__desk[1]] = i # Добавляем фигуру на доску
            else:
                mover = self.__createPiece(dePieces[i][4],dePieces[i][1],dePieces[i][3],ability=dePieces[i][5])
                # 2 6 7 8
                mover["oldptid"] = dePieces[i][2]
                mover["lastmove"] = dePieces[i][6]
                mover["pawndirection"] = dePieces[i][7]
                mover["alive"] = dePieces[i][8]
        return True

    def __updateObj(self,deState,deLevel,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers):
        if not(self.last_set_objects[1]==deState and self.last_set_objects[2]==deLevel and self.last_set_objects[3]==deDesk):
            if deState==1:
                if self.__state==0:
                    self.__firstBattle() # Создать доску текущего уровня
                elif self.__state==2:
                    self.__endBattle() # Удалить все фигуры, потом
                    # пересоздать доску текущего уровня
            elif deState==3:
                self.__endCampain()

            
            self.__state = deState
            self.__currentLVL = deLevel
            ###
            self.last_set_objects[1] = deState
            self.last_set_objects[2] = deLevel
            self.last_set_objects[3] = deDesk
            # 1 2 3
        if not(self.last_set_objects[4]==deCurrMove):
            self.__currentmove = deCurrMove
            ###
            self.last_set_objects[4] = deCurrMove
            # 4
        if not(self.last_set_objects[5]==deAllMoves):
            self.__movequeue = deAllMoves
            ###
            self.last_set_objects[5] = deAllMoves
            # 5
        if not(self.last_set_objects[6]==dePieces):
            self.__updatePieces(dePieces)
            ###
            self.last_set_objects[6] = dePieces
            # 6
        if not(self.last_set_objects[7]==dePlayers):
            self.__updatePlayers(dePlayers)
            ###
            self.last_set_objects[7] = dePlayers
            # 7
        
    def __ctd(self, symbol):
        if not(len(symbol)==2 and symbol[0] in self.__incodetable[0] and symbol[1] in self.__incodetable[0]):
            return -1
        return self.__incodetable[0].index(symbol[0])*len(self.__incodetable[0]) + self.__incodetable[0].index(symbol[1])
        
    def __decodeMov(self, s):
        pos = 0
        l = len(s)
        if s[-1]!=self.__incodetable[3][0]:
            return "error with message, __decodeObj"

        i = 0
        mov = [] # Новые ходы
        while s[pos]!=self.__incodetable[2][0]:
            mov.append([])
            mov[i].append(self.__ctd(s[pos:pos+2])) # Номер игрока
            m = []
            while s[pos]!=self.__incodetable[2][1]:
                m.append(s[pos]) # Символ сообщения
                pos += 1
            mov[i].append(m) # Код хода
            pos += 1  # --Следующий ход--
        pos += 1 # --Далее--
            
        i = 0
        mes = [] # Новый чат
        while s[pos]!=self.__incodetable[2][0]:
            mes.append([])
            mes[i].append(self.__ctd(s[pos:pos+2])) # Номер игрока
            m = []
            while s[pos]!=self.__incodetable[2][1]:
                m.append(s[pos]) # Символ сообщения
                pos += 1
            mes[i].append(m) # Код хода
            pos += 1  # --Следующий ход--
        pos += 1 # --Далее--
        m1 = []
        while s[pos]!=self.__incodetable[2][0]:
            m1.append(s[pos]) # Символ имени 1
            pos += 1
        pos += 1 # --Далее--
        m2 = []
        while s[pos]!=self.__incodetable[3][0]:
            m2.append(s[pos]) # Символ имени 2
            pos += 1
        pos += 1 # --Далее--
        names = (m1,m2)
            
        return (mov,mes,names)
    
        
    def __decodeInt(self, s):
        pos = 0
        l = len(s)
        if s[-1]!=self.__incodetable[3][0]:
            return "error with message, __decodeObj"
        
        prev = [] # Превью фигуры
        i = 0
        while s[pos]!=self.__incodetable[3][0]:
            prev.append({}) # Добавляем словарь под игрока
            while s[pos]!=self.__incodetable[2][1]:
                h = str(self.__ctd(s[pos:pos+2])) # Добавляем словарь под h
                pos += 2
                prev[i][h] = {}
                while s[pos]!=self.__incodetable[2][2]:
                    w = str(self.__ctd(s[pos:pos+2])) # Получаем w
                    pos += 2
                    prev[i][h][w] = self.__ctd(s[pos:pos+2]) # Пишем тип демо-фигуры
                    pos += 2
                    pos += 1 # --Следующая w--
                pos += 1 # --Следующая h--
            pos += 1  # --Следующий игрок--
            i += 1
        
        return prev
    
        
    def __decodeObj(self, s):
        pos = 0
        l = len(s)
        if s[-1]!=self.__incodetable[3][0] or l<12:
            return "error with message, __decodeObj"
        #print ("")
        #print ("")
        #print ("")
        #print (s)
        #print ("")
        #print ("")
        #print ("")
        deState = int(self.__ctd(s[pos:pos+2])) # Состояние сервера, номер
        pos += 2
        deLevel = int(self.__ctd(s[pos:pos+2])) # Уровень
        pos += 2
        deDesk = (int(self.__ctd(s[pos:pos+2])),int(self.__ctd(s[pos+2:pos+4]))) # Доска, размеры
        pos += 4
        pos += 1 # ---Далее---
        
        deCurrMove = int(self.__ctd(s[pos:pos+2])) # Текущий ход
        pos += 2
        deAllMoves = [] # Очерёдность ходов
        while s[pos]!=self.__incodetable[2][0]:
            deAllMoves.append(int(self.__ctd(s[pos:pos+2])))
            pos +=2
        pos += 1 # ---Далее---

        dePieces = [] # Фигуры
        while s[pos]!=self.__incodetable[2][0]:
            dePieces.append([int(self.__ctd(s[pos:pos+2])), # ID фигуры
                             int(self.__ctd(s[pos+2:pos+4])), # Номер типа фигуры
                             int(self.__ctd(s[pos+4:pos+6])), # Изначальный номер типа фигуры
                             int(self.__ctd(s[pos+6:pos+8])), # Индекс-точка на доске
                             int(self.__ctd(s[pos+8:pos+10])), # Номер владельца
                             bool(self.__ctd(s[pos+10:pos+12])), # Способность
                             int(self.__ctd(s[pos+12:pos+14])), # Номер последнего хода
                             bool(self.__ctd(s[pos+14:pos+16])), # Направление движения
                             bool(self.__ctd(s[pos+16:pos+18])), # Жив ли
                             ])
            pos += 18
            pos += 1 # ---Следующая фигура---
        pos += 1 # ---Далее---
        
        i = 0
        #print("s[pos] = "+str(s[pos])+", pos0 = "+str(pos))
        dePlayers = [] # Игроки
        while s[pos]!=self.__incodetable[3][0]:
            dePlayers.append([int(self.__ctd(s[pos:pos+2])), # Номер-ID игрока
                              int(self.__ctd(s[pos+2:pos+4])), # Контроллер №
                              int(self.__ctd(s[pos+4:pos+6])), # Номер цвета
                              bool(self.__ctd(s[pos+6:pos+8])), # Направление движения
                              []]) # Команда
            pos += 8
            while s[pos]!=self.__incodetable[2][2]:
                dePlayers[i][4].append(int(self.__ctd(s[pos:pos+2]))) # Номера игроков команды
                pos += 2
            pos += 1 # Конец атрибута команда
            if s[pos]!= self.__incodetable[2][2]:
                dePlayers[i].append([int(self.__ctd(s[pos:pos+2])),[]]) # Взятие на проходе, № Фигуры
                pos += 2
                while s[pos]!=self.__incodetable[2][2]:
                    dePlayers[i][5][1].append(int(self.__ctd(s[pos:pos+2]))) # Взятие на проходе, index клетки
                    pos += 2
            else:
                dePlayers[i].append([]) # Взятие на проходе, пустое
            pos += 1 # Конец атрибута на проходе
            dePlayers[i].append([int(self.__ctd(s[pos:pos+2])),int(self.__ctd(s[pos+2:pos+4])),[],[],[],[]]) # Подготовка, золото
            pos += 4
            while s[pos]!=self.__incodetable[2][2]:
                dePlayers[i][6][2].append(int(self.__ctd(s[pos:pos+2]))) # Подготовка, фигуры
                dePlayers[i][6][3].append(int(self.__ctd(s[pos+2:pos+4]))) # Подготовка, апгрейды
                dePlayers[i][6][4].append(int(self.__ctd(s[pos+4:pos+6])))
                dePlayers[i][6][5].append(int(self.__ctd(s[pos+6:pos+8])))
                pos += 8
            pos += 1 # Конец атрибута подготовка
            pos += 1 # --Следующий игрок--
            i += 1
            
        return (deState,deLevel,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers)

    
    def __executeOrder(self, order):
        #print(order)
        cmd = order["command"]
        if cmd=="premove_result":
            return order["result"]
        elif cmd=="set_objects":
            if self.last_set_objects[0] != order["server_objects"]:
                self.last_set_objects[0] = order["server_objects"]
                self.update_board = True
            return True
        elif cmd=="set_interface":
            if self.last_set_interface[0] != order["server_interface"]:
                self.last_set_interface[0] = order["server_interface"]
                self.update_interface = True
            return True
        elif cmd=="add_text":
            (mov,mes,names) = self.__decodeMov(order["new_text"])
            return self.__addTextInt(mov,mes,names)
    
    def infiniteLoop(self):
        
        
        while True:

            self.update_board = False
            self.update_interface = False
            while len(self.clientObject.newCommands) > 0:
                order = self.clientObject.newCommands.pop(0)
                self.__executeOrder(order)

            if self.update_board: # Обновить данные объектов
                (deState,deLevel,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers) = self.__decodeObj(self.last_set_objects[0])
                self.__updateObj(deState,deLevel,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers)
            
            if self.update_interface: # Обновить данные вторичных
                prev = self.__decodeInt(self.last_set_interface[0])
                self.__updateInt(prev)

            if self.update_board or self.update_interface:
                self.__printDeck()
            pygame.time.delay(2)
            
                      


if __name__ == "__main__":
     
    print("game input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)
            
    ongoingGameClient = OngoingGameClient((HOST, PORT),join=False) # Создаем объект клиента
