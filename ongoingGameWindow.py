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
                
        # Загружаем спрайты

        # imagePath: пути к папкам со спрайтами
        # playersColorsPath: пути цветов игроков
        # piecetypes: типы фигур
        # squarelist: список клеток доски
        # pieceimglist и piecerectlist: рисунки и поверхности всех фигур
        self.imagePath = {"desktop":"sprites\\desk",
                          "interface":"sprites\\interface",
                          "pieces":"sprites\\pieces"}
        self.playersColorsPath = ("grey",
                                  "red",
                                  "green",
                                  "purple",
                                  "brown",
                                  "blue")
        self.piecetypes = ("lesserPawn","pawn",
                           "lesserRock","rock",
                           "lesserKnight","knight",
                           "lesserBishop","bishop",
                           "queen","king")

        t = 0
        self.squarelist = []
        for i in range(10):
            self.squarelist.append([])
            for n in range(4):
                self.squarelist[t].append(pygame.image.load(self.imagePath["desktop"]+"\\"+"squareWhite"+".png"))#.convert_alpha()
                self.squarelist[t].append(pygame.image.load(self.imagePath["desktop"]+"\\"+"squareBlack"+".png"))
            t+=1
            self.squarelist.append([])
            for n in range(10):
                self.squarelist[t].append(pygame.image.load(self.imagePath["desktop"]+"\\"+"squareBlack"+".png"))
                self.squarelist[t].append(pygame.image.load(self.imagePath["desktop"]+"\\"+"squareWhite"+".png"))
            t+=1
            
        t = 0
        self.pieceimglist = []
        self.piecerectlist = []
        for i in self.playersColorsPath:
            self.pieceimglist.append({})
            self.piecerectlist.append({})
            for n in self.piecetypes:
                self.pieceimglist[t][n]=pygame.image.load(self.imagePath["pieces"]+"\\"+i+"\\"+n+".png")
                self.piecerectlist[t][n]=self.pieceimglist[t][n].get_rect()
            t+=1

        
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
    HOST = input()# Адрес сервера
    HOST = "localhost" if HOST=="" else HOST
    print("game input host port (it uses 8080 if left empty)")
    PORT = input()# Порт сервера
    PORT = 8080 if PORT=="" else int(PORT)

    myWindow=pygame.display.set_mode((800,600))
    MyOngoingGameWindow = OngoingGameWindow(screen=myWindow)
    # Создаем объект клиента

    MyOngoingGameClient = OngoingGameClient((HOST, PORT),join=False,screen=MyOngoingGameWindow.screen)
    # Создаем объект клиента

    

     
