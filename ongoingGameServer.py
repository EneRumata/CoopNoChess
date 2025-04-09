import pygame
from server import Server
from client import Client
import socket
from threading import Thread

class OngoingGameServer:

    def __init__(self, addr, max_conn=999):
 
        pygame.init() # Инициализируем pygame

        self.movequeue = [] # Очередь для ходов
        self.currentmove = -1 # Текущий ход (индекс объекта self.movequeue),
        # Где -1 означает ничей ход
        self.playercontroller = [] # Кто контролирует игрока (ии, клиент)
        self.playerid = [] # ID игроков
        self.playerteam = [] # Союзники игрока

        
        # Создаем словарь для хранения данных об объектах

        #
        #
        # Создаём стартовые переменные игры
        #
        #

        self.piecetypes = ("lesserPawn","pawn", # Типы фигур
                           "lesserRock","rock",
                           "lesserKnight","knight",
                           "lesserBishop","bishop",
                           "queen","king")
        
        self.piecenames = {self.piecetypes[0]:"Сердечко", # Игровые имена фигур
                           self.piecetypes[1]:"Пешка",
                           self.piecetypes[2]:"Лодка",
                           self.piecetypes[3]:"Ладья",
                           self.piecetypes[4]:"Собака",
                           self.piecetypes[5]:"Конь",
                           self.piecetypes[6]:"Вор",
                           self.piecetypes[7]:"Слон",
                           self.piecetypes[8]:"Королева",
                           self.piecetypes[9]:"Король"}
        
        
        self.desk = (("a","b","c","d","e","f","g","h","i","j","k","l","m","n"),("1","2","3","4","5","6","7","8","9","10","11","12","13","14"))
        # Размер доски, её строки и столбцы
        count = 0
        self.indexToCoordAndPieces = [] # Массивы доски и её связей
        self.coordToIndexAndPieces = {}
        for i in self.desk[1]:
            for n in self.desk[0]:
                self.indexToCoordAndPieces.append([(n,i),[]])
                self.coordToIndexAndPieces[n+i] = [count,[]]
                count +=1
                
        self.pieces = [] # Фигуры

        self.createDefaultPieces()
        #self.movePieceToDest(self.pieces[1],"a7")
        self.testmoves()
        self.printDeck()
        #
        #
        #
        #
        #
        
        
        self.server = Server(addr)
        # Создаём объект-сервер для получения команд от объектов-клиентов
        
        Thread(target=self.infiniteGameLoop).start()
        # Делаем новый поток с циклом, в которoм берем данные об игроках

    def testmoves(self):
        print("t a3 "+str(self.TryPieceMove(self.pieces[8],"a3",16)))
        print("t c3 "+str(self.TryPieceMove(self.pieces[10],"c3",18)))
        print("t h3 "+str(self.TryPieceMove(self.pieces[15],"h3",23)))
        
        print("f a3 "+str(self.TryPieceMove(self.pieces[8],"h2",15)))
        print("f c3 "+str(self.TryPieceMove(self.pieces[10],"c2",10)))
        print("f c3 "+str(self.TryPieceMove(self.pieces[15],"a4",24)))

        print("t b4 "+str(self.TryPieceMove(self.pieces[9],"b4",25)))
        print("t c4 "+str(self.TryPieceMove(self.pieces[10],"c4",26)))
        print("t c3 "+str(self.TryPieceMove(self.pieces[1],"c3",18)))
        print("t b2 "+str(self.TryPieceMove(self.pieces[2],"b2",9)))
        print("t a2 "+str(self.TryPieceMove(self.pieces[3],"a2",8)))
        print("t e1 "+str(self.TryPieceMove(self.pieces[0],"e1",4)))
        
    def printDeck(self): # Показывает доску в отладке
        s = [""]
        n = 0
        r = 0
        for i in self.coordToIndexAndPieces:
            if self.isDestEmpty(i):
                s[r] += "  -  "
            else:
                s[r] += " " + str(self.coordToPiece(i)[0].name[0:2])+str(self.coordToPiece(i)[0].ownerid) + " "
            n += 1
            if n>7:
                n = 0
                r += 1
                s.append("")
        for i in range(7,-1,-1):
            print("i="+str(i)+"   "+s[i])
        print("len c is "+str(len(self.coordToIndexAndPieces)))
        print("len i is "+str(len(self.indexToCoordAndPieces)))
        
    def createDefaultPieces(self): # Создаёт набор стандартных фигур для игроков 0 и 1
        for new in (("rock",0,"a1",True),
                    ("knight",0,"b1",True),
                    ("bishop",0,"c1",True),
                    ("queen",0,"d1",True),
                    ("king",0,"e1",True),
                    ("bishop",0,"f1",True),
                    ("knight",0,"g1",True),
                    ("rock",0,"h1",True),
                    
                    ("pawn",0,"a2",True),
                    ("pawn",0,"b2",True),
                    ("pawn",0,"c2",True),
                    ("pawn",0,"d2",True),
                    ("pawn",0,"e2",True),
                    ("pawn",0,"f2",True),
                    ("pawn",0,"g2",True),
                    ("pawn",0,"h2",True),
                    
                    ("rock",1,"a8",False),
                    ("knight",1,"b8",False),
                    ("bishop",1,"c8",False),
                    ("queen",1,"d8",False),
                    ("king",1,"e8",False),
                    ("bishop",1,"f8",False),
                    ("knight",1,"g8",False),
                    ("rock",1,"h8",False),
                    
                    ("pawn",1,"a7",False),
                    ("pawn",1,"b7",False),
                    ("pawn",1,"c7",False),
                    ("pawn",1,"d7",False),
                    ("pawn",1,"e7",False),
                    ("pawn",1,"f7",False),
                    ("pawn",1,"g7",False),
                    ("pawn",1,"h7",False),
                    ):
            newpiece = self.createPiece(new[0],new[1],new[2],pawndirection=new[3])
            
    # Создает фигуру
    def createPiece(self, piecetype, ownerid, coord=0, index=-1, ability=True, pawndirection=False):
        if (piecetype in self.piecetypes) and (self.isCoordValuable(coord) or self.isIndexValuable(index)) and(ownerid>=0 and ownerid<=4):
            if self.isCoordValuable(coord) and (self.isDestEmpty(coord)):
                piece = self.noChessPiece(self.piecenames[piecetype], piecetype, ownerid, coord, self.coordToIndex(coord), ability, pawndirection)
                # Создаём фигуру
                self.addPieceToDest(piece, coord) # Добавляем фигуру на доску
                self.pieces.append(piece) # Добавляем фигуру в список фигур
                return piece
                
            elif self.isIndexValuable(index) and (self.indexToPiece(index)==[]):
                piece = self.noChessPiece(self.piecenames[piecetype], piecetype, ownerid, self.indexToCoord(index), index, ability, pawndirection)
                # Создаём фигуру
                self.addPieceToDest(piece, index) # Добавляем фигуру на доску
                self.pieces.append(piece) # Добавляем фигуру в список фигур
                return piece

            else:
                print("an error with placement of a new piece")
                return -1
                 
        else:
            print("an error with atributes of a new piece")
            return -1

    # Удаляет фигуру
    def removePiece(self, piece, dest):
        if type(piece)==self.noChessPiece:
            self.removePieceFromDest(piece, dest)
            piece.kill()
            return 0
        else:
            print("an error with removing piece, removePiece, type is "+str(type(piece)))
            return -1
    
    class noChessPiece: # Класс фигуры
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

    # Союзная ли фигура
    def isIndexInDeck(self, index):
        return (index>0 and index<(len(self.desk[0])*len(self.desk[1])))
        
    def isPieceAlly(self, piece1, piece2):
        return piece1.ownerid == piece2.ownerid
        
    def isCoordValuable(self, coord):
        return (coord in self.coordToIndexAndPieces)
    
    def isIndexValuable(self, index):
        return (index>=0 and index<len(self.indexToCoordAndPieces))
    
    def coordToIndex(self, coord):
        return self.coordToIndexAndPieces[coord][0]
    
    def indexToCoord(self, index):
        return self.indexToCoordAndPieces[index][0]
    
    def coordToPiece(self, coord):
        #print("coord="+str(coord)+",l="+str(len(self.coordToIndexAndPieces[coord][1])))
        answer = self.coordToIndexAndPieces[coord][1] #if (len(self.coordToIndexAndPieces[coord][1])>0) else False
        return answer
    
    def indexToPiece(self, index):
        #print("index="+str(index)+",l="+str(len(self.indexToCoordAndPieces[index][1])))
        answer = self.indexToCoordAndPieces[index][1] #if (len(self.indexToCoordAndPieces[index][1])>0) else False
        return answer

    def isDestEmpty(self, dest):
        if (type(dest)==str or type(dest)==int):
            if type(dest)==str:
                if self.isCoordValuable(dest):
                    coord = dest
                    index = self.coordToIndex(dest)
                else:
                    print("an error with coord dest of the square, isDestEmpty")
                    return -1
            else:#type(dest)==int:
                if self.isIndexValuable(dest):
                    coord = self.indexToCoord(dest)
                    coord = coord[0]+coord[1]
                    index = dest
                else:
                    print("an error with coord dest of the square, isDestEmpty")
                    return -1
            return len(self.coordToIndexAndPieces[coord][1])==0 and len(self.indexToCoordAndPieces[index][1])==0
        else:
            print("an error with dest of the square, isDestEmpty, type is "+str(type(dest)))
            return -1

    def removePieceFromDest(self, piece, dest): # Удаляет фигуру с доски
        if type(dest)==str or type(dest)==int:
            if type(dest)==str:
                if (self.isCoordValuable(dest) and not(self.isDestEmpty(dest))):
                    coord = dest
                    index = self.coordToIndex(dest)
                else:
                    print("an error with coord dest of the square, removePieceFromDest")
                    return -1
            else:#type(dest)==int:
                if (self.isIndexValuable(dest) and not(self.isDestEmpty(dest))):
                    coord = self.indexToCoord(dest)
                    coord = coord[0]+coord[1]
                    index = dest
                else:
                    print("an error with index dest of the square, removePieceFromDest")
                    return -1
            self.coordToIndexAndPieces[coord][1].remove(piece)
            self.indexToCoordAndPieces[index][1].remove(piece)
            piece.coord=="none"
            piece.index==-1
            return 0
        else:
            print("an error with dest of the square, removePieceFromDest, type is "+str(type(dest)))
            return -1
        
    def addPieceToDest(self, piece, dest):
        if type(dest)==str or type(dest)==int:
            if type(dest)==str:
                if (self.isCoordValuable(dest) and self.isDestEmpty(dest)):
                    coord = dest
                    index = self.coordToIndex(dest)
                else:
                    print("an error with coord dest of the square, addPieceToDest")
                    return -1
            else:#type(dest)==int:
                if (self.isIndexValuable(dest) and not(self.isDestEmpty(dest))):
                    coord = self.indexToCoord(dest)
                    coord = coord[0]+coord[1]
                    index = dest
                else:
                    print("an error with index dest of the square, addPieceToDest")
                    return -1
            self.coordToIndexAndPieces[coord][1].append(piece)
            self.indexToCoordAndPieces[index][1].append(piece)
            piece.coord==coord
            piece.index==index
            return 0
        else:
            print("an error with dest of the square, addPieceToDest, "+str(type(dest)))
            return -1

    def movePieceToDest(self, piece, dest):
        if type(dest)==str or type(dest)==int:
            if type(piece)==self.noChessPiece:
                if type(dest)==str:
                    if (self.isCoordValuable(dest)):
                        coord = dest
                        index = self.coordToIndex(dest)
                    else:
                        print("an error with coord dest of the square, movePieceToDest")
                        return -1
                else:#type(dest)==int: not(self.isDestEmpty(dest)) not(self.isDestEmpty(dest))
                    if (self.isIndexValuable(dest)):
                        coord = self.indexToCoord(dest)
                        coord = coord[0]+coord[1]
                        index = dest
                    else:
                        print("an error with index dest of the square, movePieceToDest")
                        return -1
                if (not(self.isDestEmpty(dest))):
                    if (not(self.isPieceAlly(piece,self.coordToPiece(coord)[0]))):
                        self.removePiece(self.coordToPiece(coord)[0],dest)
                    else:
                        print("an error with dest of the square (ally), movePieceToDest")
                        return -1
                        
                self.coordToPiece(piece.coord).remove(piece)
                self.indexToPiece(piece.index).remove(piece)

                self.coordToPiece(coord).append(piece)
                self.indexToPiece(index).append(piece)
                piece.coord=coord
                piece.index=index
                return 0
            else:
                print("an error with piece-object type, movePieceToDest, "+str(type(piece)))
                return -1
        else:
            print("an error with dest of the square, movePieceToDest, "+str(type(dest)))
            return -1
        
    def changePieceType(self, piece, newtype):
        if ((type(piece)==self.noChessPiece) and (newtype in self.piecetypes)):
            piece.changeType(newtype,self.piecenames[newtype])
            return 0
        else:
            print("an error with newtype or piece-object type, movePieceToDest, "+str(type(piece)))
            return -1
            
        
    #
    #
    #
    #
    def TryLesserPawnMove(self, piece, coord, index): # Пробует походить lesserPawn в нужную точку
        width = len(self.desk[0])
        if piece.pawndirection: # True - вверх по доске (это вперёд по координатам),
            # а False - вниз по доске и назад по координатам
            multiplier = 1
        else:
            multiplier = -1
        diff = index - piece.index
        if diff == -1:
            if piece.index//width!=0 and self.isDestEmpty(index) and piece.ability:
                self.movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move left TryLesserPawnMove")
                return False
        elif diff == (multiplier*width):
            if self.isDestEmpty(index) or not(self.isPieceAlly(piece,self.indexToPiece(index)[0])):
                self.movePieceToDest(piece, index)
                return True
            else:
                print("Cannot move middle TryLesserPawnMove")
                return False
        elif diff == 1:
            if piece.index//width!=width-1 and self.isDestEmpty(index) and piece.ability:
                self.movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move rigth TryLesserPawnMove")
                return False

        else:
            print("Impossible move TryLesserPawnMove")
            return False
        return False

    def TryLesserRockMove(self, piece, coord, index): # Пробует походить lesserRock в нужную точку
        return True
    def TryLesserKnightMove(self, piece, coord, index): # Пробует походить lesserKnight в нужную точку
        return True
    def TryLesserBishopMove(self, piece, coord, index): # Пробует походить lesserBishop в нужную точку
        return True
    def TryPawnMove(self, piece, coord, index): # Пробует походить pawn в нужную точку
        width = len(self.desk[0])
        if piece.pawndirection: # True - вверх по доске (это вперёд по координатам),
            # а False - вниз по доске и назад по координатам
            multiplier = 1
        else:
            multiplier = -1
        diff = index - piece.index
        if diff == (multiplier*width)-1:
            if piece.index//width!=0 and not(self.isDestEmpty(index) or self.isPieceAlly(piece,self.indexToPiece(index)[0])):
                self.movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move left TryPawnMove")
                return False
        elif diff == (multiplier*width):
            if self.isDestEmpty(index):
                self.movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move middle TryPawnMove")
                return False
        elif diff == (multiplier*width)+1:
            if piece.index//width!=width-1 and not(self.isDestEmpty(index) or self.isPieceAlly(piece,self.indexToPiece(index)[0])):
                self.movePieceToDest(piece, index)
                piece.ability = False
                return True
            else:
                print("Cannot move rigth TryPawnMove")
                return False
        elif diff == (multiplier*width)*2:
            if self.isDestEmpty(index) and self.isDestEmpty(index-width) and piece.ability:
                self.movePieceToDest(piece, index)
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
    
    def TryRockMove(self, piece, coord, index): # Пробует походить rock в нужную точку
        width = len(self.desk[0])
        height = len(self.desk[1])
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
        for i in range(piece.index+multiplier, index, step*multiplier):
            if not(self.isDestEmpty(i)):
                print("Impossible blocked move with index "+str(i)+" step "+str(multiplier*step)+" TryRockMove")
                return False
        if self.isDestEmpty(index) or not(self.isPieceAlly(piece,self.indexToPiece(index)[0])):
            self.movePieceToDest(piece, index)
            piece.ability = False
            return True
        elif self.indexToPiece(index)[0].piecetype=="king":
            king = self.indexToPiece(index)[0]
            if self.isIndexInDeck(index-2*step*multiplier) and (self.isDestEmpty(index-2*step*multiplier) or self.indexToPiece(index-2*step*multiplier)[0]==piece):
                if piece.index!=index-1*step*multiplier:
                    self.movePieceToDest(piece, index-1*step*multiplier)
                    piece.ability = False
                    self.movePieceToDest(king, index-2*step*multiplier)
                    king.ability = False
                    return True
            else:
                 print("Cant move the king to castle TryRockMove")
                 return False
        else:
            print("Impossible move with piece at the end TryRockMove")
            return False
        print("wtf TryRockMove")
        return False
        
    def TryKnightMove(self, piece, coord, index): # Пробует походить knight в нужную точку
        self.movePieceToDest(piece, index)
        return True
    def TryBishopMove(self, piece, coord, index): # Пробует походить bishop в нужную точку
        self.movePieceToDest(piece, index)
        return True
    def TryQueenMove(self, piece, coord, index): # Пробует походить queen в нужную точку
        self.movePieceToDest(piece, index)
        return True
    def TryKingMove(self, piece, coord, index): # Пробует походить king в нужную точку
        self.movePieceToDest(piece, index)
        return True
        

    def TryPieceMove(self, piece, coord, index): # Пробует походить
        if type(piece)==self.noChessPiece:
            if self.isIndexInDeck(index):
                if piece.piecetype == "lesserPawn":
                    return self.TryLesserPawnMove(piece, coord, index)
                elif piece.piecetype == "lesserRock":
                    return self.TryLesserRockMove(piece, coord, index)
                elif piece.piecetype == "lesserKnight":
                    return self.TryLesserKnightMove(piece, coord, index)
                elif piece.piecetype == "lesserBishop":
                    return self.TryLesserBishopMove(piece, coord, index)
                elif piece.piecetype == "pawn":
                    return self.TryPawnMove(piece, coord, index)
                elif piece.piecetype == "rock":
                    return self.TryRockMove(piece, coord, index)
                elif piece.piecetype == "knight":
                    return self.TryKnightMove(piece, coord, index)
                elif piece.piecetype == "bishop":
                    return self.TryBishopMove(piece, coord, index)
                elif piece.piecetype == "queen":
                    return self.TryQueenMove(piece, coord, index)
                elif piece.piecetype == "king":
                    return self.TryKingMove(piece, coord, index)
                else:
                    print("Incorrect piece type, TryPieceMove")
                    return False
            else:
                print("index off the board, TryPieceMove")
                return False
        else:
            print("Nothing to move, TryPieceMove")
            return False
        print("wtf TryPieceMove")
        return False
        
    def isOrderPossible(self, order):

        return True
        
    def executeOrder(self, order):
        
        return True

    def infiniteGameLoop(self):
        
        while True:
            while self.server.newCommands != []:
                order = self.server.newCommands[0]
                print("0st "+order)
                self.server.newCommands.remove(order)
                print("1st "+order)

                if self.isOrderPossible(order):
                    self.executeOrder(order)

            pygame.time.delay(2)

        



if __name__ == "__main__":
     
    print("game input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)
            
    ongoingGameClient = OngoingGameClient((HOST, PORT),join=False) # Создаем объект клиента
