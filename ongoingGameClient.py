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

        self.__desk = [["a","b","c","d","e","f","g","h"],["1","2","3","4","5","6","7","8"]]
        self.last_set_objects = ["none",0,0,0,0,0,0] # Последний набор объектов от сервера
        self.update_board = False
        self.last_set_interface = ["none",0,0,0] # Последний набор вторичных от сервера
        self.update_interface = False
        self.battleMoves = [] # Все ходы последнего матча
        self.textChat = [] # Все сообщения чата
        
        self.joined = join # Нужен ли сервер, False - синглплеер, True - мультиплеер
        
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
        Thread(target=self.infiniteLoop).start()

    def __addTextInt(self, mov, mes):
        for s in mov:
            self.battleMoves.append(mov)
        for s in mes:
            self.textChat.append(mes)
        return True
    
    def __removeAllPieces(self):
        return True
    
    def __rebuildBoard(self):
        return True
        
    def __UpdateDesk(self,deState,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers):
        if not(last_set_objects[1]==deState and last_set_objects[2]==deDesk):
            if last_set_objects[1]==2 and deState==1:
                self.__removeAllPieces()
                # 1 2
            last_set_objects[1] = deState
            self.__rebuildBoard()
        if not(last_set_objects[3]==deCurrMove):
            last_set_objects[3] = deCurrMove
            # 3
        if not(last_set_objects[4]==deCurrMove):
            last_set_objects[4] = deCurrMove
            # 4
        if not(last_set_objects[5]==deCurrMove):
            last_set_objects[5] = deCurrMove
            # 5
        if not(last_set_objects[6]==deCurrMove):
            last_set_objects[6] = deCurrMove
            # 6
        
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
        while s[pos]!=self.__incodetable[3][0]:
            mes.append([])
            mes[i].append(self.__ctd(s[pos:pos+2])) # Номер игрока
            m = []
            while s[pos]!=self.__incodetable[2][1]:
                m.append(s[pos]) # Символ сообщения
                pos += 1
            mes[i].append(m) # Код хода
            pos += 1  # --Следующий ход--
            
        return (mov,mes)
    
        
    def __decodeInt(self, s):
        pos = 0
        l = len(s)
        if s[-1]!=self.__incodetable[3][0]:
            return "error with message, __decodeObj"
        
        prev = [] # Превью фигуры
        i = 0
        while s[pos]!=self.__incodetable[2][0]:
            prev.append([])
            while s[pos]!=self.__incodetable[2][1]:
                #print("a = "+str(self.__desk[0][self.__ctd(s[pos:pos+2])]+self.__desk[1][self.__ctd(s[pos+2:pos+4])]))
                #print("b = "+str(self.__ctd(s[pos+4:pos+6])))
                prev[i].append({self.__desk[0][self.__ctd(s[pos:pos+2])]+self.__desk[1][self.__ctd(s[pos+2:pos+4])]:self.__ctd(s[pos+4:pos+6])})
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
            (mov,mes) = self.__decodeMov(order["new_text"])
            return self.__addTextInt(mov,mes)
    
    def infiniteLoop(self):
        
        
        while True:

            self.update_board = False
            while len(self.clientObject.newCommands) > 0:
                order = self.clientObject.newCommands.pop(0)
                self.__executeOrder(order)

            if self.update_board: # Обновить данные объектов
                (deState,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers) = self.__decodeObj(self.last_set_objects[0])
                return True#self.UpdateDesk(deState,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers)
            
            if self.update_interface: # Обновить данные вторичных
                (prev,prepieces,preupgrades) = self.__decodeInt(self.last_set_interface[0])
                return True#self.UpdateDesk(deState,deDesk,deCurrMove,deAllMoves,dePieces,dePlayers)

            pygame.time.delay(2)
            
                      


if __name__ == "__main__":
     
    print("game input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)
            
    ongoingGameClient = OngoingGameClient((HOST, PORT),join=False) # Создаем объект клиента
