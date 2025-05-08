import pygame
from ongoingGameServer import OngoingGameServer
from ongoingGameClient import OngoingGameClient
from threading import Thread

class OngoingGameWindow():
    def __init__(self, screen):
        if not(screen):
            self.screen=pygame.display.set_mode((800,600))
            self.screen.set_caption("CoopNoChess")
        else:
            self.screen=pygame.Surface((512, 512))
            screen.blit(self.screen,(288,0))
            
        
    def buildDesk(self):
        
        while True:
            for event in pygame.event.get():
                # Перебираем все события которые произошли с программой
                if event.type == pygame.QUIT: # Проверяем на выход из игры
                    self.clientObject.conn.close()
                    if not(self.joined):
                        self.serverObject.sock.close()
                    exit()
                    
            pygame.time.delay(2)
            
    def infiniteLoop(self):
        
        
        while True:
            for event in pygame.event.get():
                # Перебираем все события которые произошли с программой
                if event.type == pygame.QUIT: # Проверяем на выход из игры
                    self.clientObject.conn.close()
                    if not(self.joined):
                        self.serverObject.sock.close()
                    exit()
                    
            pygame.time.delay(2)
            

if __name__ == "__main__":
    print("game input host adress (it uses localhost if left empty)")
    #HOST = input()# Адрес сервера
    #HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    #PORT = input()# Порт сервера
    #PORT = 8080 if PORT=="" else int(PORT)
    HOST = "localhost"
    PORT = 8080

    myWindow=pygame.display.set_mode((800,600))
    MyOngoingGameWindow = OngoingGameWindow(screen=myWindow)
    # Создаем объект клиента

    MyOngoingGameClient = OngoingGameClient((HOST, PORT),join=False)
    # Создаем объект клиента

    

     
