import pygame
from ongoingGameServer import OngoingGameServer
#from ongoingGameWindow import OngoingGameWindow
from client import Client
import socket
from threading import Thread

class OngoingGameClient:

    def __init__(self, addr, join=False):
 
        self.__incodetable = ("0123456789abcdefghijklmnopqrstuvwxyz","%%","[],.()","-")

        pygame.init() # Инициализируем pygame
        self.__pause = True # Стоит ли игра на паузе
        self.__states = ("waiting_for_players","preparation","battle","ended")
        self.__state = 0 # Состояние клиента
        self.__server_state = 0 # Состояние сервера
        self.__player = [] # Массив игроков
        self.__createPlayers()
        
        # Создаём объект-сервер для получения команд от объектов-клиентов
        #self.__server = Server(addr)
        
        #
        #
        # Создаём стартовые переменные игры
        #
        #

        self.__movequeue = [0,1] # Очередь для ходов
        self.__currentmove = 0 # Текущий ход (индекс объекта self.__movequeue),
        # Где -1 означает ничей ход
        self.__idcolor = ["grey","red","green","purple","brown","blue"]
        self.__idcolorname = ["Серый","Красный","Зелёный","Бирюзовый","Коричневый","Голубой"]

        # Максимальный размер доски, её строки и столбцы
        self.__initialdesk = (("a","b","c","d","e","f","g","h","i","j","k","l","m","n"),("1","2","3","4","5","6","7","8","9","10","11","12","13","14"))
        self.__desk = [[],[]] # Доска
        self.__pieces = [] # Фигуры
        self.__indexToCoordAndPieces = [] # Массивы доски и её связей
        self.__coordToIndexAndPieces = {}

        self.__lastmoves = ("none","move","capture","ability")
        
        self.__piecetypes = ("lesserPawn","pawn", # Типы фигур
                           "lesserRock","rock",
                           "lesserKnight","knight",
                           "lesserBishop","bishop",
                           "queen","king")
        
        self.__piecenames = {self.__piecetypes[0]:"Сердечко", # Игровые имена фигур
                           self.__piecetypes[1]:"Пешка",
                           self.__piecetypes[2]:"Лодка",
                           self.__piecetypes[3]:"Ладья",
                           self.__piecetypes[4]:"Собака",
                           self.__piecetypes[5]:"Конь",
                           self.__piecetypes[6]:"Вор",
                           self.__piecetypes[7]:"Слон",
                           self.__piecetypes[8]:"Королева",
                           self.__piecetypes[9]:"Король"}
        ##
        ## Уникально для клиента

        self.update_board = False
        self.last_set_objects = "none"
        self.joined = join # Нужен ли сервер, False - синглплеер, True - мультиплеер

        self.premoves = [] # Премувы игрока
        self.__deskPremoved = [[],[]] # Доска после премувов
        self.__piecesPremoved = [] # Фигуры после премувов
        self.__indexToCoordAndPiecesPremoved = [] # Массивы доски и её связей
        self.__coordToIndexAndPiecesPremoved = {} # После премувов
        
        # СЕРВЕР
        self.serverAdress = addr
        if join: # Подключаемся
            self.serverObject = 0
        else: # Или создаём сервер
            self.serverObject = OngoingGameServer(addr)

        # КЛИЕНТ
        self.clientObject = Client(addr) # Создаём клиент

        # Делаем новый поток с циклом, в которoм берем данные об игроках
        Thread(target=self.infiniteLoop).start()
        
        ##
        ##

        
        #
        #
        #
        #
        #

        # Делаем новый поток с циклом, в которoм берем данные об игроках
            
        self.__createDesk() # Создаёт новую доску
        self.__premoves() # Тестовые ходы
        self.__printDeck() # Выводит доску в консоль
        
        Thread(target=self.infiniteLoop).start()
        
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
               
    def __premoves(self):
        self.__sendCmdToServer({"request": "move", "move": ("pawn",8,16)})

    def __sendCmdToServer(self,cmd):
        self.clientObject.send.append(cmd)
        
    def __printDeck(self): # Показывает доску в отладке
        return True
        s = [""]
        n = 0
        r = 0
        for i in self.__coordToIndexAndPieces:
            if self.__isDestEmpty(i):
                s[r] += "  -  "
            else:
                s[r] += " " + str(self.__coordToPiece(i)[0].name[0:2])+str(self.__coordToPiece(i)[0].ownerid) + " "
            n += 1
            if n>7:
                n = 0
                r += 1
                s.append("")
        for i in range(7,-1,-1):
            print("i="+str(i)+"   "+s[i])
        print("")

    #
    ##
    ###
    ####
    #####
    #Objects
    
    def __createPlayers(self):
        self.__player.append(self.__createPlayer(0,"AI",1,[0], True))
        self.__player.append(self.__createPlayer(1,"AI",1,[1],False))
        self.__player.append(self.__createPlayer(2,"AI",1,[2],False))
        self.__player.append(self.__createPlayer(3,"AI",1,[3],False))
        
    # Создает игрока
    def __createPlayer(self, pid, controller, color, team, pawndirection=False):
        return self.__noChessPlayer(pid, controller, color, team, pawndirection)

    def __owningPlayer(self,piece):
        return self.__player[piece.ownerid]
    
    def __changePlayerController(self, player, controller): # Меняет игрока
        return player.changeController(controller)
        
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
            
        def changeController(self, controller):
            if self.controller != controller:
                self.controller = controller
                return True
            else:
                return False

        def changeColor(self, color):
            self.color = color

        def kill(self): # Вызов деструктора
            self.__del__()
            
        def __del__(self):
            print("player deleted")
        
    
    # Создает фигуру
    def __createPiece(self, piecetype, ownerid, coord=0, index=-1, ability=True, pawndirection=False):
        if (piecetype in self.__piecetypes) and (self.__isCoordValuable(coord) or self.__isIndexValuable(index)) and(ownerid>=0 and ownerid<=4):
            if self.__isCoordValuable(coord) and (self.__isDestEmpty(coord)):
                piece = self.__noChessPiece(self.__piecenames[piecetype], piecetype, ownerid, coord, self.__coordToIndex(coord), ability, pawndirection)
                # Создаём фигуру
                self.__addPieceToDest(piece, coord) # Добавляем фигуру на доску
                self.__pieces.append(piece) # Добавляем фигуру в список фигур
                return piece
                
            elif self.__isIndexValuable(index) and (self.__indexToPiece(index)==[]):
                piece = self.__noChessPiece(self.__piecenames[piecetype], piecetype, ownerid, self.__indexToCoord(index), index, ability, pawndirection)
                # Создаём фигуру
                self.__addPieceToDest(piece, index) # Добавляем фигуру на доску
                self.__pieces.append(piece) # Добавляем фигуру в список фигур
                return piece

            else:
                print("an error with placement of a new piece")
                return -1
                 
        else:
            print("an error with atributes of a new piece")
            return -1

    # Удаляет фигуру
    def __removePiece(self, piece, dest):
        if type(piece)==self.__noChessPiece:
            self.__removePieceFromDest(piece, dest)
            piece.kill()
            return 0
        else:
            print("an error with removing piece, removePiece, type is "+str(type(piece)))
            return -1
        
    class __noChessPiece: # Класс фигуры
        def __init__(self, piecename, piecetype, ownerid, coord, index, ability=True, pawndirection=False):

            self.name = piecename # Имя фигуры
            self.piecetype = piecetype # Тип
            self.piecetypefirst = piecetype # Изначальный тип фигуры
            self.coord = coord # Точка на доске, к примеру H8
            self.index = index # Индекс точки, к примеру 63
            self.ownerid = ownerid # Индекс владельца, к примеру 1
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
            self.__del__()
            
        def __del__(self):
            self.ability = False
            
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

    def __movePieceToDest(self, piece, dest):
        if type(dest)==str or type(dest)==int:
            if type(piece)==self.__noChessPiece:
                if type(dest)==str:
                    if (self.__isCoordValuable(dest)):
                        coord = dest
                        index = self.__coordToIndex(dest)
                    else:
                        print("an error with coord dest of the square, movePieceToDest")
                        return -1
                else:#type(dest)==int: not(self.__isDestEmpty(dest)) not(self.__isDestEmpty(dest))
                    if (self.__isIndexValuable(dest)):
                        coord = self.__indexToCoord(dest)
                        coord = coord[0]+coord[1]
                        index = dest
                    else:
                        print("an error with index dest of the square, movePieceToDest")
                        return -1
                if self.__isDestEmpty(dest):
                    piece.lastmove = "move"
                else:
                    if (not(self.__isPieceAlly(piece,self.__coordToPiece(coord)[0]))):
                        piece.lastmove = "capture"
                        self.__removePiece(self.__coordToPiece(coord)[0],dest)
                    else:
                        print("an error with dest of the square (ally), movePieceToDest")
                        return -1
                        
                self.__coordToPiece(piece.coord).remove(piece)
                self.__indexToPiece(piece.index).remove(piece)

                self.__coordToPiece(coord).append(piece)
                self.__indexToPiece(index).append(piece)
                piece.coord=coord
                piece.index=index
                return 0
            else:
                print("an error with piece-object type, movePieceToDest, "+str(type(piece)))
                return -1
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
            
    # End Objects
    #####
    ####
    ###
    ##
    #
       
    def __reCreateDesk(self,width=8,height=8):
        for p in self.__pieces:
            self.__removePiece(p,p.index)
        self.__currentmove = 0
        self.__createDesk(width=width,height=height)
         
    def UpdateDesk(self, deState, deDesk, deCurrMove, deAllMoves, dePieces, dePlayers):
        #if deAllMoves != self.__movequeue:
        #    print(self.__movequeue)
        #    self.__movequeue.clear()
        #    self.__movequeue.extend(deAllMoves)
        if True:#deDesk[0]!=len(self.__desk[0]) or deDesk[1]!=len(self.__desk[1]):
            self.__reCreateDesk(width=deDesk[0],height=deDesk[1])

            self.__currentmove = deCurrMove
            self.__movequeue.clear()
            self.__movequeue.extend(deAllMoves)

            for i in range(len(dePlayers)):
                self.__player[i].id = dePlayers[i][0] # ID
                self.__player[i].controller = dePlayers[i][1] # Контроллер
                self.__player[i].color = dePlayers[i][2] #Номер цвета
                self.__player[i].pawndirection = dePlayers[i][3] # Направление пешек
                self.__player[i].team.clear() 
                self.__player[i].team.extend(dePlayers[i][4]) # Команда
                
            for i in range(len(dePieces)):
                p = self.__createPiece(self.__piecetypes[dePieces[i][0]], # Тип фигуры
                                       dePieces[i][3], # Номер игрока-владельца
                                       coord="".join(self.__indexToCoord(dePieces[i][2])), # Координата
                                       index=dePieces[i][2], # Индекс
                                       ability=dePieces[i][4], # Способность
                                       pawndirection=dePieces[i][6]) # Направление пешек
                #print("p is "+str(type(p))+" "+str(p))
                p.lastmove = dePieces[i][5] # Последний ход
                p.piecetypefirst = dePieces[i][1] # Изначальный тип фигуры

        print ("desk updated")
        self.__printDeck()
        return True

    def __ctd(self, symbol):
        if not(len(symbol)==2 and symbol[0] in self.__incodetable[0] and symbol[1] in self.__incodetable[0]):
            return -1
        return self.__incodetable[0].index(symbol[0])*len(self.__incodetable[0]) + self.__incodetable[0].index(symbol[1])
        
    def __decode(self, s):

        pos = 0
        l = len(s)
        if s[-1]!=self.__incodetable[3][0] or l<12:
            return "error with message"
        print ("")
        print ("")
        print ("")
        print (s)
        print ("")
        print ("")
        print ("")
        deState = int(self.__ctd(s[pos:pos+2])) # Состояние сервера, номер
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
                             ])
            pos += 16
            pos += 1 # ---Следующая фигура---
        pos += 1 # ---Далее---
        
        i = 0
        print("s[pos] = "+str(s[pos])+", pos0 = "+str(pos))
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
            dePlayers[i].append([int(self.__ctd(s[pos:pos+2])),[],[]]) # Подготовка, золото
            pos += 2
            while s[pos]!=self.__incodetable[2][2]:
                dePlayers[i][6][1].append(int(self.__ctd(s[pos:pos+2]))) # Подготовка, фигуры
                dePlayers[i][6][2].append(int(self.__ctd(s[pos+2:pos+4]))) # Подготовка, апгрейды
                pos += 4
            pos += 1 # Конец атрибута подготовка
            pos += 1 # --Следующий игрок--
            i += 1
            
        return (deState,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers)
    

    def __executeOrder(self, order):
        #print(order)
        cmd = order["command"]
        if cmd=="premove_result":
            return order["result"]
        elif cmd=="set_objects":
            if self.last_set_objects != order["server_objects"]:
                self.last_set_objects = order["server_objects"]
                self.update_board = True
                return True
    
    def infiniteLoop(self):
        
        
        while True:

            self.update_board = False
            while len(self.clientObject.newCommands) > 0:
                order = self.clientObject.newCommands.pop(0)
                self.__executeOrder(order)

            if self.update_board:
                (deState,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers) = self.__decode(order["server_objects"])
                return self.UpdateDesk(deState,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers)
            pygame.time.delay(2)
            
                      


if __name__ == "__main__":
     
    print("game input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)
            
    ongoingGameClient = OngoingGameClient((HOST, PORT),join=False) # Создаем объект клиента
