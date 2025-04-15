import socket
from threading import Thread
import json

class Server:

    def __init__(self, addr, max_conn=999):

        self.newCommands = [] # Новые команды для оболочки игры-сервера
        
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.bind(addr) # запускаем сервер от заданного адреса

        self.objects = ""

        self.__players = [] # создаем массив данных игроков на сервере
        
        self.__max_players = max_conn # максимум людей на сервере
        self.__sock.listen(self.__max_players) # устанавливаем максимальное
        # кол-во прослушиваний на сервере (пока не используется)

        Thread(target=self.__listen).start() # Запускаем в новом потоке проверку действий игрока

    def sendToClient(self, cmd, pid):
        self.__players[pid].send.append(cmd)
        
    class __ClientThreadPack:
        def __init__(self, player_parent_object, player_conn, player_addr, player_id):
            self.__parent = player_parent_object
            self.__conn = player_conn
            self.__addr = player_addr
            self.id = player_id
            self.__waiting = 0 # Кол-во ожиданий ответа до дисконнекта
            self.__data = "" # Данные ответа на запрос
            self.send = [] # Команды для отправки клиенту
            
            self.__thread = Thread(target=self.handleClientThreadPack, args=(self.__conn,)).start() # Запускаем в новом потоке проверку действий игрока
            
        def __jsonFixError(self):
            self.__data="["+self.__data.decode('utf-8')+"]"
            i = 2
            while i<len(self.__data)-1:
                if self.__data[i]=="}" and self.__data[i+1]=="{":
                    self.__data=self.__data[:i+1]+","+self.__data[(i+1):]
                    i+=3
                else:
                    i+=1
            
        def handleClientThreadPack(self, conn): 
            while True:
                try:
                    self.__data = self.__conn.recv(1024) # ждем запросов от клиента                    
                    if not self.__data: # если запросы перестали поступать, то ждём несколько итераций
                        if self.__waiting>10:
                            
                            self.__thread = 0# если вышел или выкинуло с сервера - поток off
                            return
                        
                        else:
                            self.__waiting += 1
                    else:
                        self.__waiting = 0

                    self.__jsonFixError() # Исправляем ошибки

                    # загружаем данные в json формате
                    self.__data = json.loads(self.__data)
                    

                    # запрос на получение с сервера
                    for d in self.__data:
                        cmd = d["request"]
                        if cmd == "get_objects": # Запрос данных
                            
                            answer_to_objects = self.__parent.objects
                            #print(answer_to_objects)
                            self.__conn.sendall(bytes(json.dumps({"request": "set_objects", "response": answer_to_objects}), 'UTF-8'))
                        elif cmd == "move":
                            self.__parent.newCommands.append({"command":"move","move":d["move"],"id":self.id})

                    for s in self.send: # Проверяем, нужно ли что-то сообщить клиенту
                        self.__conn.sendall(bytes(json.dumps(s), 'UTF-8'))
                    self.send.clear()
                    
                except Exception as e:
                    print(e)

    def __listen(self):
        while True:
            if True:##not len(self.__players) >= self.__max_players: # проверяем не превышен ли лимит
                # одобряем подключение, получаем взамен адрес и другую информацию о клиенте
                conn, addr = self.__sock.accept()
                b = True ## нужно ли создавать новый объект клиент-обработчика
                print("New connection", addr)
                print("conn", conn)

                # Цикл и условный оператор отвечают за переподключение игрока и
                # подключение нового игрока к серверу с созданием потока обработки
                for i in self.__players:
                    if i.addr[0] == addr[0]:
                        if not(i.thread):
                            b = False
                            i.addr = addr
                            i.conn = conn
                            i.thread = Thread(target=i.handleClientThreadPack, args=(conn,)).start() # Запускаем в новом потоке проверку действий игрока
                    
                if b:
                    newpack = self.__ClientThreadPack(self,conn,addr,len(self.__players))
                    self.__players.append(newpack)# добавляем его в массив игроков
                    self.newCommands.append({"command":"newcomer","id":newpack.id})


if __name__ == "__main__":
    
    print("input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)

    server = Server((HOST, PORT))
