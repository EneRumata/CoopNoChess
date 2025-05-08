from random import randrange as randomInt
from os import path as filePath

import pygame
from threading import Thread
import json
from os import path as filePath

class noChessAiSimple:
    
    def __init__(self, desk, pieces, moves, teams = [[0,1,4],[0,1,4],[2,3,4],[2,3,4]]):
        self.createMoves(moves) # Создаёт очередь ходов
        self.createPlayers(teams) # Создаёт игроков
        self.createDesk(desk) # Сохраняет данные доски
        self.createPieces(pieces) # Создаёт и добавляет на доску фигуры
        
        #self.getMove()
        
    def rebuildInit(self, desk, pieces, moves, teams = [[0,1,4],[0,1,4],[2,3,4],[2,3,4]]):
        return True

    #def getMove()
    ########################################################################
    ########################################################################
    
    def createMoves(self, moves):
        self.cMove = moves[0]
        self.allMoves = moves[1].copy
        return True
        
    def createPlayers(self, teams):
        self.players = []
        for p in teams:
            self.players.append({"AI":True, # ИИ ли игрок
                                 "team":p, # Союзники
                                 "valrange":0, # В каком диапозоне лучших значений будет ход
                                 "eye":0, # Дальность расчёта ходов
                                 "evalfunc":0 # Функция определения выгоды позиции
                                 })
        return True

    def createDesk(self, desk):
        self.desk = (desk[0],desk[1])
        self.index = []
        for h in range(desk[1]):
            self.index.append([])
            for w in range(desk[0]):
                self.index[h].append(-1)
        return True

    def createPieces(self, pieces):
        self.pieces = []
        for p in pieces:
            if p["alive"]:
                h = p["index"]//self.desk[0]
                w = p["index"]%self.desk[0]
                self.index[h][w]=p.id
            self.pieces.append({"id":p["id"],# 0
                                "ownerid":p["ownerid"], # 1
                                "alive":p["alive"], # 2
                                "ptid":p["ptid"], # 3
                                "oldptid":p["oldptid"], # 4
                                "index":p["index"], # 5
                                "ability":p["ability"], # 6
                                "lastmove":p["lastmove"], # 7
                                "pawndirection":p["pawndirection"] # 8
                                })
        return True

    ########################################################################
    ########################################################################

    #
    ##
    ###
    ####
    #####
    ######

    def setPlayerAiState(self,pid,AI=-1,valrange=-1,eye=-1,evalfunc=-1):
        if type(AI)==bool:
            self.players[pid]["AI"] = AI
        if type(valrange)==int and valrange>0:
            self.players[pid]["valrange"] = valrange
        if type(eye)==int and eye>0:
            self.players[pid]["eye"] = eye
        if type(evalfunc)!=-1:
            self.players[pid]["evalfunc"] = evalfunc

    #def addMove(self,move):
        #(piecetype,index1,index2) = move
        #

    ######
    #####
    ####
    ###
    ##
    #


        
















        
