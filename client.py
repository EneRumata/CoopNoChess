import socket
import json
from threading import Thread

class Client:

    def __init__(self, addr):
        self.__conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__conn.connect(addr) # подключаемся к айпи адресу сервера
        
        self.__incodetable = ("0123456789abcdefghijklmnopqrstuvwxyz","%%","[],.()","-")
        
        self.__waiting = 0 # Кол-во ожиданий ответа до дисконнекта
        self.__data = [] # Данные ответа на запрос
        self.unreaddata = [] # Данные ответа на запрос

        self.send = [{"request": "move", "move": ("pawn",8,16)}] # Команды для отправки серверу
            
        self.objects = [] # Создаем массив для хранения данных об объектах

        Thread(target=self.__getObjects).start()
        # Делаем новый поток с циклом, в которым берем данные об игроках

    def __jsonFixError(self):# Преобразовывает байтовую строку в текст и исправляет ошибки
        self.__data="["+self.__data.decode('utf-8')+"]"
        i = 2
        while i<len(self.__data)-1:
            if self.__data[i]=="}" and self.__data[i+1]=="{":
                self.__data=self.__data[:i+1]+","+self.__data[(i+1):]
                i+=3
            else:
                i+=1
            
    def __ctd(self, symbol):
        if not(len(symbol)==2 and symbol[0] in self.__incodetable[0] and symbol[1] in self.__incodetable[0]):
            return -1
        return self.__incodetable[0].index(symbol[0])*len(self.__incodetable[0]) + self.__incodetable[0].index(symbol[1])
        
    def __decode(self, s):

        l = len(s)
        if s[-1]!=self.__incodetable[3][0] or l<12:
            return "error with message"
        desk = (self.__ctd(s[0:2]),self.__ctd(s[2:4])) # Доска
         # ---Далее---
        curmove = self.__ctd(s[6:8]) # Текущий ход

        pos = 9 # ---Далее---
        allmoves = [] # Очерёдность ходов
        while s[pos]!=self.__incodetable[2][0]:
            allmoves.append(self.__ctd(s[pos:pos+2]))
            pos +=2       

        pos += 1 # ---Далее---
        pieces = [] # Фигуры
        while s[pos]!=self.__incodetable[2][0]:
            pieces.append([self.__ctd(s[pos:pos+2]), # Номер фигуры
                           self.__ctd(s[pos+2:pos+4]), # Изначальный номер фигуры
                           self.__ctd(s[pos+4:pos+6]), # Точка на доске 
                           self.__ctd(s[pos+6:pos+8]), # Номер владельца
                           self.__ctd(s[pos+8:pos+10]), # Способность
                           self.__ctd(s[pos+10:pos+12]), # Номер последнего хода
                           self.__ctd(s[pos+12:pos+14]), # Направление движения
                           ])
            pos += 15 # --Следующая фигура--

        pos += 1 # ---Далее---
        i = 0
        players = [] # Игроки
        while s[pos]!=self.__incodetable[3][0]:
            players.append([self.__ctd(s[pos:pos+2]), # Номер игрока
                           self.__ctd(s[pos+2:pos+4]), # Контроллер
                           self.__ctd(s[pos+4:pos+6]), # Цвет 
                           self.__ctd(s[pos+6:pos+8]), # Направление движения
                           []])
            pos += 8 # Команда
            while s[pos]!=self.__incodetable[2][2]:
                players[i][4].append(self.__ctd(s[pos:pos+2]))
                pos += 2
            pos += 1 # Конец атрибута команда
            players[i].append([self.__ctd(s[pos:pos+2]),[]]) # Взятие на проходе
            pos += 2 # Взятие на проходе, клетки
            while s[pos]!=self.__incodetable[2][2]:
                players[i][5][1].append(self.__ctd(s[pos:pos+2]))
                pos += 2
            pos += 1 # Конец атрибута на проходе
            pos += 1 # --Следующий игрок--
            
        return (desk,curmove,allmoves,pieces,players)
    
    def __getObjects(self):
        while True:
            self.__conn.sendall(bytes(json.dumps({"request": "get_objects"}), 'UTF-8'))
            # Отправляем серверу запрос для обновления данных объектов,
            # а также указываем серверу этим на то, что клиент в обработке
            for s in self.send: # Проверяем, нужно ли что-то сообщить серверу
                self.__conn.sendall(bytes(json.dumps(s), 'UTF-8'))
            self.send.clear()
            
            self.__data.clear()
            self.__data = self.__conn.recv(1024) # ждем запросов от клиента

            if not self.__data: # если запросы перестали поступать, то ждём несколько итераций
                if self.__waiting>10:
                    self.__conn.close()
                    return
                else:
                    self.__waiting += 1
            else:
                self.__waiting = 0

                self.__jsonFixError()

                # загружаем данные в json формате
                self.__data = json.loads(self.__data)
                #print(type(self.__data))
                for cmd in self.__data:
                    #if cmds["request"]=="set_objects":
                    #    self.unreaddata.append({"request":"set_objects","response":self.__decode(cmd["response"])})
                    self.unreaddata.append(cmd)
                self.unreaddata.append(self.__data)

    def __move(self, code):
        self.sock.sendall(bytes(json.dumps({
            "request": "move",
            "move": code
        }), 'UTF-8')) # Отправляем серверу запрос для передвижения фигуры

    def __click(self, button):
        self.sock.sendall(bytes(json.dumps({
            "request": "click",
            "click": button
        }), 'UTF-8')) # Отправляем серверу запрос о нажании кнопки интерфейса


if __name__ == "__main__":
    
    print("input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)

    server = Client((HOST, PORT))

