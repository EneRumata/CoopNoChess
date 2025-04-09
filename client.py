import socket
import json
from threading import Thread

class Client:

    def __init__(self, addr):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(addr) # подключаемся к айпи адресу сервера
        
        self.waiting = 0 # Кол-во ожиданий ответа до дисконнекта
        self.data = 0 # Данные ответа на запрос

        self.objects = [] # Создаем массив для хранения данных об объектах

        Thread(target=self.getObjects).start()
        # Делаем новый поток с циклом, в которым берем данные об игроках

    def jsonFixError(self):# Преобразовывает байтовую строку в текст и исправляет ошибки
        self.data="["+self.data.decode('utf-8')+"]"
        i = 2
        while i<len(self.data)-1:
            if self.data[i]=="}" and self.data[i+1]=="{":
                self.data=self.data[:i+1]+","+self.data[(i+1):]
                i+=3
            else:
                i+=1
            
    def getObjects(self):
        while True:
            self.conn.sendall(bytes(json.dumps({"request": "get_objects"}), 'UTF-8'))
            # Отправляем серверу запрос для обновления данных объектов,
            # а также указываем серверу этим на то, что клиент в обработке

            self.data = self.conn.recv(1024) # ждем запросов от клиента
            self.jsonFixError()

            if not self.data: # если запросы перестали поступать, то ждём несколько итераций
                if self.waiting>10:
                    self.conn.close()
                    return
                else:
                    self.waiting += 1
            else:
                self.waiting = 0

            # загружаем данные в json формате
            self.data = json.loads(self.data)
            self.data = self.data

    def move(self, code):
        self.sock.sendall(bytes(json.dumps({
            "request": "move",
            "move": code
        }), 'UTF-8')) # Отправляем серверу запрос для передвижения фигуры

    def click(self, button):
        self.sock.sendall(bytes(json.dumps({
            "request": "click",
            "move": button
        }), 'UTF-8')) # Отправляем серверу запрос о нажании кнопки интерфейса


if __name__ == "__main__":
    
    print("input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)

    server = Client((HOST, PORT))

