import socket
from threading import Thread
import json

class Server:

    def __init__(self, addr, max_conn=999):

        self.newCommands = [] # Новые команды для оболочки игры-сервера
        self.data = "" # Сообщение от последнего клиента
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(addr) # запускаем сервер от заданного адреса

        self.players = [] # создаем массив данных игроков на сервере
        
        self.max_players = max_conn # максимум людей на сервере
        self.sock.listen(self.max_players) # устанавливаем максимальное
        # кол-во прослушиваний на сервере (пока не используется)
        
        #self.listen() # вызываем цикл, который отслеживает подключения к серверу
        Thread(target=self.listen).start() # Запускаем в новом потоке проверку действий игрока
        
    class ClientThreadPack:
        def __init__(self, player_parent_object, player_conn, player_addr, player_id):
            self.parent = player_parent_object
            self.conn = player_conn
            self.addr = player_addr
            self.id = player_id
            self.waiting = 0 # Кол-во ожиданий ответа до дисконнекта
            self.data = 0 # Данные ответа на запрос
            
            self.thread = Thread(target=self.handleClientThreadPack, args=(self.conn,)).start() # Запускаем в новом потоке проверку действий игрока

        def jsonFixError(self):
            self.data="["+self.data.decode('utf-8')+"]"
            i = 2
            while i<len(self.data)-1:
                if self.data[i]=="}" and self.data[i+1]=="{":
                    self.data=self.data[:i+1]+","+self.data[(i+1):]
                    i+=3
                else:
                    i+=1
            
        def handleClientThreadPack(self, conn): 
            while True:
                try:
                    self.data = self.conn.recv(1024) # ждем запросов от клиента
                    self.jsonFixError() # Исправляем ошибки
                    
                    if not self.data: # если запросы перестали поступать, то ждём несколько итераций
                        if self.waiting>10:
                            
                            self.thread = 0# если вышел или выкинуло с сервера - поток off
                            return
                        
                        else:
                            self.waiting += 1
                    else:
                        self.waiting = 0

                    # загружаем данные в json формате
                    self.data = json.loads(self.data)
                    

                    # запрос на получение с сервера
                    for d in self.data:
                        if d["request"] == "get_objects": # Запрос данных
                            
                            answer_to_objects = {"squares":self.parent.objects["squares"],
                                                 "abilities":self.parent.objects["abilities"],
                                                 "currentMove":self.parent.objects["currentMove"],
                                                 }
                            self.conn.sendall(bytes(json.dumps({"response": answer_to_objects}), 'UTF-8'))

                        # движение
                        if d["request"] == "move":
                            self.newCommands.append((d["request"],d["move"]))
                            
                except Exception as e:
                    print(e)

    def listen(self):
        while True:
            if True:##not len(self.players) >= self.max_players: # проверяем не превышен ли лимит
                # одобряем подключение, получаем взамен адрес и другую информацию о клиенте
                conn, addr = self.sock.accept()
                b = True ## нужно ли создавать новый объект клиент-обработчика
                print("New connection", addr)
                print("conn", conn)

                # Цикл и условный оператор отвечают за переподключение игрока и
                # подключение нового игрока к серверу с созданием потока обработки
                for i in self.players:
                    if i.addr[0] == addr[0]:
                        if not(i.thread):
                            b = False
                            i.addr = addr
                            i.conn = conn
                            i.thread = Thread(target=i.handleClientThreadPack, args=(conn,)).start() # Запускаем в новом потоке проверку действий игрока
                    
                if b:
                    self.players.append(self.ClientThreadPack(self.players,conn,addr,len(self.players)))# добавляем его в массив игроков


if __name__ == "__main__":
    
    print("input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)

    server = Server((HOST, PORT))
