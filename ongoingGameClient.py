import pygame
from ongoingGameServer import OngoingGameServer
#from ongoingGameWindow import OngoingGameWindow
from client import Client
import socket
from threading import Thread

class OngoingGameClient:

    def __init__(self, addr, join=False, screen=False):
 
        pygame.init() # Инициализируем pygame

        if not(screen):
            self.screen = pygame.display.set_mode((800, 600)) # Создаем окно с разрешением 800x600
        else:
            self.screen = screen
        
        self.objects = {"squares":[],
                        "abilities":[],
                        "currentMove":[],
                        "playersController":[],
                        "playersId":[],
                        }
        # Создаем словарь для хранения данных об объектах
        
        self.joined = join # Нужен ли сервер, False - синглплеер, True - мультиплеер
        
        self.serverAdress = addr
        if join: # Подключаемся
            self.serverObject = 0
        else: # Или создаём сервер
            self.serverObject = OngoingGameServer(addr)
            
        self.clientObject = Client(addr) # Создаём клиент
        
        Thread(target=self.infiniteLoop).start()
        # Делаем новый поток с циклом, в которoм берем данные об игроках

    def infiniteLoop(self):
        
        
        while True:
            pygame.time.delay(2)
            
                      


if __name__ == "__main__":
     
    print("game input host adress (it uses localhost if left empty)")
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)
            
    ongoingGameClient = OngoingGameClient((HOST, PORT),join=False) # Создаем объект клиента
