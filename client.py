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
        self.newCommands = [] # Данные ответа на запрос

        self.send = [] # Команды для отправки серверу
            
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
            
    def __getObjects(self):
        while True:
            self.__conn.sendall(bytes(json.dumps({"request": "get_objects"}), 'UTF-8'))
            # Отправляем серверу запрос для обновления данных объектов,
            # а также указываем серверу этим на то, что клиент в обработке
            while len(self.send)>0: # Проверяем, нужно ли что-то сообщить серверу
                s =self.send.pop(0)
                self.__conn.sendall(bytes(json.dumps(s), 'UTF-8'))
            
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
                for d in self.__data:
                    cmd = d["request"]
                    if cmd == "set_objects": # Запрос данных
                        self.newCommands.append({"command":"set_objects","server_objects":d["response"]})
                    elif cmd == "premove_result":
                        self.newCommands.append({"command":"premove_result","result":d["response"]})


if __name__ == "__main__":
    
    print("input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)

    server = Client((HOST, PORT))

