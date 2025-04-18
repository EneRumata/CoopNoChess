import pygame
from ongoingGameServer import OngoingGameServer
#from ongoingGameWindow import OngoingGameWindow
from client import Client
import socket
from threading import Thread
import json
from os import path as filePath

class OngoingGameClient:

    def __init__(self, addr, join=False):
 
        self.__incodetable = ("0123456789abcdefghijklmnopqrstuvwxyz","%%","[],.()","-")

        pygame.init() # Инициализируем pygame
        self.__pause = True # Стоит ли игра на паузе
        self.__states = ("waiting_for_players","preparation","battle")
        self.__lastmoves = ("none","move","capture","ability","promote")
        self.__state = 0 # Состояние клиента (и сервера)
        self.__player = [] # Массив игроков
        self.__demoPieces = [{},{}] # Фигуры на стадии подготовки
        self.__playerReady = [False,False] # Кнопка готов
        self.__playerSurrender = [False,False] # Кнопка сдаться
        self.__textChat = [] # История текстового чата
        self.__battleMoves = [] # Ходы в этой битве
        #self.colors = [] # Цвета

        self.__currentLVL = 0 # Текущий уровень игры
        self.__levels = [] # Уровни игры
        
        self.__movequeue = [0,1] # Очередь для ходов
        self.__currentmove = 0 # Текущий ход (индекс объекта self.__movequeue),
        # Где -1 означает ничей ход

        self.last_set_objects = ["none",0,0,0,0,0,0,0] # Последний набор объектов от сервера
        self.update_board = False
        self.last_set_interface = ["none",0,0,0,0] # Последний набор вторичных от сервера
        self.update_interface = False
        self.battleMoves = [] # Все ходы последнего матча
        self.textChat = [] # Все сообщения чата

        # Максимальный размер доски, её строки и столбцы
        self.__initialdesk = (("a","b","c","d","e","f","g","h","i","j","k","l","m","n"),("1","2","3","4","5","6","7","8","9","10","11","12","13","14"))
        self.__desk = [[],[]] # Доска
        self.__indexToCoordAndPieces = [] # Массивы доски и её связей
        self.__coordToIndex = {}

        self.__ptids = 0
        self.__piecetypes = [] # Типы фигур
        self.__pieces = [] # Фигуры

        self.__lastmoves = ("none","move","capture","ability")
        
        #
        #
        #
        #
        #
        
        self.__createPieceTypes() # 1 - Создаём типы фигур
        self.__createPlayers() # 2 - Создаём игроков
        self.__createLevels() # 3 - Создаём уровни

        #
        #
        #
        #
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
        s = [""]
        n = 0
        r = 0
        for i in range(len(self.__indexToCoordAndPieces)):
            if self.__isDestEmptyClient(i):
                s[r] += "  -  "
            else:
                s[r] += " " + str(self.__piecetypes[self.__indexToCoordAndPieces[i][1][0].ptid].type[0:2])+str(self.__indexToCoordAndPieces[i][1][0].ownerid) + " "
            n += 1
            if n>=len(self.__desk[0]):
                n = 0
                r += 1
                s.append("")
        print("")
        for i in range(len(self.__desk[0])-1,-1,-1):
            print("i="+str(i)+"   "+s[i])
        print("")
        
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
        self.__desk.append(self.__initialdesk[0][:width])
        self.__desk.append(self.__initialdesk[1][:height])
        count = 0
        self.__indexToCoordAndPieces.clear() # Массивы доски и её связей
        self.__coordToIndex.clear()
        for i in self.__desk[1]:
            for n in self.__desk[0]:
                self.__indexToCoordAndPieces.append([(n,i),[]])
                self.__coordToIndex[n+i] = [count]
                count +=1
        return True
                
    def __clearDeck(self):
        self.__indexToCoordAndPieces.clear() # Массивы доски и её связей
        self.__coordToIndex.clear()
        self.__desk.clear() # Доска
        self.__desk.extend([[],[]])
        
        for p in self.__pieces:
            p.delete()
        self.__pieces.clear()
        return True
        
    def __removePrePieces(self):
        return True

    def __endCampain(self):
        return True
        self.__pause = True
        
    ##################################################################
    ##################################################################

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
    ##### Игрок
    # Создает игроков
    def __createPlayers(self):
        self.__createPlayer(0,"AI",1,[0,4], True)
        self.__createPlayer(1,"AI",1,[1,4],False)
        self.__createPlayer(2,"AI",1,[2,3,4],False)
        self.__createPlayer(3,"AI",1,[2,3,4],False)
        self.__createPlayer(4,"AI",1,[4],False)
        #print("added")
        
    # Создает игрока
    def __createPlayer(self, pid, controller, color, team, pawndirection=False):
        pl = self.__noChessPlayer(pid, controller, color, team, pawndirection)
        self.__player.append(pl)
        #print("add"+str(pid))
        for i in range(2):
            for p in self.__piecetypes:
                pl.upgrades[i].append(0)
                if p == "king":
                    pl.piecesnum[i].append(1)
                else:
                    pl.piecesnum[i].append(0)
        #print("pl.upgrades = "+str(pl.upgrades)+", pl.piecesnum = "+str(pl.piecesnum))
        return pl

    def __owningPlayer(self,piece):
        return self.__player[piece.ownerid]
    
    def __changePlayerController(self, player, controller): # Меняет игрока
        player.controller = controller
        return True
        
    def __changePlayerColor(self, player, color): # Меняет игрока
        return player.changeColor(color)
        
    class __noChessPlayer: # Класс игрока
        def __init__(self, pid, controller, color, team, pawndirection=False):
            self.id = pid
            self.name = "Игрок "+str(pid)
            self.controller = controller
            self.color = color
            self.pawndirection = pawndirection
            self.team = team
            self.onpassan = []
            self.premoves = []
            self.gold = [500,500] # 0 - перед раундом, 1 - в начале
            self.upgrades = [[],[]] # 0 - перед раундом, 1 - в начале
            self.piecesnum = [[],[]] # 0 - перед раундом, 1 - в начале
            
        def addOnpassan(self,piece,squeres):
            self.onpassan.append(piece)
            self.onpassan.append(squeres)
            
        def clearOnpassan(self):
            self.onpassan.clear()
            
        def addPremove(self,move):
            self.premoves.append(move)
            
        def removeFirstPremove(self):
            if len(self.premoves)>0:
                self.premoves.pop(0)
            
        def clearPremoves(self):
            self.onpassan.clear()
            
        def changeColor(self, color):
            self.color = color
            return True

        def kill(self): # Вызов деструктора
            self.__del__()
            
        def __del__(self):
            print("player deleted")

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
        path = "json//pieces.json"
        if filePath.exists(path):
            with open(path,'r') as file:
                pieces = json.load(file)["pieces"]
                #print(pieces)
        else:
            print("Path ''json//pieces.json'' not found, __createPieceTypes")
            return False
        for p in pieces:
            self.__createPieceType(pieces[p]["gamename"],pieces[p]["normalname"],pieces[p]["piececost"],pieces[p]["upgradecost"],pieces[p]["functionname"],pieces[p]["ispurchasable"])
        return True
        
    def __createPieceType(self,ptgamename,ptdisplayname,ptpiececost,ptupgradecost,function,ispurchasable):
        if self.__ptids<100:
            if len(ptgamename)<=20:
                if len(ptdisplayname)<=20:
                    pt = self.__noPieceType(self.__ptids,ptgamename,ptdisplayname,ptpiececost,ptupgradecost,function,ispurchasable)
                    self.__ptids += 1
                    self.__piecetypes.append(pt)
                    #print("type is "+str(pt.type))
                    return pt
                else:
                    print("Too long ptdisplayname, __createPieceType")
                    return False
            else:
                print("Too long ptgamename, __createPieceType")
                return False
        else:
            print("Too much ptids, __createPieceType")
            return False
        print("wtf, __createPieceType")
        return False
            
    class __noPieceType: # Класс типа фигуры
        def __init__(self, ptid, ptgamename, ptdisplayname, ptpiececost, ptupgradecost, movefunction, ispurchasable):
            self.id = ptid
            self.type = ptgamename
            self.name = ptdisplayname
            self.cost = ptpiececost
            self.upgrade = ptupgradecost
            self.function = movefunction
            self.purchasable = ispurchasable

    #####
    ####
    ###
    ##
    #



    #
    ##
    ###
    ####
    ##### Клиентская фигура

    def __createClientPiece(self, pid, ptid, otid, index, ownerid, ability, lastmove, pawndirection, alive):
        piece = self.__noClientPiece(pid, alive, ptid, otid, ownerid, index, ability, lastmove, pawndirection)
        # Создаём фигуру
        self.__pieces.append(piece) # Добавляем фигуру в список фигур
        self.__indexToCoordAndPieces[index][1].clear()
        self.__indexToCoordAndPieces[index][1].append(piece) # Добавляем фигуру на доску
        return piece
    
    class __noClientPiece: # Класс клиентской фигуры
        def __init__(self, pid, alive, ptid, otid, ownerid, index, ability, lastmove, pawndirection):
            self.id = pid
            self.alive = True
            self.ptid = ptid # ID типа фигуры
            self.oldptid = otid # Изначальный ID типа фигуры
            self.ownerid = ownerid # Индекс владельца, к примеру 1
            self.index = index # Индекс точки, к примеру 63
            self.ability = ability # Наличие уникального хода, к примеру рокировка
            self.lastmove = lastmove # Последнее действие, используется другими фигурами
            self.pawndirection = pawndirection # Направление движения (только для фигур-пешек)
            # Где True означает наверх, а False - вниз

        def delete(self):
            self.__del__()
            
        def __del__(self):
            print("piece deleted")

    
    #####
    ####
    ###
    ##
    #
    


            
    #
    #
    #
    # Функции для работы с координатами доски
    def __isPieceAllyClient(self, piece1, piece2): # Союзная ли фигура
        return  piece2.ownerid in self.__owningPlayer(piece1).team
        
    def __isCoordValuableClient(self, coord):
        return (coord in self.__coordToIndex)
    
    def __isIndexValuableClient(self, index):
        return (index>=0 and index<len(self.__indexToCoordAndPieces))
    
    def __coordToIndexClient(self, coord):
        return self.__coordToIndex[coord]
    
    def __indexToCoordClient(self, index):
        return self.__indexToCoordAndPieces[index][0]
    
    def __coordToPieceClient(self, coord):
        return self.__coordToIndexAndPieces[coord][1]
    
    def __indexToPieceClient(self, index):
        return self.__indexToCoordAndPieces[index][1]

    def __isDestEmptyClient(self, dest):
        if (type(dest)==str or type(dest)==int):
            if type(dest)==str:
                if self.__isCoordValuable(dest):
                    index = self.__coordToIndexClient(dest)
                else:
                    print("an error with coord dest of the square, isDestEmptyClient")
                    return -1
            else:#type(dest)==int:
                if self.__isIndexValuableClient(dest):
                    index = dest
                else:
                    print("an error with index dest of the square, isDestEmptyClient")
                    return -1
            return len(self.__indexToCoordAndPieces[index][1])==0
        else:
            print("an error with dest of the square, isDestEmptyClient, type is "+str(type(dest)))
            return -1










    def __addTextInt(self, mov, mes, names):
        for s in mov:
            self.battleMoves.append(mov)
        for s in mes:
            self.textChat.append(mes)
        self.__player[0].name = names[0]
        self.__player[1].name = names[1]
        return True
    
    def __updateInt(self,prev):
        for i in range(len(prev)):
            self.__demoPieces[i].clear() # Удаляем пре-фигуры
            for coord in prev[i]:
                self.__demoPieces[i][coord] = prev[i][coord] # Добавляем пре-фигуры
        return True

    def __updatePlayers(self, dePlayers):
        #
        # 0   1    2    3     4               5                     6
        #                               0      1         0       1          2          3           4
        # id cont color pd   team         onpassan      gold   pieces1   upgrades1   pieces2   upgrades2
        # int int int  bool [int,...] [int, [int,...]]  [int, [int,...], [int,...], [int,...], [int,...]]
        #                                    []     
        for i in range(len(dePlayers)):
            p = self.__player[i]
            d = dePlayers[i]
            ###
            p.id = d[0]
            p.controller = d[1]
            p.color = d[2]
            p.pawndirection = d[3]
            p.team = d[4].copy()
            p.onpassan = d[5].copy()
            p.gold = d[6][0]
            p.piecesnum[1] = d[6][1].copy()
            p.upgrades[1] = d[6][2].copy()
            p.piecesnum[0] = d[6][3].copy()
            p.upgrades[0] = d[6][4].copy()
        return True

    def __updatePieces(self, dePieces):
        if len(dePieces)<len(self.__pieces): # Если фигур меньше, чем надо,
            for p in self.__pieces: # пересоздадим их полностью
                p.delete()
            self.__pieces.clear()
        ###
        for i in self.__indexToCoordAndPieces: # Чистим доску
            i[1].clear()
        ###
        for i in range(len(dePieces)):
            if i<len(self.__pieces):
                self.__pieces[i].id = dePieces[i][0]
                self.__pieces[i].ptid = dePieces[i][1] # ID типа фигуры
                self.__pieces[i].oldptid = dePieces[i][2] # Изначальный ID типа фигуры
                self.__pieces[i].index = dePieces[i][3] # Индекс точки, к примеру 63
                self.__pieces[i].ownerid = dePieces[i][4] # Индекс владельца, к примеру 1
                self.__pieces[i].ability = dePieces[i][5] # Наличие уникального хода, к примеру рокировка
                self.__pieces[i].lastmove = dePieces[i][6] # Последнее действие, используется другими фигурами
                self.__pieces[i].pawndirection = dePieces[i][7] # Направление движения (только для фигур-пешек)
                self.__pieces[i].alive = dePieces[i][8] # Жив ли
                self.__indexToCoordAndPieces[dePieces[i][3]][1].append(self.__pieces[i]) # Добавляем фигуру на доску
            else:
                self.__createClientPiece(dePieces[i][0],
                                         dePieces[i][1],
                                         dePieces[i][2],
                                         dePieces[i][3],
                                         dePieces[i][4],
                                         dePieces[i][5],
                                         dePieces[i][6],
                                         dePieces[i][7],
                                         dePieces[i][8])
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
        while s[pos]!=self.__incodetable[2][0]:
            prev.append({})
            while s[pos]!=self.__incodetable[2][1]:
                #print("a = "+str(self.__desk[0][self.__ctd(s[pos:pos+2])]+self.__desk[1][self.__ctd(s[pos+2:pos+4])]))
                #print("b = "+str(self.__ctd(s[pos+4:pos+6])))
                prev[i][self.__desk[0][self.__ctd(s[pos:pos+2])]+self.__desk[1][self.__ctd(s[pos+2:pos+4])]] = self.__ctd(s[pos+4:pos+6])
                pos += 6
                pos += 1 # --Следующая префигура--
            pos += 1  # --Следующий игрок--
            i += 1
        pos += 1 # --Далее--

        prepieces = []
        preupgrades = [] # Войска и апгрейды игроков
        i = 0
        while s[pos]!=self.__incodetable[3][0]:
            prepieces.append([])
            preupgrades.append([])
            while s[pos]!=self.__incodetable[2][1]:
                prepieces[i].append(self.__ctd(s[pos:pos+2]))
                pos += 2 
                preupgrades[i].append(self.__ctd(s[pos:pos+2]))
                pos += 2 
                pos += 1 # --Следующие фигура и апгрейд--
            pos += 1  # --Следующий игрок--
            i += 1
        
        return (prev,prepieces,preupgrades)
    
        
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
            dePlayers[i].append([int(self.__ctd(s[pos:pos+2])),[],[],[],[]]) # Подготовка, золото
            pos += 2
            while s[pos]!=self.__incodetable[2][2]:
                dePlayers[i][6][1].append(int(self.__ctd(s[pos:pos+2]))) # Подготовка, фигуры
                dePlayers[i][6][2].append(int(self.__ctd(s[pos+2:pos+4]))) # Подготовка, апгрейды
                dePlayers[i][6][3].append(int(self.__ctd(s[pos+4:pos+6])))
                dePlayers[i][6][4].append(int(self.__ctd(s[pos+6:pos+8])))
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
                (prev,prepieces,preupgrades) = self.__decodeInt(self.last_set_interface[0])
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
