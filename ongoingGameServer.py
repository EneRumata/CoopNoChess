import pygame
from server import Server
from client import Client
import socket
from threading import Thread
import json
from os import path as filePath

class OngoingGameServer:

    def __init__(self, addr, max_conn=999, currentLVL=0, savefile="none"):
        
        self.__incodetable = ("0123456789abcdefghijklmnopqrstuvwxyz","%%","[],.()","-")
        
        pygame.init() # Инициализируем pygame
        self.__pause = True # Стоит ли игра на паузе
        self.__states = ("waiting_for_players","battle","preparation")
        self.__state = 0 # Состояние сервера
        self.__player = [] # Массив игроков
        #self.__demoPieces = [] # Фигуры на стадии подготовки
        self.__demoPieces = [{"a1":5,"a2":0,"b2":0},{}]
        self.__playerReady = [False,False] # Кнопка готов
        self.__playerSurrender = [False,False] # Кнопка сдаться
        self.__textChat = [1]
        self.__battleMoves = [1]

        #
        #
        # Создаём стартовые переменные игры
        #
        #

        self.__currentLVL = currentLVL # Текущий уровень игры
        self.__levels = [] # Уровни игры
        
        self.__movequeue = [0,1] # Очередь для ходов
        self.__currentmove = 0 # Текущий ход (индекс объекта self.__movequeue),
        # Где -1 означает ничей ход
        self.__idcolor = ["grey","red","green","purple","brown","blue"]
        self.__idcolorname = ["Серый","Красный","Зелёный","Бирюзовый","Коричневый","Голубой"]

        # Максимальный размер доски, её строки и столбцы
        self.__initialdesk = (("a","b","c","d","e","f","g","h","i","j","k","l","m","n"),("1","2","3","4","5","6","7","8","9","10","11","12","13","14"))
        self.__desk = [[],[]] # Доска
        self.__indexToCoordAndPieces = [] # Массивы доски и её связей
        self.__coordToIndexAndPieces = {}
        self.__ptids = 0
        self.__piecetypes = [] # Типы фигур
        self.__pids = 0
        self.__pieces = [] # Фигуры

        self.__lastmoves = ("none","move","capture","ability")
        
        #
        #
        #
        #
        #

        # Делаем новый поток с циклом, в которoм берем данные об игроках

        
        self.__createPieceTypes() # 1 - Создаём типы фигур
        self.__createPlayers() # 2 - Создаём игроков
        self.__createLevels() # 3 - Создаём уровни

        if savefile=="none":
            self.__firstBattle(self.__currentLVL)
        else:
            print("file!!!")
        
        self.__server = Server(addr) # Создаём объект-сервер
        
        Thread(target=self.__infiniteGameLoop).start()




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
    


    def __testmoves(self):
        Ra1 = self.__pieces[0]
        Kb1 = self.__pieces[1]
        Bc1 = self.__pieces[2]
        Qd1 = self.__pieces[3]
        Le1 = self.__pieces[4]
        lBf1 = self.__pieces[5]
        Kg1 = self.__pieces[6]
        Rh1 = self.__pieces[7]
        
        Pa2 = self.__pieces[8]
        Pb2 = self.__pieces[9]
        Pc2 = self.__pieces[10]
        Pd2 = self.__pieces[11]
        Pe2 = self.__pieces[12]
        lPf2 = self.__pieces[13]
        lPg2 = self.__pieces[14]
        lPh2 = self.__pieces[15]

        Ra8 = self.__pieces[16]
        Kb8 = self.__pieces[17]
        Bc8 = self.__pieces[18]
        Qd8 = self.__pieces[19]
        Le8 = self.__pieces[20]
        lBf8 = self.__pieces[21]
        Kg8 = self.__pieces[22]
        Rh8 = self.__pieces[23]
        
        
        Pa7 = self.__pieces[24]
        Pb7 = self.__pieces[25]
        Pc7 = self.__pieces[26]
        Pd7 = self.__pieces[27]
        Pe7 = self.__pieces[28]
        lPf7 = self.__pieces[29]
        lPg7 = self.__pieces[30]
        lPh7 = self.__pieces[31]
        
        print("P e4 "+str(self.__TryPieceMove(Pe2,"e4",self.__coordToIndex("e4"))))
        print("P e5 "+str(self.__TryPieceMove(Pe7,"e5",self.__coordToIndex("e5"))))
        print("P d4 "+str(self.__TryPieceMove(Pd2,"d4",self.__coordToIndex("d4"))))
        print("P d5 "+str(self.__TryPieceMove(Pd7,"d5",self.__coordToIndex("d5"))))
        print("P e5 "+str(self.__TryPieceMove(Pd2,"e5",self.__coordToIndex("e5"))))
        print("P e4 "+str(self.__TryPieceMove(Pd7,"e4",self.__coordToIndex("e4"))))

        print("K c3 "+str(self.__TryPieceMove(Kb1,"c3",self.__coordToIndex("c3"))))
        print("K c6 "+str(self.__TryPieceMove(Kb8,"c6",self.__coordToIndex("c6"))))

        print("B e3 "+str(self.__TryPieceMove(Bc1,"e3",self.__coordToIndex("e3"))))
        print("B c6 "+str(self.__TryPieceMove(Bc8,"e6",self.__coordToIndex("e6")))) 

        print("Q e2 "+str(self.__TryPieceMove(Qd1,"e2",self.__coordToIndex("e2"))))
        print("Q c7 "+str(self.__TryPieceMove(Qd8,"e7",self.__coordToIndex("e7")))) 

        print("R a1 "+str(self.__TryPieceMove(Ra1,"e1",self.__coordToIndex("e1"))))
        print("R a8 "+str(self.__TryPieceMove(Ra8,"e8",self.__coordToIndex("e8"))))
        
        print("lP g3 "+str(self.__TryPieceMove(lPg2,"g3",self.__coordToIndex("g3"))))
        print("lP g6 "+str(self.__TryPieceMove(lPg7,"g6",self.__coordToIndex("g6"))))
        print("lP g4 "+str(self.__TryPieceMove(lPg2,"g4",self.__coordToIndex("g4"))))
        print("lP g5 "+str(self.__TryPieceMove(lPg7,"g5",self.__coordToIndex("g5"))))
        print("lP g5 "+str(self.__TryPieceMove(lPg2,"g5",self.__coordToIndex("g5"))))
        
        print("lP h6 "+str(self.__TryPieceMove(lPh7,"h6",self.__coordToIndex("h6"))))
        print("lP h3 "+str(self.__TryPieceMove(lPh2,"h3",self.__coordToIndex("h3"))))
        print("lP h5 "+str(self.__TryPieceMove(lPh7,"h5",self.__coordToIndex("h5"))))
        print("lP h4 "+str(self.__TryPieceMove(lPh2,"h4",self.__coordToIndex("h4"))))
        print("lP h5 "+str(self.__TryPieceMove(lPh7,"h4",self.__coordToIndex("h4"))))
              
        print("lP h5 "+str(self.__TryPieceMove(lPg2,"h5",self.__coordToIndex("h5"))))
        print("lP a5 "+str(self.__TryPieceMove(lPh7,"a5",self.__coordToIndex("a5"))))
        
        print("lP f3 "+str(self.__TryPieceMove(lPf2,"f3",self.__coordToIndex("f3"))))
        print("lP f6 "+str(self.__TryPieceMove(lPf7,"f6",self.__coordToIndex("f6"))))
        print("lP f4 "+str(self.__TryPieceMove(lPf2,"f4",self.__coordToIndex("f4"))))
        print("lP f5 "+str(self.__TryPieceMove(lPf7,"f5",self.__coordToIndex("f5"))))
        print("lP f5 "+str(self.__TryPieceMove(lPf2,"f5",self.__coordToIndex("f5"))))

        print("lB g2 "+str(self.__TryPieceMove(lBf1,"g2",self.__coordToIndex("g2"))))
        print("lB g7 "+str(self.__TryPieceMove(lBf8,"g7",self.__coordToIndex("g7"))))
        print("lB f3 "+str(self.__TryPieceMove(lBf1,"f3",self.__coordToIndex("f3"))))
        print("lB f6 "+str(self.__TryPieceMove(lBf8,"f6",self.__coordToIndex("f6"))))
        print("lB d5 "+str(self.__TryPieceMove(lBf1,"d5",self.__coordToIndex("d5"))))
        print("lB d4 "+str(self.__TryPieceMove(lBf8,"d4",self.__coordToIndex("d4"))))
        print("lB g8 "+str(self.__TryPieceMove(lBf1,"g8",self.__coordToIndex("g8"))))
        print("lB g1 "+str(self.__TryPieceMove(lBf8,"g1",self.__coordToIndex("g1"))))
        
    def __printDeck(self): # Показывает доску в отладке
        return True
        s = [""]
        n = 0
        r = 0
        for i in self.__coordToIndexAndPieces:
            if self.__isDestEmpty(i):
                s[r] += "  -  "
            else:
                s[r] += " " + str(self.__coordToPiece(i)[0].type.type[0:2])+str(self.__coordToPiece(i)[0].ownerid) + " "
            n += 1
            if n>7:
                n = 0
                r += 1
                s.append("")
        print("")
        for i in range(7,-1,-1):
            print("i="+str(i)+"   "+s[i])
        print("")
        
    def __createDefaultPieces(self): # Создаёт набор стандартных фигур для игроков 0 и 1
        for new in (("rock",0,"a1"),
                    ("knight",0,"b1"),
                    ("bishop",0,"c1"),
                    ("queen",0,"d1"),
                    ("king",0,"e1"),
                    ("bee",0,"f1"),
                    ("knight",0,"g1"),
                    ("rock",0,"h1"),
                    
                    ("pawn",0,"a2"),
                    ("pawn",0,"b2"),
                    ("pawn",0,"c2"),
                    ("pawn",0,"d2"),
                    ("pawn",0,"e2"),
                    ("ram",0,"f2"),
                    ("ram",0,"g2"),
                    ("ram",0,"h2"),
                    
                    ("rock",1,"a8"),
                    ("knight",1,"b8"),
                    ("bishop",1,"c8"),
                    ("queen",1,"d8"),
                    ("king",1,"e8"),
                    ("bee",1,"f8"),
                    ("knight",1,"g8"),
                    ("rock",1,"h8"),
                    
                    ("pawn",1,"a7"),
                    ("pawn",1,"b7"),
                    ("pawn",1,"c7"),
                    ("pawn",1,"d7"),
                    ("pawn",1,"e7"),
                    ("ram",1,"f7"),
                    ("ram",1,"g7"),
                    ("ram",1,"h7"),
                    ):
            newpiece = self.__createPiece(new[0],new[1],coord=new[2])

    def currentState(self):
        return self.__state
    
    #
    # Пауза
    def __setPause(self,pause):
        self.__pause = pause
        
    def __pauseGame(self,pause):
        self.__pause = True
        
    def __resumeGame(self,pause):
        self.__pause = False
        
    def __isGamePaused(self):
        return self.__pause
        
    def __isGameUnpaused(self):
        return not(self.__pause)
    #
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
        print("added")
        
    # Создает игрока
    def __createPlayer(self, pid, controller, color, team, pawndirection=False):
        pl = self.__noChessPlayer(pid, controller, color, team, pawndirection)
        self.__player.append(pl)
        print("add"+str(pid))
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

        def kill(self): # Вызов деструктора
            self.__del__()
            
        def __del__(self):
            print("player deleted")

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

    def __firstBattle(self, lvl):
        self.__state = 1 # Состояние сервера - Подготовка
        self.__initLevel(self.__currentLVL)
        #self.__testmoves() # Тестовые ходы
        self.__printDeck() # Выводит доску в консоль
        return True
        
    
    def __initEndBattle(self, pid):
        return self.__endBattle(pid<2)
        
    def __endBattle(self, isvictory):
        self.__clearDeck() # Чистим доску
        if isvictory:
            self.__currentLVL += 1
            golddif = self.__levels[self.__currentLVL].gold - self.__levels[self.__currentLVL-1].gold
            for p in self.__player:
                p.gold[1] = p.gold[1] + golddif
                p.gold[0] = p.gold[1]
                p.upgrades[0] = p.upgrades[1].copy()
                p.piecesnum[0] = p.piecesnum[1].copy()
        else:
            for p in self.__player:
                p.gold[1] = p.gold[0]
                p.upgrades[1] = p.upgrades[0].copy()
                p.piecesnum[1] = p.piecesnum[0].copy()
        self.__state = 1 # Состояние сервера - Подготовка
        self.__initLevel(self.__currentLVL)
        return True

    def __initLevel(self, num):
        lvl = self.__levels[num]
        self.__createDesk(lvl.desk[0],lvl.desk[1])
        self.__createCreeps(lvl.pieces)
        return True

    def __createDesk(self,width=8,height=8):
        self.__desk.clear()
        self.__desk.append(self.__initialdesk[0][:width])
        self.__desk.append(self.__initialdesk[1][:height])
        count = 0
        self.__indexToCoordAndPieces.clear() # Массивы доски и её связей
        self.__coordToIndexAndPieces.clear()
        for i in self.__desk[1]:
            for n in self.__desk[0]:
                self.__indexToCoordAndPieces.append([(n,i),[]])
                self.__coordToIndexAndPieces[n+i] = [count,[]]
                count +=1
        return True
                
    def __clearDeck(self):
        self.__indexToCoordAndPieces.clear() # Массивы доски и её связей
        self.__coordToIndexAndPieces.clear()
        self.__desk.clear() # Доска
        self.__desk.extend([[],[]])
        
        self.__pids = 0 # Фигуры
        for p in self.__pieces:
            p.delete()
        self.__pieces.clear()
        return True
        
    def __createCreeps(self,pieces):
        ne = pieces["neutral"]
        e1 = pieces["enemy1"]
        e2 = pieces["enemy2"]
        for p in ne:
            np = self.__createPiece(p[0],4,coord=p[1],ability=p[2])
        for p in e1:
            np = self.__createPiece(p[0],2,coord=p[1],ability=p[2])
        for p in e2:
            np = self.__createPiece(p[0],3,coord=p[1],ability=p[2])
        return True
            
    def __playerPrepBuyPiece(self, pid, piecetype):
        p = self.__player[pid]
        if p.gold[1] >= piecetype.cost:
            p.gold[1] -= - piecetype.cost
            p.piecesnum[1][piecetype] += 1
        return True

    def __playerPrepPlacePiece(self, pid, piecetype, coord):
        if self.__isCoordValuable(coord):
            if self.__isDestEmpty(coord) and not((coord in self.__demoPieces[0]) or (coord in self.__demoPieces[1]) or (coord in self.__demoPieces[2]) or (coord in self.__demoPieces[3])):
                w = self._desk.index(coord[0])
                h = self._desk.index(coord[1:])
                pw1 = self.__levels[self.__currentLVL].player[0]
                pw2 = len(self.__desk[1])-pw1
                ph = self.__levels[self.__currentLVL].player[1]
                if (h<ph and ((pid==0 and w<pw1) or (pid==0 and w>=pw2))):
                    self.__demoPieces[pid][coord] = piecetype
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
        self.__demoPieces[pid].clear()
        self.__player[pid].gold[1] = p.gold[0]
        self.__player[pid].upgrades[1] = self.__player[pid].upgrades[0].copy()
        self.__player[pid].piecesnum[1] = self.__player[pid].piecesnum[0].copy()
        return True

    def __playerReadyOn(self, pid):
        self.__playerReady[pid] = True
        for r in range(len(self.__playerReady)):
            if not(self.__playerReady[r]) and self.__player[r].controller != "AI":
                print("r = "+str(r))
                return False
        self.__startBattle()
        return True
        
    def __playerReadyOff(self, pid):
        self.__playerReady[pid] = False
        return True
        
    def __startBattle(self):
        self.__makeCompanionPieces() # Создаёт фигуры для бота-компаньёна
        for i in range(len(self.__demoPieces)):
            for p in self.__demoPieces[i]:
                #print("self.__demoPieces[i][p] = "+str(self.__demoPieces[i][p])+", i = "+str(i)+", p = "+str(p)+", ability = "+str(self.__player[i].upgrades[1][self.__demoPieces[i][p]]))
                np = self.__createPiece(self.__demoPieces[i][p],i,coord=p,ability=self.__player[i].upgrades[1][self.__demoPieces[i][p]])
            self.__demoPieces[i].clear()
        self.__state = 2 # Состояние сервера - битва
        self.__playerReady[0] = False
        self.__playerReady[1] = False
        self.__battleMoves.clear()
        self.__battleMoves.append(1)
        self.__printDeck()
        print("goool")
        return True

    def __makeCompanionPieces(self):
        boolka = False
        if self.__player[0].controller == "AI":
            a = 0
            b = 1
            boolka = True
        elif self.__player[1].controller == "AI":
            a = 1
            b = 0
            boolka = True
        if boolka:
            self.__player[a].gold[1] = self.__player[b].gold[1]
            self.__player[a].upgrades[1] = self.__player[b].upgrades[1].copy()
            self.__player[a].piecesnum[1] = self.__player[b].piecesnum[1].copy()
            
            self.__demoPieces[a].clear()
            for coord in self.__demoPieces[0]:
                c = self.__desk[0][len(self.__desk[0])-1-self.__desk[0].index(coord[0])]
                self.__demoPieces[1][c+coord[1:]]=self.__demoPieces[0][coord]
                
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
        for i in len(self.__demoPieces):
            for p in self.__demoPieces[i]:
                np = self.__createPiece(self.__demoPieces[i][p],i,coord=p,ability=self.__player[i].upgrades[self.__demoPieces[i][p]])
            self.__demoPieces[i].clear()
        self.__state = 2 # Состояние сервера - битва
        self.__playerReady[0] = False
        self.__playerReady[1] = False
        return True
    
    ######################################################piece.ownerid
    ######################################################



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
                    print("type is "+str(pt.type))
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
    ##### Фигура
    
    # Создает фигуру
    def __createPiece(self, ptp, ownerid, coord=0, index=-1, ability=True):
        if type(ptp)==str:
            ptid = -1
            for pt in self.__piecetypes:
                if ptp in (pt.type,pt.name):
                    ptid = pt.id
            if ptid<0:
                print("No such piece-type "+str(ptp)+", __createPiece")
                return False
        elif type(ptp)!=int:
            print("Type is not int or str, __createPiece")
            return False
        else:
            ptid = ptp
        
        if (ptid<self.__ptids) and (self.__isCoordValuable(coord) or self.__isIndexValuable(index)) and(ownerid>=0 and ownerid<=4):
            if self.__isCoordValuable(coord) and (self.__isDestEmpty(coord)):
                #print("self.__player[ownerid].pawndirection type is "+str(type(self.__player[ownerid].pawndirection)))
                #print("ptid = "+str(ptid)+", type is "+str(type(ptid)))
                piece = self.__noChessPiece(self.__pids, ptid, self.__piecetypes[ptid], ownerid, coord, self.__coordToIndex(coord), ability, self.__player[ownerid].pawndirection)
                # Создаём фигуру
                self.__pids +=self.__pids
                self.__addPieceToDest(piece, coord) # Добавляем фигуру на доску
                self.__pieces.append(piece) # Добавляем фигуру в список фигур
                #print("cool, index "+str(index)+", coord "+str(coord)+", __createPiece")
                return piece
                
            elif self.__isIndexValuable(index) and (self.__indexToPiece(index)==[]):
                piece = self.__noChessPiece(self.__pids, ptid, self.__piecetypes[ptid], ownerid, self.__indexToCoord(index), index, ability, self.__player[ownerid].pawndirection)
                # Создаём фигуру
                self.__pids +=self.__pids
                self.__addPieceToDest(piece, index) # Добавляем фигуру на доску
                self.__pieces.append(piece) # Добавляем фигуру в список фигур
                #print("cool, index "+str(index)+", coord "+str(coord)+", __createPiece")
                return piece

            else:
                print("an error with placement of a new piece, index "+str(index)+", coord "+str(coord)+", __createPiece")
                return False
                 
        else:
            print("an error with atributes of a new piece, __createPiece")
            return False
        print("wtf, __createPiece")
        return False

    # Удаляет фигуру
    def __removePiece(self, piece, dest):
        if type(piece)==self.__noChessPiece:
            self.__removePieceFromDest(piece, dest)
            piece.kill()
            if p.type == "king":
                for p in self.__pieces:
                    if p.ownerid in self.__player[piece.ownerid].team and p.type == "king":
                        return True
                return self.__initEndBattle(p.ownerid)
            return True
        else:
            print("an error with removing piece, removePiece, type is "+str(type(piece)))
            return False
        
    class __noChessPiece: # Класс фигуры
        def __init__(self, pids, ptid, ptype, ownerid, coord, index, ability=True, pawndirection=False):
            self.id = pids
            pids += 1

            self.alive = True
            self.ptid = ptid # ID типа фигуры
            self.type = ptype # Тип фигуры
            self.oldptid = ptid # Изначальный ID типа фигуры
            self.oldtype = ptype # Изначальный тип фигуры
            self.ownerid = ownerid # Индекс владельца, к примеру 1
            self.coord = coord # Точка на доске, к примеру H8
            self.index = index # Индекс точки, к примеру 63
            self.ability = ability # Наличие уникального хода, к примеру рокировка
            self.lastmove = "none" # Последнее действие, используется другими фигурами
            self.pawndirection = pawndirection # Направление движения (только для фигур-пешек)
            # Где True означает наверх, а False - вниз

        def changeType(self, newtype, newname): # Превращение в другую фигуру
            self.piecetype = newtype
            self.name = newname
            self.ability = False
            self.lastmove = "promote"
            
        def kill(self): # Вызов деструктора
            print("piece kinda died")
            self.alive = False
            
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

    def __isIndexInDeck(self, index):
        return (index>0 and index<(len(self.__desk[0])*len(self.__desk[1])))
        
    def __isPieceAlly(self, piece1, piece2): # Союзная ли фигура
        #print("id"+str(piece2.ownerid)+", self.__owningPlayer(piece1).team "+str(self.__owningPlayer(piece1).team))
        return  piece2.ownerid in self.__owningPlayer(piece1).team
        
    def __isCoordValuable(self, coord):
        return (coord in self.__coordToIndexAndPieces)
    
    def __isIndexValuable(self, index):
        return (index>=0 and index<len(self.__indexToCoordAndPieces))
    
    def __coordToIndex(self, coord):
        return self.__coordToIndexAndPieces[coord][0]
    
    def __indexToCoord(self, index):
        return self.__indexToCoordAndPieces[index][0]
    
    def __coordToPiece(self, coord):
        #print("coord="+str(coord)+",l="+str(len(self.__coordToIndexAndPieces[coord][1])))
        answer = self.__coordToIndexAndPieces[coord][1] #if (len(self.__coordToIndexAndPieces[coord][1])>0) else False
        return answer
    
    def __indexToPiece(self, index):
        #print("index="+str(index)+",l="+str(len(self.__indexToCoordAndPieces[index][1])))
        answer = self.__indexToCoordAndPieces[index][1] #if (len(self.__indexToCoordAndPieces[index][1])>0) else False
        return answer

    def __isDestEmpty(self, dest):
        if (type(dest)==str or type(dest)==int):
            if type(dest)==str:
                if self.__isCoordValuable(dest):
                    coord = dest
                    index = self.__coordToIndex(dest)
                else:
                    print("an error with coord dest of the square, isDestEmpty")
                    return -1
            else:#type(dest)==int:
                if self.__isIndexValuable(dest):
                    coord = self.__indexToCoord(dest)
                    coord = coord[0]+coord[1]
                    index = dest
                else:
                    print("an error with coord dest of the square, isDestEmpty")
                    return -1
            return len(self.__coordToIndexAndPieces[coord][1])==0 and len(self.__indexToCoordAndPieces[index][1])==0
        else:
            print("an error with dest of the square, isDestEmpty, type is "+str(type(dest)))
            return -1

    def __removePieceFromDest(self, piece, dest): # Удаляет фигуру с доски
        if type(dest)==str or type(dest)==int:
            if type(dest)==str:
                if (self.__isCoordValuable(dest) and not(self.__isDestEmpty(dest))):
                    coord = dest
                    index = self.__coordToIndex(dest)
                else:
                    print("an error with coord dest of the square, removePieceFromDest")
                    return -1
            else:#type(dest)==int:
                if (self.__isIndexValuable(dest) and not(self.__isDestEmpty(dest))):
                    coord = self.__indexToCoord(dest)
                    coord = coord[0]+coord[1]
                    index = dest
                else:
                    print("an error with index dest of the square, removePieceFromDest")
                    return -1
            self.__coordToIndexAndPieces[coord][1].remove(piece)
            self.__indexToCoordAndPieces[index][1].remove(piece)
            piece.coord=="none"
            piece.index==-1
            return 0
        else:
            print("an error with dest of the square, removePieceFromDest, type is "+str(type(dest)))
            return -1
        
    def __addPieceToDest(self, piece, dest):
        if type(dest)==str or type(dest)==int:
            if type(dest)==str:
                if (self.__isCoordValuable(dest) and self.__isDestEmpty(dest)):
                    coord = dest
                    index = self.__coordToIndex(dest)
                else:
                    print("an error with coord dest of the square, addPieceToDest")
                    return -1
            else:#type(dest)==int:
                if (self.__isIndexValuable(dest) and not(self.__isDestEmpty(dest))):
                    coord = self.__indexToCoord(dest)
                    coord = coord[0]+coord[1]
                    index = dest
                else:
                    print("an error with index dest of the square, addPieceToDest")
                    return -1
            self.__coordToIndexAndPieces[coord][1].append(piece)
            self.__indexToCoordAndPieces[index][1].append(piece)
            piece.coord==coord
            piece.index==index
            return 0
        else:
            print("an error with dest of the square, addPieceToDest, "+str(type(dest)))
            return -1

    def __movePieceToDest(self, piece, dest, external=False):
        if type(dest)==str or type(dest)==int:
            if type(piece)==self.__noChessPiece:
                if type(dest)==str:
                    if (self.__isCoordValuable(dest)):
                        coord = dest
                        index = self.__coordToIndex(dest)
                    else:
                        print("an error with coord dest of the square, movePieceToDest")
                        return False
                else:#type(dest)==int: not(self.__isDestEmpty(dest)) not(self.__isDestEmpty(dest))
                    if (self.__isIndexValuable(dest)):
                        coord = self.__indexToCoord(dest)
                        coord = coord[0]+coord[1:]
                        index = dest
                    else:
                        print("an error with index dest of the square, movePieceToDest")
                        return False
                if self.__isDestEmpty(dest):
                    piece.lastmove = "move"
                else:
                    if (not(self.__isPieceAlly(piece,self.__coordToPiece(coord)[0]))):
                        piece.lastmove = "capture"
                        self.__removePiece(self.__coordToPiece(coord)[0],dest)
                    else:
                        print("an error with dest of the square (ally), movePieceToDest")
                        return False
                s = str(piece.ownerid) if not(external) else str(self.__coordToPiece(piece.coord).ownerid)
                self.__battleMoves.append((self.__battleMoves[0],s+"-"+str(piece.coord)+"-"+str(coord)))
                self.__battleMoves[0] += 1
                
                self.__coordToPiece(piece.coord).remove(piece)
                self.__indexToPiece(piece.index).remove(piece)

                self.__coordToPiece(coord).append(piece)
                self.__indexToPiece(index).append(piece)
                piece.coord=coord
                piece.index=index
                return True
            else:
                print("an error with piece-object type, movePieceToDest, "+str(type(piece)))
                return False
        else:
            print("an error with dest of the square, movePieceToDest, "+str(type(dest)))
            return -1
        
    def __changePieceType(self, piece, newtype):
        if ((type(piece)==self.__noChessPiece) and (newtype in self.__piecetypes)):
            piece.__changeType(newtype,self.__piecenames[newtype])
            return 0
        else:
            print("an error with newtype or piece-object type, movePieceToDest, "+str(type(piece)))
            return -1
            
        
    #
    #
    #
    #
    def __TryPawnMove(self, piece, coord, index): # Пробует походить pawn в нужную точку
        width = len(self.__desk[0])
        if piece.pawndirection: # True - вверх по доске (это вперёд по координатам),
            # а False - вниз по доске и назад по координатам
            multiplier = 1
        else:
            multiplier = -1
        diff = index - piece.index
        if diff == (multiplier*width)-1:
            if piece.index%width!=0 and not(self.__isDestEmpty(index) or self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move left TryPawnMove")
                return False
        elif diff == (multiplier*width):
            if self.__isDestEmpty(index):
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move middle TryPawnMove")
                return False
        elif diff == (multiplier*width)+1:
            if piece.index%width!=width-1 and not(self.__isDestEmpty(index) or self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move rigth TryPawnMove")
                return False
        elif diff == (multiplier*width)*2:
            if self.__isDestEmpty(index) and self.__isDestEmpty(index-width*multiplier) and piece.ability:
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move ability TryPawnMove")
                return False

        else:
            print("Impossible move TryPawnMove")
            return False
        print("wtf TryPawnMove")
        return False
    
    def __TryRockMove(self, piece, coord, index): # Пробует походить rock в нужную точку
        width = len(self.__desk[0])
        height = len(self.__desk[1])
        diff = index - piece.index
        if coord[0]==piece.coord[0]:
            step = width # Проверка по высоте, индекс меняется на значение ширины
        elif coord[1:]==piece.coord[1:]:
            step = 1 # Проверка по длите, индекс меняется на единицу
        else:
            print("Impossible diagonal move TryRockMove")
            return False
        if diff>0: # Двигаемся вправо или вверх
            multiplier = 1
        else: # Двигаемся влево или вниз
            multiplier = -1
        #print("step="+str(step)+", multiplier="+str(multiplier))
        for i in range(piece.index+multiplier*step, index, step*multiplier):
            if not(self.__isDestEmpty(i)):
                print("Impossible blocked move with index "+str(i)+" step "+str(multiplier*step)+" TryRockMove")
                return False
        if self.__isDestEmpty(index) or not(self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
            self.__movePieceToDest(piece, index)
            piece.ability = False
            return True
        elif self.__indexToPiece(index)[0].type=="king":
            return self.__TryKingMove(self.__indexToPiece(index)[0],piece.coord,piece.index, external=True)
        else:
            print("Impossible move with piece at the end TryRockMove")
            return False
        print("wtf TryRockMove")
        return False
        
    def __TryKnightMove(self, piece, coord, index): # Пробует походить knight в нужную точку
        width = len(self.__desk[0])
        height = len(self.__desk[1])
        may = []
        a = self.__desk[0].index(coord[0])
        b = self.__desk[1].index(coord[1:])
        # Нижняя половина
        if a>=2 and b>=1:
            may.append(index-width*1-2)
        if a>=1 and b>=2:
            may.append(index-width*2-1)
        if a<=width-1 and b>=2:
            may.append(index-width*2+1)
        if a<=width-2 and b>=1:
            may.append(index-width*1+2)
        # Верхняя
        if a>=2 and b<=height-1:
            may.append(index+width*1-2)
        if a>=1 and b<=height-2:
            may.append(index+width*2-1)
        if a<=width-1 and b<=height-2:
            may.append(index+width*2+1)
        if a>=width-2 and b<=height-1:
            may.append(index+width*1+2)
        if self.__isDestEmpty(index) or not(self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
            self.__movePieceToDest(piece, index)
            return True
        else:
            print("Impossible move TryKnightMove")
            return False
        print("wtf TryKnightMove")
        return False
        
        self.__movePieceToDest(piece, index)
        return True
    
    def __TryBishopMove(self, piece, coord, index): # Пробует походить bishop в нужную точку
        width = len(self.__desk[0])
        height = len(self.__desk[1])
        diff = index - piece.index
        a = self.__desk[0].index(piece.coord[0]) - self.__desk[0].index(coord[0])
        b = self.__desk[1].index(piece.coord[1:]) - self.__desk[1].index(coord[1:])
        if diff == width or diff == -width or diff == 1 or diff == -1:
            if self.__isDestEmpty(index) and piece.ability:
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move ability, blocked way TryBishopMove")
                return False
        if a==b:
            step = 9 # /
        elif a==-b:
            step = 7 # \
        else:
            print("Impossible non-diagonal move TryBishopMove")
            return False
        if diff>0:
            multiplier = 1 # Наверх
        else:
            multiplier = -1 # Вниз
            
        for i in range(piece.index+multiplier*step, index, step*multiplier):
            if not(self.__isDestEmpty(i)):
                print("Impossible blocked move with index "+str(i)+" step "+str(multiplier*step)+" TryBishopMove")
                return False
        if self.__isDestEmpty(index) or not(self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
            self.__movePieceToDest(piece, index)
            return True
        else:
            print("Impossible move with piece at the end TryBishopMove")
            return False
        print("wtf TryBishopMove")
        return False
    
    def __TryQueenMove(self, piece, coord, index): # Пробует походить queen в нужную точку
        width = len(self.__desk[0])
        height = len(self.__desk[1])
        diff = index - piece.index
        a = self.__desk[0].index(piece.coord[0]) - self.__desk[0].index(coord[0])
        b = self.__desk[1].index(piece.coord[1:]) - self.__desk[1].index(coord[1:])
        if (diff == width or diff == -width or diff == 1 or diff == -1 or diff == width-1 or diff == width+1 or diff == -width-1 or diff == -width+1) and not(self.__isDestEmpty(index)) and self.__isPieceAlly(piece,self.__indexToPiece(index)[0]):
            if piece.ability:
                place = piece.index
                self.__removePieceFromDest(piece, piece.index)
                self.__movePieceToDest(self.__indexToPiece(index)[0], place)
                self.__addPieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move ability=false, blocked way TryQueenMove")
                return False
        if a==b:
            step = 9 # /
        elif a==-b:
            step = 7 # \
        elif coord[0]==piece.coord[0]:
            step = width # Проверка по высоте, индекс меняется на значение ширины
        elif coord[1:]==piece.coord[1:]:
            step = 1 # Проверка по длите, индекс меняется на единицу
        else:
            print("Impossible move TryQueenMove")
            return False
        if diff>0:
            multiplier = 1 # Наверх
        else:
            multiplier = -1 # Вниз
            
        for i in range(piece.index+multiplier*step, index, step*multiplier):
            if not(self.__isDestEmpty(i)):
                print("Impossible blocked move with index "+str(i)+" step "+str(multiplier*step)+" TryQueenMove")
                return False
        if self.__isDestEmpty(index) or not(self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
            self.__movePieceToDest(piece, index)
            return True
        else:
            print("Impossible move with piece at the end TryQueenMove")
            return False
        print("wtf TryQueenMove")
        return False
    
    def __TryKingMove(self, piece, coord, index, external=False): # Пробует походить king в нужную точку
        width = len(self.__desk[0])
        height = len(self.__desk[1])
        diff = index - piece.index
        a = self.__desk[0].index(piece.coord[0]) - self.__desk[0].index(coord[0])
        b = self.__desk[1].index(piece.coord[1:]) - self.__desk[1].index(coord[1:])
        if (diff == width or diff == -width or diff == 1 or diff == -1 or diff == width-1 or diff == width+1 or diff == -width-1 or diff == -width+1):
            if self.__isDestEmpty(index) or not(self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
                self.__movePieceToDest(piece, index)
                return True
            if piece.ability and self.__indexToPiece(index)[0].ability and self.__indexToPiece(index)[0].piecetype=="rock":
                if self.__isDestEmpty(index+diff):
                    if (b==0 and (coord[0]+a in self.__desk[0])) or (a==0 and (coord[1:]+b in self.__desk[1])):
                        self.__movePieceToDest(piece, index+diff, external=True)
                        piece.ability = False
                        self.__indexToPiece(index)[0].ability = False
                        return True
                    else:
                        print("Rock at the edge TryKingMove")
                        return False
                else:
                    print("Not empty behind the rock TryKingMove")
                    return False
                piece.ability = False
                place = piece.index
                self.__removePieceFromDest(piece, piece.index)
                self.__movePieceToDest(self.__indexToPiece(index)[0], place)
                self.__addPieceToDest(piece, index)
                return True
            else:
                print("Impossible move with piece at the end TryKingMove")
                return False
        if (a==0 or b==0) and piece.ability and not(self.__isDestEmpty(index)) and self.__isPieceAlly(piece,self.__indexToPiece(index)[0]) and self.__indexToPiece(index)[0].ability and self.__indexToPiece(index)[0].piecetype=="rock":
            # Рокировка, ладья по горизонтали/вертикали со способностью
            rock = self.__indexToPiece(index)[0]
            if a==0:
                step=width
            else:#b==0:
                step=1
            if diff>0:
                multiplier = 1
            else:
                multiplier = -1
            if (self.__indexToCoord(piece.index)[0]==self.__indexToCoord(piece.index+step*multiplier*2)[0]) or (self.__indexToCoord(piece.index)[1]==self.__indexToCoord(piece.index+step*multiplier*2)[1]):
                if self.__isDestEmpty(piece.index+step*multiplier) or piece.__self.__indexToPiece(piece.index+step*multiplier)[0]==rock:
                    if self.__isDestEmpty(piece.index+step*multiplier*2) or piece.__self.__indexToPiece(piece.index+step*multiplier*2)[0]==rock:
                        for i in range(piece.index+step*multiplier*2,index,step*multiplier):
                            if not(self.__isDestEmpty(i)):
                                print("Impossible blocked move with index "+str(i)+" step "+str(multiplier*step)+" TryKingMove")
                                return False
                        self.__movePieceToDest(rock, piece.index+step*multiplier)
                        self.__movePieceToDest(piece,piece.index+step*multiplier*2)
                        rock.ability = False
                        piece.ability = False
                        return True
            print("Cant move to this rock TryKingMove")
            return False
        else:
            print("Impossible move TryKingMove")
            return False
        print("wtf TryKingMove")
        return False
        
    def __TryRamMove(self, piece, coord, index): # Пробует походить lesserPawn в нужную точку
        width = len(self.__desk[0])
        if piece.pawndirection: # True - вверх по доске (это вперёд по координатам),
            # а False - вниз по доске и назад по координатам
            multiplier = 1
        else:
            multiplier = -1
        diff = index - piece.index
        if diff == -1:
            if piece.index%width!=0 and self.__isDestEmpty(index) and piece.ability:
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move left TryLesserPawnMove")
                return False
        elif diff == (multiplier*width):
            if self.__isDestEmpty(index) or not(self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
                self.__movePieceToDest(piece, index)
                return True
            else:
                print("Cannot move middle TryLesserPawnMove")
                return False
        elif diff == 1:
            if piece.index%width!=width-1 and self.__isDestEmpty(index) and piece.ability:
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move rigth TryLesserPawnMove")
                return False

        else:
            print("Impossible move TryLesserPawnMove")
            return False
        return False

    def __TryBeeMove(self, piece, coord, index): # Пробует походить lesserBishop в нужную точку
        width = len(self.__desk[0])
        height = len(self.__desk[1])
        diff = index - piece.index
        a = self.__desk[0].index(piece.coord[0]) - self.__desk[0].index(coord[0])
        b = self.__desk[1].index(piece.coord[1:]) - self.__desk[1].index(coord[1:])
        if (diff == width-1 or diff == width+1 or diff == -width-1 or diff == -width+1):
            if self.__isDestEmpty(index) or not(self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
                self.__movePieceToDest(piece, index)
                return True
            else:
                print("Cannot move piece at dest TryLesserBishopMove")
                return False
        elif (diff == width or diff == -width or diff == 1 or diff == -1):
            if self.__isDestEmpty(index) and piece.ability:
                self.__movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move ability, blocked way TryLesserBishopMove")
                return False
        elif not(self.__isDestEmpty(index) or self.__isPieceAlly(piece,self.__indexToPiece(index)[0])):
            print("Should move behind first enemy TryLesserBishopMove")
            return False
        if a==b:
            step = 9 # /
        elif a==-b:
            step = 7 # \
        else:
            print("Impossible move TryLesserBishopMove")
            return False
        if diff>0:
            multiplier = 1 # Наверх
        else:
            multiplier = -1 # Вниз
        for i in range(piece.index+multiplier*step, index, step*multiplier):
            if not(self.__isDestEmpty(i)):
                if i+step*multiplier==index and not(self.__isPieceAlly(piece,self.__indexToPiece(i)[0])):
                    self.__movePieceToDest(piece, index)
                    return True
                else:
                    print("Impossible blocked move with index "+str(i)+" step "+str(multiplier*step)+" TryLesserBishopMove")
                    return False
        print("wtf TryLesserBishopMove")
        return False
    
    def __TryPieceMove(self, piece, coord, index): # Пробует походить
        if type(piece)==self.__noChessPiece:
            if piece.index!=index:
                if self.__isIndexInDeck(index):
                    if piece.type.type == "pawn":
                        return self.__TryPawnMove(piece, coord, index)
                    elif piece.type.type == "rock":
                        return self.__TryRockMove(piece, coord, index)
                    elif piece.type.type == "knight":
                        return self.__TryKnightMove(piece, coord, index)
                    elif piece.type.type == "bishop":
                        return self.__TryBishopMove(piece, coord, index)
                    elif piece.type.type == "queen":
                        return self.__TryQueenMove(piece, coord, index)
                    elif piece.type.type == "king":
                        return self.__TryKingMove(piece, coord, index)
                    elif piece.type.type == "ram":
                        return self.__TryRamMove(piece, coord, index)
                    elif piece.type.type == "bee":
                        return self.__TryBeeMove(piece, coord, index)
                    else:
                        print("Incorrect piece type, TryPieceMove")
                        return False
                else:
                    print("index off the board, TryPieceMove")
                    return False
            else:
                print("piece.index is index already, TryPieceMove")
                return False
        else:
            print("Nothing to move, TryPieceMove")
            return False
        print("wtf TryPieceMove")
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
        allstr.append(self.__incodetable[3][0]) # ---Конец сообщения--- 

        return "".join(allstr)

            
    def __incodeInt(self, prev, player):
        allstr = []
        for i in range(len(prev)): # Превью фигуры
            for s in prev[i]:
                allstr.append(self.__cti(self.__desk[0].index(s[0]) ))
                allstr.append(self.__cti(self.__desk[1].index(s[1:]) ))
                allstr.append(self.__cti(prev[i][s]))
                allstr.append(self.__incodetable[2][2]) # --Следующая префигура--
            allstr.append(self.__incodetable[2][1]) # --Следующий игрок--
        allstr.append(self.__incodetable[2][0]) # ---Далее---  
                
        for i in range(2): # Войска и апгрейды игроков
            s = player[i]
            allstr.append(self.__cti(s.gold[1]))
            for n in range(len(s.upgrades[1])):
                allstr.append(self.__cti(s.upgrades[1][n]))
                allstr.append(self.__cti(s.piecesnum[1][n]))
                allstr.append(self.__incodetable[2][2]) # --Следующая фигура--
            allstr.append(self.__incodetable[2][1]) # --Следующий игрок--
        allstr.append(self.__incodetable[3][0]) # ---Конец сообщения---  
                
        return "".join(allstr)
            
        
    def __incodeObj(self, desk, coord, piece, player, movequere, currentmove):
        allstr = []                             
        allstr.append(self.__cti(self.__state)) # Состояние сервера
        allstr.append(self.__cti(len(desk[0]))) # Параметры доски
        allstr.append(self.__cti(len(desk[1])))
        allstr.append(self.__incodetable[2][0]) # ---Далее---
                      
        allstr.append(self.__cti(currentmove)) # Текущий ход
        for s in movequere: # Все ходы
            allstr.append(self.__cti(s))
        allstr.append(self.__incodetable[2][0]) # ---Далее---
        
        for s in piece: # Фигуры доски
            allstr.append(self.__cti(s.id)) # ID фигуры
            allstr.append(self.__cti(s.ptid)) # Тип фигуры
            allstr.append(self.__cti(s.oldptid)) # Изначальный тип фигуры
            allstr.append(self.__cti(s.index)) # Индекс клетки
            allstr.append(self.__cti(s.ownerid)) # Номер владельца
            allstr.append(self.__cti(int(s.ability))) # Способность
            allstr.append(self.__cti(self.__lastmoves.index(s.lastmove))) # Ласт ход
            allstr.append(self.__cti(int(s.pawndirection))) # Направление фигуры
            allstr.append(self.__incodetable[2][1]) # --Следующая фигура--
        allstr.append(self.__incodetable[2][0]) # ---Далее---
        
        for s in player: # Параметры игроков
            allstr.append(self.__cti(s.id)) # ID игрока
            if s.controller=="AI": # Контроллер
                allstr.append(self.__cti(s.controller))
            else:
                allstr.append(self.__cti(-1))
            allstr.append(self.__cti(s.color)) # Цвет
            allstr.append(self.__cti(s.pawndirection)) # Направление пешек
            for t in s.team: # Команда
                allstr.append(self.__cti(int(t)))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута команда
            if len(s.onpassan)>0: # Взятие на проходе
                allstr.append(self.__cti(self.pieces.index(s.onpassan[0])))
                for t in s.onpassan[1]:
                    allstr.append(self.__cti(t))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута на проходе
            allstr.append(self.__cti(s.gold[1])) # Золото 1
            for t in range(len(s.piecesnum[1])): # Войска
                allstr.append(self.__cti(s.piecesnum[1][t]))
                allstr.append(self.__cti(s.upgrades[1][t]))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута армия-золото
            allstr.append(self.__incodetable[2][1]) # --Следующий игрок--
        allstr.append(self.__incodetable[3][0]) # --Конец сообщения--

        return "".join(allstr)
            
    
    def __addObjectsToServerClass(self):
        self.__server.objects[0] = self.__incodeObj(self.__desk,
                                                    self.__coordToIndexAndPieces,
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
            if self.__changePlayerController(i, pid):
                return True
        return False
        
    def __TryMove(self, move):
        (piecetype,index1,index2) = move
        if self.__isDestEmpty(index1):
            print("no piece at the start "+str(index1)+", __TryMove")
            return False
        else:
            piece = self.__indexToPiece(index1)[0]
        if piecetype != piece.piecetype:
            print("not right piece at the start "+str(piece.piecetype)+", __TryMove")
            return False
        
        elif pid != self.__owningPlayer(piece).controller:
            print("not right player, __TryMove")
            return False
        else:
            return self.__TryPieceMove(piece,"".join(self.__indexToCoord(index1)),index2)
        print("wtf, __TryMove")
        return False
        
    def __AddMove(self, move, pid):
        for i in self.__player:
            if i.controller == pid:
                i.addPremove(move)
                return True
        return False
        
    def __executeOrder(self, order):
        cmd = order["command"]
        if cmd=="newcomer":
            return self.__TryAddIdToPlayers(order["id"])
        elif cmd=="move":
            if self.__AddMove(order["move"],order["id"]):
                self.__currentmove = (self.__currentmove+1)%len(self.__movequeue)
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

    def __infiniteGameLoop(self):
        
        while True:

            
            while len(self.__server.newCommands) > 0:
                order = self.__server.newCommands.pop(0)
                self.__executeOrder(order)
                #print ("order "+str(order)+" "+str(self.__executeOrder(order)))

            p = self.__player[self.__movequeue[self.__currentmove]]
            if len(p.premoves)>0:
                if self.__TryMove(p.premoves[0]):
                    p.removeFirstPremove()
                    self.__currentmove = (self.__currentmove+1)%len(self.__movequeue)
                    self.server.sendToClient({"request": "premove_result", "response": True})
                else:
                    p.clearPremoves()
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
