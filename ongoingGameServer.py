import pygame
from server import Server
from client import Client
import socket
from threading import Thread

class OngoingGameServer:

    def __init__(self, addr, max_conn=999):
        
        self.__incodetable = ("0123456789abcdefghijklmnopqrstuvwxyz","%%","[],.()","-")
        
        pygame.init() # Инициализируем pygame
        self.__pause = True # Стоит ли игра на паузе
        self.__state = "waiting_for_players" # Состояние сервера
        self.__player = [] # Массив игроков
        self.__createPlayers()
        
        # Создаём объект-сервер для получения команд от объектов-клиентов
        self.__server = Server(addr)
        
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
        #
        #
        #
        #
        #

        # Делаем новый поток с циклом, в которoм берем данные об игроках

        self.__createDesk() # Создаёт новую доску
        self.__createDefaultPieces() # Создаёт стандартные фигуры
        #self.__testmoves() # Тестовые ходы
        #self.__printDeck() # Выводит доску в консоль
        
        Thread(target=self.__infiniteGameLoop).start()
        
    def __createDesk(self,width=8,height=8):
        self.__desk.clear()
        self.__desk.append(self.__initialdesk[0][:width])
        self.__desk.append(self.__initialdesk[1][:height])
        count = 0
        self.__indexToCoordAndPieces = [] # Массивы доски и её связей
        self.__coordToIndexAndPieces = {}
        for i in self.__desk[1]:
            for n in self.__desk[0]:
                self.__indexToCoordAndPieces.append([(n,i),[]])
                self.__coordToIndexAndPieces[n+i] = [count,[]]
                count +=1
                
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
        print("len c is "+str(len(self.__coordToIndexAndPieces)))
        print("len i is "+str(len(self.__indexToCoordAndPieces)))
        
    def __createDefaultPieces(self): # Создаёт набор стандартных фигур для игроков 0 и 1
        for new in (("rock",0,"a1",True),
                    ("knight",0,"b1",True),
                    ("bishop",0,"c1",True),
                    ("queen",0,"d1",True),
                    ("king",0,"e1",True),
                    ("lesserBishop",0,"f1",True),
                    ("knight",0,"g1",True),
                    ("rock",0,"h1",True),
                    
                    ("pawn",0,"a2",True),
                    ("pawn",0,"b2",True),
                    ("pawn",0,"c2",True),
                    ("pawn",0,"d2",True),
                    ("pawn",0,"e2",True),
                    ("lesserPawn",0,"f2",True),
                    ("lesserPawn",0,"g2",True),
                    ("lesserPawn",0,"h2",True),
                    
                    ("rock",1,"a8",False),
                    ("knight",1,"b8",False),
                    ("bishop",1,"c8",False),
                    ("queen",1,"d8",False),
                    ("king",1,"e8",False),
                    ("lesserBishop",1,"f8",False),
                    ("knight",1,"g8",False),
                    ("rock",1,"h8",False),
                    
                    ("pawn",1,"a7",False),
                    ("pawn",1,"b7",False),
                    ("pawn",1,"c7",False),
                    ("pawn",1,"d7",False),
                    ("pawn",1,"e7",False),
                    ("lesserPawn",1,"f7",False),
                    ("lesserPawn",1,"g7",False),
                    ("lesserPawn",1,"h7",False),
                    ):
            newpiece = self.__createPiece(new[0],new[1],new[2],pawndirection=new[3])

    def __currentState(self):
        return __state
    
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
        
    # Создает игроков
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
            
        def clearOnpassan(self,piece,squeres):
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
            print("piece deleted")
            
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
                if (not(self.__isDestEmpty(dest))):
                    if (not(self.__isPieceAlly(piece,self.__coordToPiece(coord)[0]))):
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
            
        
    #
    #
    #
    #
    def __TryLesserPawnMove(self, piece, coord, index): # Пробует походить lesserPawn в нужную точку
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

    def __TryLesserRockMove(self, piece, coord, index): # Пробует походить lesserRock в нужную точку
        return False
    
    def __TryLesserKnightMove(self, piece, coord, index): # Пробует походить lesserKnight в нужную точку
        return False
    
    def __TryLesserBishopMove(self, piece, coord, index): # Пробует походить lesserBishop в нужную точку
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
        elif self.__indexToPiece(index)[0].piecetype=="king":
            return self.__TryKingMove(self.__indexToPiece(index)[0],piece.coord,piece.index)
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
    
    def __TryKingMove(self, piece, coord, index): # Пробует походить king в нужную точку
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
                        self.__movePieceToDest(piece, index+diff)
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
        

    def __TryPieceMove(self, piece, coord, index): # Пробует походить
        if type(piece)==self.__noChessPiece:
            if piece.index!=index:
                if self.__isIndexInDeck(index):
                    if piece.piecetype == "lesserPawn":
                        return self.__TryLesserPawnMove(piece, coord, index)
                    elif piece.piecetype == "lesserRock":
                        return self.__TryLesserRockMove(piece, coord, index)
                    elif piece.piecetype == "lesserKnight":
                        return self.__TryLesserKnightMove(piece, coord, index)
                    elif piece.piecetype == "lesserBishop":
                        return self.__TryLesserBishopMove(piece, coord, index)
                    elif piece.piecetype == "pawn":
                        return self.__TryPawnMove(piece, coord, index)
                    elif piece.piecetype == "rock":
                        return self.__TryRockMove(piece, coord, index)
                    elif piece.piecetype == "knight":
                        return self.__TryKnightMove(piece, coord, index)
                    elif piece.piecetype == "bishop":
                        return self.__TryBishopMove(piece, coord, index)
                    elif piece.piecetype == "queen":
                        return self.__TryQueenMove(piece, coord, index)
                    elif piece.piecetype == "king":
                        return self.__TryKingMove(piece, coord, index)
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
        
    def __incode(self, desk, coord, piece, player, movequere, currentmove):
        allstr = []
        allstr.append(self.__cti(len(desk[0]))) # Параметры доски
        allstr.append(self.__cti(len(desk[1])))
        allstr.append(self.__incodetable[2][0]) # ---Далее---
                      
        allstr.append(self.__cti(currentmove)) # Текущий ход
        for s in movequere: # Все ходы
            allstr.append(self.__cti(s))
        allstr.append(self.__incodetable[2][0]) # ---Далее---
        
        for s in piece: # Фигуры доски
            allstr.append(self.__cti(self.__piecetypes.index(s.piecetype)))
            allstr.append(self.__cti(self.__piecetypes.index(s.piecetypefirst)))
            allstr.append(self.__cti(s.index))
            allstr.append(self.__cti(s.ownerid))
            allstr.append(self.__cti(int(s.ability)))
            allstr.append(self.__cti(self.__lastmoves.index(s.lastmove)))
            allstr.append(self.__cti(int(s.pawndirection)))
            allstr.append(self.__incodetable[2][1]) # --Следующая фигура--
        allstr.append(self.__incodetable[2][0]) # ---Далее---
        
        for s in player: # Параметры игроков
            allstr.append(self.__cti(s.id))
            if s.controller=="AI":
                allstr.append(self.__cti(s.controller))
            else:
                allstr.append(self.__cti(-1))
            allstr.append(self.__cti(s.color))
            allstr.append(self.__cti(s.pawndirection))
            for t in s.team: # Команда
                allstr.append(self.__cti(int(t)))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута команда
            if len(s.onpassan)!=0: # Взятие на проходе
                allstr.append(self.__cti(self.pieces.index(s.onpassan[0])))
                for t in s.onpassan[1]:
                    allstr.append(self.__cti(t))
            allstr.append(self.__incodetable[2][2]) # Конец атрибута на проходе
            allstr.append(self.__incodetable[2][1]) # --Следующий игрок--
        allstr.append(self.__incodetable[3][0]) # --Конец сообщения--

        return "".join(allstr)
    
    def __addObjectsToServerClass(self):
        self.__server.objects = self.__incode(self.__desk,
                                              self.__coordToIndexAndPieces,
                                              self.__pieces,
                                              self.__player,
                                              self.__movequeue
                                              ,self.__currentmove)

    def __TryAddIdToPlayers(self, pid):
        for i in self.__player:
            if self.__changePlayerController(i, pid):
                return True
        return False
        
    def __TryMove(self, move, pid):
        if not(self.__player[self.__currentmove].controller == pid):
            print("not "+str(pid)+" turn, __TryMove")
            return False
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
        
    def __executeOrder(self, order):
        cmd = order["command"]
        if cmd=="newcomer":
            return self.__TryAddIdToPlayers(order["id"])
        elif cmd=="move":
            if self.__TryMove(order["move"],order["id"]):
                self.__currentmove = (self.__currentmove+1)%len(self.__movequeue)
                return True
            else:
                return False
        return False

    def __infiniteGameLoop(self):
        
        while True:

            
            while self.__server.newCommands != []:
                order = self.__server.newCommands[0]
                self.__server.newCommands.remove(order)
                print ("order "+str(order)+" "+str(self.__executeOrder(order)))

            self.__addObjectsToServerClass()
            pygame.time.delay(2)

        



if __name__ == "__main__":
     
    print("game input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)
            
    ongoingGameClient = OngoingGameClient((HOST, PORT),join=False) # Создаем объект клиента
