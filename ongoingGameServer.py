import pygame
from server import Server
from client import Client
import socket
from threading import Thread
import json
from os import path as filePath

import piecesMoves as pMoves
from noChessAi import noChessAiSimple as noChessAi

class OngoingGameServer:

    def __init__(self, addr, max_conn=999, currentLVL=0, savefile="none"):
        
        self.__incodetable = ("0123456789abcdefghijklmnopqrstuvwxyz","%%","[],.()","-")
        
        pygame.init() # Инициализируем pygame
        self.__pause = True # Стоит ли игра на паузе
        self.__state = 0 # Состояние сервера
        self.__player = [] # Массив игроков
        #self.__demoPieces = [{},{}] # Фигуры на стадии подготовки
        self.__demoPieces = [{"0":{"0":5},"1":{"0":0,"1":0}},{}]
        self.__playerReady = [False,False] # Кнопка готов
        self.__playerSurrender = [False,False] # Кнопка сдаться
        self.__textChat = [1]
        self.__battleMoves = [1]

        self.__AI = False
        self.__AIIsAskedForMove = False
        self.__AIMove = ""

        #
        #
        # Создаём стартовые переменные игры
        #
        #

        self.__currentLVL = currentLVL # Текущий уровень игры
        self.__levels = [] # Уровни игры
        
        self.__movequeue = [0,1] # Очередь для ходов
        self.__currentmove = -1 # Текущий ход (индекс объекта self.__movequeue),
        # Где -1 означает ничей ход
        
        # Максимальный размер доски, её строки и столбцы
        self.__desk = [0,0] # Доска
        self.__index = [] # Массивы доски и её связей
        self.__piecetypes = [] # Типы фигур
        self.__pieces = [] # Фигуры

        #self.__lastmoves = ("none","move","capture","ability","promote")
        
        #
        #
        #
        #
        #
        
        self.__createPieceTypes() # 1 - Создаём типы фигур
        self.__createPlayers() # 2 - Создаём игроков
        self.__createLevels() # 3 - Создаём уровни

        #

        if savefile=="none":
            # Создание битвы
            self.__firstBattle()
        else:
            print("file!!!")
        
        self.__server = Server(addr) # Создаём объект-сервер
        
        Thread(target=self.__infiniteGameLoop).start()



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



    ######################################################
    ######################################################

    def __chatMessage(self, pid, mes):
        self.__textChat.append((self.__textChat[0],pid,mes))
        self.__textChat[0] += 1
        if self.__textChat[0]>600:
            self.__textChat[0] -= 1
            self.__textChat.pop(1)

    def __firstBattle(self):
        self.__state = 1 # Состояние сервера - Подготовка
        self.__initLevel(self.__currentLVL)
        return True
        
    def __initEndBattle(self, pid):
        return self.__endBattle(pid<2)
        
    def __endBattle(self, isvictory):
        self.__state = 1 # Состояние сервера - Подготовка
        self.__clearDeck() # Чистим доску
        if isvictory:
            self.__currentLVL += 1
            golddif = self.__levels[self.__currentLVL].gold - self.__levels[self.__currentLVL-1].gold
            for p in self.__player:
                p["gold"][1] = p["gold"][1] + golddif
                p["gold"][0] = p["gold"][1]
                p["upgrades"][0] = p["upgrades"][1].copy()
                p["piecesnum"][0] = p["piecesnum"][1].copy()
        else:
            for p in self.__player:
                p["gold"][1] = p["gold"][0]
                p["upgrades"][1] = p["upgrades"][0].copy()
                p["piecesnum"][1] = p["piecesnum"][0].copy()
        self.__initLevel(self.__currentLVL)
        return True

    def __initLevel(self, num):
        lvl = self.__levels[num]
        self.__createDesk(lvl.desk[0],lvl.desk[1])
        self.__createCreeps(lvl.pieces,lvl.desk[0])
        #self.__printDeck()
        return True
    
    def __createDesk(self,width=8,height=8):
        self.__desk.clear()
        self.__desk.extend((width,height)) # Размер доски
        count = 0
        self.__index.clear() # Клетки доски
        for h in range(self.__desk[1]):
            self.__index.append([])
            for w in range(self.__desk[0]):
                self.__index[h].append(-1)
        pMoves.setBoard(width,height) # Обновляет доску для функций движения фигур
                
    def __clearDeck(self):
        self.__index.clear() # Массивы доски и её связей
        self.__desk.clear() # Доска
        self.__desk.extend((0,0))
        
        self.__pieces.clear() # Фигуры
        return True

    def __createCreeps(self,pieces,width):
        ne = pieces["neutral"]
        e1 = pieces["enemy1"]
        e2 = pieces["enemy2"]
        for p in ne:
            np = self.__createPiece(4,p[0],p[1]+p[2]*width,ability=p[3])
        for p in e1:
            np = self.__createPiece(2,p[0],p[1]+p[2]*width,ability=p[3])
        for p in e2:
            np = self.__createPiece(3,p[0],p[1]+p[2]*width,ability=p[3])
        return True
            
    def __playerPrepBuyPiece(self, pid, piecetype):
        p = self.__player[pid]
        pt = self.__piecetypes[piecetype]
        if p["gold"][1] >= pt["piececost"]:
            p["gold"][1] -= pt["piececost"]
            p["piecesnum"][1][piecetype] += 1
            return True
        return False
  
    def __playerPrepBuyUpgrade(self, pid, piecetype):
        p = self.__player[pid]
        pt = self.__piecetypes[piecetype]
        if not(p["upgrades"][1][piecetype]) and p["gold"][1] >= pt["upgradecost"]:
            p["gold"][1] -= pt["upgradecost"]
            p["upgrades"][1][piecetype] = True
            return True
        return False

    def __isCoordInDemoPieces(self,h,w):
        for dp in self.__demoPieces:
            if str(h) in dp:
                if str(w) in dp[str(h)]:
                    return True
        return False
    
    def __addCoordToDemoPieces(self,h,w,pid,pt):
        dp = self.__demoPieces[pid]
        if str(h) in dp:
            if str(w) in dp[str(h)]:
                return False
            else:
                dp[str(h)][str(w)] = pt
        else:
            dp[str(h)] = {str(w):pt}
        return True
    
    def __playerPrepPlacePiece(self, pid, pt, h, w):
        if pMoves.isPointEmpty(h,w,self.__index):
            if not(self.__isCoordInDemoPieces(h,w)):
                pw1 = self.__levels[self.__currentLVL].player[0]
                pw2 = self.__desk[1]-pw1
                ph = self.__levels[self.__currentLVL].player[1]
                if (h<ph and ((pid==0 and w<pw1) or (pid==1 and w>=pw2))):
                    self.__addCoordToDemoPieces(h,w,pid,pt)
                else:
                    print("Coord is not in player zone, __playerPrepPlacePiece")
                    return False
            else:
                print("Dest is not empty, __playerPrepPlacePiece")
                return False
        else:
            print("Dest is not valuable, __playerPrepPlacePiece")
            return False
        return True
        
    def __playerPrepDropAll(self, pid):
        p = self.__player[pid]
        self.__demoPieces[pid].clear()
        p["gold"][1] = p["gold"][0]
        p["upgrades"][1] = p["upgrades"][0].copy()
        p["piecesnum"][1] = p["piecesnum"][0].copy()
        return True

    def __playerReadyOn(self, pid):
        self.__playerReady[pid] = True
        for r in range(len(self.__playerReady)):
            if not(self.__playerReady[r]) and self.__player[r]["controller"]>=0:
                print("r = "+str(r))
                return False
        self.__startBattle()
        return True
        
    def __playerReadyOff(self, pid):
        self.__playerReady[pid] = False
        return True
        
    def __startBattle(self):
        self.__makeCompanionPieces() # Создаёт демо-фигуры для бота-компаньёна
        
        for i in range(len(self.__demoPieces)): # Создаёт фигуры на основе демо-фигур
            for h in self.__demoPieces[i]:
                for w in self.__demoPieces[i][h]:
                    #print("self.__demoPieces[i][p] = "+str(self.__demoPieces[i][p])+", i = "+str(i)+", p = "+str(p)+", ability = "+str(self.__player[i].upgrades[1][self.__demoPieces[i][p]]))
                    np = self.__createPiece(i,self.__demoPieces[i][h][w],int(h)*self.__desk[0]+int(w),ability=self.__player[i]["upgrades"][1][self.__demoPieces[i][h][w]])
            self.__demoPieces[i].clear()
            
        self.__state = 2 # Состояние сервера - битва
        self.__playerReady[0] = False # Сброс готовности
        self.__playerReady[1] = False
        self.__playerSurrender[0] = False # Сброс кнопки сдаться
        self.__playerSurrender[1] = False
        self.__battleMoves.clear() # Сброс списка ходов
        self.__battleMoves.append(1)
        self.__currentmove = self.__movequeue[0] # Текущий ход игрока
        self.__printDeck()

        #if not(self.__AI):
        #    self.__AI = noChessAi((len(self.__desk[0]),len(self.__desk[1])),
        #                          self.__pieces,
        #                          (self.__currentmove,self.__movequeue)
        #                          )
        #else:
        #    self.__AI.rebuildInit((len(self.__desk[0]),len(self.__desk[1])),
        #                          self.__pieces,
        #                          (self.__currentmove,self.__movequeue)
        #                          )
        print("goool")
        return True

    def __makeCompanionPieces(self):
        boolka = False
        if self.__player[0]["controller"]<0:
            a = 0
            b = 1
            boolka = True
        elif self.__player[1]["controller"]<0:
            a = 1
            b = 0
            boolka = True
        if boolka:
            self.__player[a]["gold"][1] = self.__player[b]["gold"][1]
            self.__player[a]["upgrades"][1] = self.__player[b]["upgrades"][1].copy()
            self.__player[a]["piecesnum"][1] = self.__player[b]["piecesnum"][1].copy()
            self.__demoPieces[a].clear()
            for h in self.__demoPieces[b]:
                self.__demoPieces[a][h] = {}
                for w in self.__demoPieces[b][h]:
                    self.__demoPieces[a][h][str(self.__desk[0]-int(w)-1)] = self.__demoPieces[b][h][w]
        return True
            
    def __playerSurrenderOn(self, pid):
        self.__playerSurrender[pid] = True
        for r in self.__playerSurrender:
            if not(r) and self.__player[pid].controller != "AI":
                return False
        return self.__executeSurrender()
        
    def __playerSurrenderOff(self, pid):
        self.__playerSurrender[pid] = False
        return True
        
    def __executeSurrender(self):
        self.__endBattle(False) # Зачанчиваем битву поражением
        self.__playerReady[0] = False # Сброс готовности
        self.__playerReady[1] = False
        self.__playerSurrender[0] = False # Сброс кнопки сдаться
        self.__playerSurrender[1] = False
        return True
    
    ######################################################
    ######################################################
        
    def __TryMove(self, pid, move):
        ### type     int     int      bool      int
        ### move = [moverid, dest, ability, promotion]
        ### or     [moverid, dest, ability]
        if move in pMoves.getPiecesMoves(self.__pieces,self.__index,pid):
            return self.__TryPieceMove(self.__pieces,self.__index,move)
        else:
            print("no such move "+str(move)+", __TryMove")
            return False
        print("wtf, __TryMove")
        return False
        
    def __cti(self, index):
        if type(index)!=int or (index<0) or (index>len(self.__incodetable[0])*len(self.__incodetable[0])-1):
            return self.__incodetable[1]
        return self.__incodetable[0][index//len(self.__incodetable[0])]+self.__incodetable[0][index%len(self.__incodetable[0])]

    def __incodeMov(self, moves, chat):
        allstr = []
        for i in range(len(moves) - moves[0]): # Неотправленные ходы
            m = moves[moves[0]+i]
            allstr.append(self.__cti(m[0])) # Номер игрока
            allstr.append(m[1]) # Код хода
            allstr.append(self.__incodetable[2][1]) # --Следующий ход--
        moves[0] = len(moves)
        allstr.append(self.__incodetable[2][0]) # ---Далее--- 

        for i in range(len(chat) - chat[0]): # Неотправленный чат
            m = chat[chat[0]+1]
            allstr.append(self.__cti(m[0])) # Номер игрока
            allstr.append(m[1]) # Сообщение игрока
            allstr.append(self.__incodetable[2][1]) # --Следующий чат--
        chat[0] = len(chat)
        allstr.append(self.__incodetable[2][0]) # ---Далее--- 
        allstr.append(self.__player[0]["name"]) # Номер игрока
        allstr.append(self.__incodetable[2][0]) # ---Далее--- 
        allstr.append(self.__player[1]["name"]) # Номер игрока
        allstr.append(self.__incodetable[3][0]) # ---Конец сообщения--- 

        return "".join(allstr)

            
    def __incodeInt(self, prev, player):
        allstr = []
        for i in range(len(prev)): # Превью фигуры
            for h in prev[i]:
                #print(h)
                allstr.append(self.__cti( int(h) ))
                for w in prev[i][h]:
                    allstr.append(self.__cti( int(w) ))
                    allstr.append(self.__cti( prev[i][h][w] ))
                    allstr.append(self.__incodetable[2][3]) # --Следующая w--
                allstr.append(self.__incodetable[2][2]) # --Следующая h--
            allstr.append(self.__incodetable[2][1]) # --Следующий игрок--
        allstr.append(self.__incodetable[3][0]) # ---Конец сообщения---  
                
        return "".join(allstr)
            
        
    def __incodeObj(self, desk, piece, player, movequere, currentmove):
        allstr = []                             
        allstr.append(self.__cti(self.__state)) # Состояние сервера                           
        allstr.append(self.__cti(self.__currentLVL)) # Уровень
        allstr.append(self.__cti(desk[0])) # Параметры доски
        allstr.append(self.__cti(desk[1]))
        allstr.append(self.__incodetable[2][0]) # ---Далее---
                      
        allstr.append(self.__cti(currentmove)) # Текущий ход
        for s in movequere: # Все ходы
            allstr.append(self.__cti(s))
        allstr.append(self.__incodetable[2][0]) # ---Далее---
        
        for s in piece: # Фигуры доски
            allstr.append(self.__cti(s["id"])) # ID фигуры
            allstr.append(self.__cti(s["ptid"])) # Тип фигуры
            allstr.append(self.__cti(s["oldptid"])) # Изначальный тип фигуры
            allstr.append(self.__cti(s["index"])) # Индекс клетки
            allstr.append(self.__cti(s["ownerid"])) # Номер владельца
            allstr.append(self.__cti(int(s["ability"]))) # Способность
            allstr.append(self.__cti(s["lastmove"])) # Ласт ход
            allstr.append(self.__cti(int(s["pawndirection"]))) # Направление фигуры
            allstr.append(self.__cti(int(s["alive"]))) # Жив ли
            allstr.append(self.__incodetable[2][1]) # --Следующая фигура--
        allstr.append(self.__incodetable[2][0]) # ---Далее---
        
        for s in player: # Параметры игроков
            allstr.append(self.__cti(s["id"])) # ID игрока
            allstr.append(self.__cti(s["controller"])) # Контроллер
            allstr.append(self.__cti(s["color"])) # Цвет
            allstr.append(self.__cti(s["pawndirection"])) # Направление пешек
            for t in s["team"]: # Команда
                allstr.append(self.__cti(int(t)))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута команда
            if len(s["onpassan"])>0: # Взятие на проходе
                allstr.append(self.__cti(self.pieces.index(s["onpassan"][0])))
                for t in s["onpassan"][1]:
                    allstr.append(self.__cti(t))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута на проходе
            allstr.append(self.__cti(s["gold"][1])) # Золото
            allstr.append(self.__cti(s["gold"][0]))
            for t in range(len(s["piecesnum"][1])): # Войска
                allstr.append(self.__cti(s["piecesnum"][1][t]))# Войска и
                allstr.append(self.__cti(s["upgrades"][1][t]))# Апгрейды
                allstr.append(self.__cti(s["piecesnum"][0][t]))
                allstr.append(self.__cti(s["upgrades"][0][t]))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута армия-золото
            allstr.append(self.__incodetable[2][1]) # --Следующий игрок--
        allstr.append(self.__incodetable[3][0]) # --Конец сообщения--

        return "".join(allstr)
            
    
    def __addObjectsToServerClass(self):
        self.__server.objects[0] = self.__incodeObj(self.__desk,
                                                    self.__pieces,
                                                    self.__player,
                                                    self.__movequeue,
                                                    self.__currentmove)
        self.__server.objects[1] = self.__incodeInt(self.__demoPieces,
                                                    self.__player)
        if len(self.__battleMoves)+len(self.__textChat)-self.__battleMoves[0]-self.__textChat[0]>0:
            print(" add moves ")
            self.__server.objects[2].append(self.__incodeMov(self.__battleMoves,
                                                             self.__textChat))

    def __TryAddIdToPlayers(self, pid):
        for i in self.__player:
            if i["controller"]<0:
                i["controller"]=pid
                return True
        return False
        
    def __AddMove(self, move, pid):
        for i in self.__player:
            if i["controller"] == pid:
                self.__addPremove(move,i)
                return True
        return False
        
    def __executeOrder(self, order):
        cmd = order["command"]
        if cmd=="newcomer":
            return self.__TryAddIdToPlayers(order["id"])
        elif cmd=="move":
            if self.__AddMove(order["move"],order["id"]):
                #self.__currentmove = (self.__currentmove+1)%len(self.__movequeue)
                return True
            else:
                return False
        elif cmd=="ready_on":
            if order["id"]<len(self.__playerReady):
                return self.__playerReadyOn(order["id"])
            else:
                print("ID greater then len, __executeOrder")
                return False
        return False
    
    def __callForAiMove(self):
        #self.__AI.getMove()
        #return pMoves()
        return True
        
    def __infiniteGameLoop(self):
        
        while True:

            
            while len(self.__server.newCommands) > 0:
                order = self.__server.newCommands.pop(0)
                self.__executeOrder(order)
                #print ("order "+str(order)+" "+str(self.__executeOrder(order)))

            pid = self.__movequeue[self.__currentmove]
            if self.__player[pid]["controller"]<0:
                #if not(self.__AIIsAskedForMove):
                #self.__AIMove
                AImove = self.__callForAiMove()
            
            elif len(self.__player[pid]["premoves"])>0:
                if self.__TryMove(pid,self.__player[pid]["premoves"][0]):
                    removeFirstPremove(pid)
                    self.__currentmove = (self.__currentmove+1)%len(self.__movequeue)
                    self.server.sendToClient({"request": "premove_result", "response": True})
                else:
                    clearPremoves(pid)
                    self.server.sendToClient({"request": "premove_result", "response": False})

            self.__addObjectsToServerClass()
            pygame.time.delay(2)

        



if __name__ == "__main__":
     
    print("game input host adress (it uses localhost if left empty)")
    #HOST = input()# Адрес сервера
    HOST = "localhost" #if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    #PORT = input()# Порт сервера
    PORT = 8080 #if PORT=="" else int(PORT)
            
    ongoingGameServer = OngoingGameServer((HOST, PORT)) # Создаем объект клиента
