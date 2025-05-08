# Globals
movesDeskVar = (0,0)
movesTeamsVar = ()

def setBoard(w,h):
    global movesDeskVar
    movesDeskVar = (w,h)
    return True

def movesDesk(i):
    global movesDeskVar
    return movesDeskVar[i]

def setTeams(t):
    global movesTeamsVar
    movesTeamsVar = t.copy()
    return True

def movesTeams(i):
    global movesTeamsVar
    return movesDeskVar[i]

def isPointAtBoard(h,w):
    return h>=0 and h<movesDesk(1) and w>=0 and w<movesDesk(0)

def isPointEmpty(h,w,index):
    return isPointAtBoard(h,w) and index[h][w]<0
    
def isIndexEmpty(i,index): # For index and not h,w
    return i>=0 and i<movesDeskVar[0]*movesDeskVar[1] and index[i//movesDesk(0)][i%movesDesk(0)]<0
    
def isPointTaken(h,w,index):
    return isPointAtBoard(h,w) and index[h][w]>=0
    
def isPointTakenAlly(h,w,index,pieces,mover):
    return isPointTaken(h,w,index) and (pieces[index[h][w]]["ownerid"] in movesTeams(mover["ownerid"]))
    
def isPointTakenEnemy(h,w,index,pieces,mover):
    return isPointTaken(h,w,index) and not(pieces[index[h][w]]["ownerid"] in movesTeams(mover["ownerid"]))

def isPointEmptyOrTakenEnemy(h,w,index,pieces,mover):
    return isPointEmpty(h,w,index) or not(pieces[index[h][w]]["ownerid"] in movesTeams(mover["ownerid"]))

#########################################################
###   getMoves
#########################################################

def getPiecesMoves(pieces,index,pid):
    ###
    piecemoves = []
    for p in pieces:
        if p["ownerid"]==pid and p["alive"]==True:
            piecemoves.extend(getSinglePieceMoves(p,pieces,index,pid))
    return piecemoves

def getSinglePieceMoves(mover,pieces,index,pid):
    if p["ptid"] == 0:
        return getPawnMoves(mover,pieces,index,pid)
    elif p["ptid"] == 1:
        return getRockMoves(mover,pieces,index,pid)
    elif p["ptid"] == 2:
        return getKnightMoves(mover,pieces,index,pid)
    elif p["ptid"] == 3:
        return getBishopMoves(mover,pieces,index,pid)
    elif p["ptid"] == 4:
        return getQueenMoves(mover,pieces,index,pid)
    elif p["ptid"] == 5:
        return getKingMoves(mover,pieces,index,pid)
    elif p["ptid"] == 6:
        return getRamMoves(mover,pieces,index,pid)
    elif p["ptid"] == 7:
        return getBeeMoves(mover,pieces,index,pid)
    print("wtf, getSinglePieceMoves")
    return []

def addPromotions(index1,index2,ability): # Вспомогательная функция
    return [[index1,index2,ability,1], # 0 и 6 - пешка и таран
            [index1,index2,ability,2],
            [index1,index2,ability,3],
            [index1,index2,ability,4],
            [index1,index2,ability,5],
            [index1,index2,ability,7]
            ]

def getPawnMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)

    if mover["pawndirection"]: # Пешка направлена вверх
        ###
        if isPointEmpty(h+1,w,index): # Вверх на 1
            if h+1==movesDesk(1)-1:
                avmoves.extend(addPromotions([mover["id"],mover["index"]+movesDesk(0),False]))
            else:
                avmoves.append([mover["id"],mover["index"]+movesDesk(0),False])
            if isPointEmpty(h+2,w,index): # Вверх на 2
                if h+2==movesDesk(1)-1:
                    avmoves.extend(addPromotions([mover["id"],mover["index"]+movesDesk(0)*2,False]))
                else:
                    avmoves.append([mover["id"],mover["index"]+movesDesk(0)*2,False])
        if isPointTakenEnemy(h+1,w-1,index,pieces,mover): # Вверх влево
            if h+1==movesDesk(1)-1:
                avmoves.extend(addPromotions([mover["id"],mover["index"]+movesDesk(0)-1,False]))
            else:
                avmoves.append([mover["id"],mover["index"]+movesDesk(0)-1,False])
        if isPointTakenEnemy(h+1,w+1,index,pieces,mover): # Вверх вправо
            if h+1==movesDesk(1)-1:
                avmoves.extend(addPromotions([mover["id"],mover["index"]+movesDesk(0)+1,False]))
            else:
                avmoves.append([mover["id"],mover["index"]+movesDesk(0)+1,False])
        ###
    else: # Вниз
        ###
        if isPointEmpty(h-1,w,index): # Вниз на 1
            if h-1==0:
                avmoves.extend(addPromotions([mover["id"],mover["index"]-movesDesk(0),False]))
            else:
                avmoves.append([mover["id"],mover["index"]-movesDesk(0,False)])
            if isPointEmpty(h-2,w,index): # Вниз на 2
                if h-2==0:
                    avmoves.extend(addPromotions([mover["id"],mover["index"]-movesDesk(0)*2,False]))
                else:
                    avmoves.append([mover["id"],mover["index"]-movesDesk(0)*2,False])
        if isPointTakenEnemy(h-1,w-1,index,pieces,mover): # Вниз влево
            if h-1==0:
                avmoves.extend(addPromotions([mover["id"],mover["index"]-movesDesk(0)-1,False]))
            else:
                avmoves.append([mover["id"],mover["index"]-movesDesk(0)-1,False])
        if isPointTakenEnemy(h-1,w+1,index,pieces,mover): # Вниз вправо
            if h-1==0:
                avmoves.extend(addPromotions([mover["id"],mover["index"]-movesDesk(0)+1,False]))
            else:
                avmoves.append([mover["id"],mover["index"]-movesDesk(0)+1,False])
        ###
    return avmoves

def getRockMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)

    for mults in ((-1,0),(1,0),(0,1),(0,-1)):
        a = mults[0]
        i = mults[1]
        while isPointEmpty(h+a,w+i,index): # Пустые по направлению
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
            a += mults[0]
            i += mults[1]
        if isPointTakenEnemy(h+a,w+i,index,pieces,mover): # Если последний враг
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
        elif isPointAtBoard(h+a,w+i): # Проверка чтобы избежать выхода за поле
            if mover["lastmove"]==0 and pieces[index[h+a][w+i]]["ptid"]==5 and index[h+a][w+i]["ability"]: # Если последний король
                avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
            if mover["ability"]: # Если есть способность
                a += mults[0]
                i += mults[1]
                while isPointEmpty(h+a,w+i,index): # Пустые по направлению
                    avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,True])
                    a += mults[0]
                    i += mults[1]
    return avmoves
            
def getKnightMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)
    for mults in ((2,-1),(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2)):
        a = mults[0]
        i = mults[1]
        if isPointEmptyOrTakenEnemy(h+a,w+i,index,pieces,mover):
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
        elif mover["ability"] and isPointAtBoard(h+a,w+i):
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,True])
    return avmoves

def getBishopMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)
    if mover["ability"]:
        if isPointEmpty(h,w-1,index): # Влево
            avmoves.append([mover["id"],mover["index"]-1,True])
        if isPointEmpty(h,w+1,index): # Вправо
            avmoves.append([mover["id"],mover["index"]+1,True])
        if isPointEmpty(h+1,w,index): # Вверх
            avmoves.append([mover["id"],mover["index"]+movesDesk(0),True])
        if isPointEmpty(h-1,w,index): # Вниз
            avmoves.append([mover["id"],mover["index"]-movesDesk(0),True])
    for mults in ([-1,-1],[1,-1],[1,1],[-1,1]):
        a = mults[0]
        i = mults[1]
        while isPointEmpty(h+a,w+i,index): # Пустые по направлению
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
            a += mults[0]
            i += mults[1]
        if isPointTakenEnemy(h+a,w+i,index,pieces,mover): # Если последний враг
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
    return avmoves

def getQueenMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)
    for mults in ((-1,0),(1,0),(0,1),(0,-1),(-1,-1),(1,-1),(1,1),(-1,1)):
        a = mults[0]
        i = mults[1]
        while isPointEmpty(h+a,w+i,index): # Пустые по направлению
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
            a += mults[0]
            i += mults[1]
        if isPointTakenEnemy(h+a,w+i,index,pieces,mover): # Если последний враг
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
        elif isPointAtBoard(h+a,w+i) and mover["ability"]: # Проверка чтобы избежать выхода за поле
            avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,True])
    return avmoves

def getKingMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)
    if isPointEmptyOrTakenEnemy(h,w-1,index,pieces,mover): # Влево
        avmoves.append([mover["id"],mover["index"]-1,False])
    if isPointEmptyOrTakenEnemy(h,w+1,index,pieces,mover): # Вправо
        avmoves.append([mover["id"],mover["index"]+1,False])
    if isPointEmptyOrTakenEnemy(h+1,w,index,pieces,mover): # Вверх
        avmoves.append([mover["id"],mover["index"]+movesDesk(0),False])
    if isPointEmptyOrTakenEnemy(h-1,w,index,pieces,mover): # Вниз
        avmoves.append([mover["id"],mover["index"]-movesDesk(0),False])
    if isPointEmptyOrTakenEnemy(h+1,w-1,index,pieces,mover): # Вверх - Влево
        avmoves.append([mover["id"],mover["index"]+movesDesk(0)-1,False])
    if isPointEmptyOrTakenEnemy(h+1,w+1,index,pieces,mover): # Вверх - Вправо
        avmoves.append([mover["id"],mover["index"]+movesDesk(0)+1,False])
    if isPointEmptyOrTakenEnemy(h-1,w-1,index,pieces,mover): # Вниз - Влево
        avmoves.append([mover["id"],mover["index"]-movesDesk(0)-1,False])
    if isPointEmptyOrTakenEnemy(h-1,w+1,index,pieces,mover): # Вниз - Вправо
        avmoves.append([mover["id"],mover["index"]-movesDesk(0)+1,False])
    if mover["ability"]: # Если есть способность
        for mults in ((-1,0),(1,0),(0,1),(0,-1)):
            throught1square = False
            a = mults[0]
            i = mults[1]
            while isPointEmpty(h+a,w+i,index): # Пустые по направлению
                throught1square = True
                a += mults[0]
                i += mults[1]
            if isPointTakenAlly(h+a,w+i,index,pieces,mover): # Если союзник
                p = pieces[index[h+a][w+i]]
                if p["ptid"]==1 and p["lastmove"]==0: # Если союзная ладья
                    if throught1square:
                        avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,True])
                    elif isPointEmpty(h+a+mults[0],w+i+mults[1],index):
                        avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,True])
                        
    return avmoves

def getRamMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)
    if isPointEmpty(h,w-1,index): # Влево
        avmoves.append([mover["id"],mover["index"]-1,True])
    if isPointEmpty(h,w+1,index): # Вправо
        avmoves.append([mover["id"],mover["index"]+1,True])
    if mover["pawndirection"]:
        if isPointEmptyOrTakenEnemy(h+1,w,index,pieces,mover): # Вверх
            if h+1==movesDesk(1)-1:
                avmoves.extend(addPromotions([mover["id"],mover["index"]+movesDesk(0),False]))
            else:
                avmoves.append([mover["id"],mover["index"]+movesDesk(0),False])
    else:
        if isPointEmptyOrTakenEnemy(h-1,w,index,pieces,mover): # Вниз
            if h-1==0:
                avmoves.extend(addPromotions([mover["id"],mover["index"]-movesDesk(0),False]))
            else:
                avmoves.append([mover["id"],mover["index"]-movesDesk(0),False])
    return avmoves

def getBeeMoves(mover,pieces,index,pid):
    avmoves = []
    h = mover["index"]//movesDesk(0)
    w = mover["index"]%movesDesk(0)
    if mover["ability"]:
        if isPointEmpty(h,w-1,index): # Влево
            avmoves.append([mover["id"],mover["index"]-1,True])
        if isPointEmpty(h,w+1,index): # Вправо
            avmoves.append([mover["id"],mover["index"]+1,True])
        if isPointEmpty(h+1,w,index): # Вверх
            avmoves.append([mover["id"],mover["index"]+movesDesk(0),True])
        if isPointEmpty(h-1,w,index): # Вниз
            avmoves.append([mover["id"],mover["index"]-movesDesk(0),True])
    if isPointEmpty(h+a,w-i,index): # Вверх - Влево
        avmoves.append([mover["id"],mover["index"]+movesDesk(0)-1,False])
    if isPointEmpty(h+a,w+i,index): # Вверх - Вправо
        avmoves.append([mover["id"],mover["index"]+movesDesk(0)+1,False])
    if isPointEmpty(h-a,w-i,index): # Вниз - Влево
        avmoves.append([mover["id"],mover["index"]-movesDesk(0)-1,False])
    if isPointEmpty(h-a,w+i,index): # Вниз - Вправо
        avmoves.append([mover["id"],mover["index"]-movesDesk(0)+1,False])
    for mults in ([-1,-1],[1,-1],[1,1],[-1,1]):
        a = mults[0]
        i = mults[1]
        while isPointEmpty(h+a,w+i,index): # Пустые по направлению
            a += mults[0]
            i += mults[1]
            if isPointTakenEnemy(h+a,w+i,index,pieces,mover): # Если последний враг
                a += mults[0]
                i += mults[1]
                while isPointEmpty(h+a,w+i,index): # Пустые по направлению
                    a += mults[0]
                    i += mults[1]
                if isPointTakenEnemy(h+a,w+i,index,pieces,mover): # Если последний враг
                    avmoves.append([mover["id"],mover["index"]+a*movesDesk(0)+i,False])
    return avmoves

#########################################################
###   getMoves
#########################################################


#########################################################
###   setMoves
#########################################################

def setPieceMove(pieces, index, move):
    ### type     int     int      bool      int
    ### move = [moverid, dest, ability, promotion]
    ### or     [moverid, dest, ability]
    if len(move)>2:
        (moverid, dest, ability, promotion) = move
    else:
        (moverid, dest, ability) = move
        promotion = -1
    return tryPieceMove(pieces, index, moverid, dest, ability, promotion)

def tryPieceMove(pieces, index, moverid, dest, ability, promotion):
    if p["ptid"] == 0:
        return tryPawnMove(pieces, index, moverid, dest, ability, promotion)
    elif p["ptid"] == 1:
        return tryRockMove(pieces, index, moverid, dest, ability, promotion)
    elif p["ptid"] == 2:
        return tryKnightMove(pieces, index, moverid, dest, ability, promotion)
    elif p["ptid"] == 3:
        return tryBishopMove(pieces, index, moverid, dest, ability, promotion)
    elif p["ptid"] == 4:
        return tryQueenMove(pieces, index, moverid, dest, ability, promotion)
    elif p["ptid"] == 5:
        return tryKingMove(pieces, index, moverid, dest, ability, promotion)
    elif p["ptid"] == 6:
        return tryRamMove(pieces, index, moverid, dest, ability, promotion)
    elif p["ptid"] == 7:
        return tryBeeMove(pieces, index, moverid, dest, ability, promotion)
    print("wtf, tryPieceMove")
    return False

def captureOrMove(pieces, index, moverid, dest): # Вспомогательная функция
    h = dest//movesDesk(0)
    w = dest%movesDesk(0)
    if isPointTaken(h,w,index): # Если клетка занята
        pieces[index[h][w]]["alive"]=False # Убиваем прошлую фигуру на целевой клетке
    elif not(isPointAtBoard(h,w)):
        return False
    index[h][w] = moverid # Записываем ID фигуры в новую клетку
    h = pieces[moverid]["index"]//movesDesk(0)
    w = pieces[moverid]["index"]%movesDesk(0)
    index[h][w].clear() # Удаляем ID фигуры из старой клетки
    pieces[moverid]["index"] = dest # Обновляем индекс клетки у фигуры
    return True

def tryPawnMove(pieces, index, moverid, dest, ability, promotion):
    if captureOrMove(pieces, index, moverid, dest): # Пробуем подвинуть фигуру
        if promotion>0:
            pieces[moverid]["ptid"]=promotion # И меняем её тип
        pieces[moverid]["ability"]=False # В любом случае удаляем способность
        return True
    return False

def tryRockMove(pieces, index, moverid, dest, ability, promotion):
    if isPointTakenAlly(dest//movesDesk(0),dest%movesDesk(0), index , pieces, pieces[moverid]):
        return tryKingMove(pieces, index, index[dest//movesDesk(0)][dest%movesDesk(0)], pieces[moverid]["index"], promotion)
    else:
        if captureOrMove(pieces, index, moverid, dest): # Пробуем подвинуть фигуру
            if ability:
                pieces[moverid]["ability"]=False # Используем способность, если нужно
            return True
    return False

def tryKnightMove(pieces, index, moverid, dest, ability, promotion):
    if isPointTakenAlly(dest//movesDesk(0),dest%movesDesk(0), index , pieces, pieces[moverid]):
        ### Свапаем фигуры
        mh = pieces[moverid]["index"]//movesDesk(0)
        mw = pieces[moverid]["index"]%movesDesk(0)
        h = dest//movesDesk(0)
        w = dest%movesDesk(0)
        pieces[index[h][w]]["index"] = pieces[moverid]["index"] # Меняем координату свапаемой фигуры на координату коня
        pieces[moverid]["index"] = dest # Меняем координату коня
        index[h][w].clear() # Меняем фигуру на доске в точке dest
        index[h][w].append(moverid)
        index[dh][dw].clear() # Меняем фигуру на доске в начальной точке коня
        index[dh][dw].append(index[h][w])
        ###
        pieces[moverid]["ability"]=False # Используем способность
        return True
    else:
        return captureOrMove(pieces, index, moverid, dest) # Пробуем подвинуть фигуру
    return False

def tryBishopMove(pieces, index, moverid, dest, ability, promotion):
    if captureOrMove(pieces, index, moverid, dest): # Пробуем подвинуть фигуру
        if ability:
            pieces[moverid]["ability"]=False # Используем способность, если нужно
        return True
    return False

def tryQueenMove(pieces, index, moverid, dest, ability, promotion):
    return captureOrMove(pieces, index, moverid, dest)

def tryKingMove(pieces, index, moverid, dest, ability, promotion):
    if isPointTakenAlly(dest//movesDesk(0),dest%movesDesk(0), index , pieces, pieces[moverid]):
        # Рокировка
        dif = dest - pieces[moverid]["index"]
        if dif >= movesDesk(0): # Вычисляем направление рокировки
            if dif >0:
                mult = movesDesk(0) # Вверх
            else:
                mult = -movesDesk(0) # Вниз
        else:
            if dif >0:
                mult = 1 # Вправо
            else:
                mult = -1 # Влево
        oldind = pieces[moverid]["index"] # Старый индекс короля
        # Двигаем ладью, если ещё не стоит вплотную
        if dest != oldind+mult:
            index[(oldind+mult)//movesDesk(0)][(oldind+mult)%movesDesk(0)] = index[dest//movesDesk(0)][dest%movesDesk(0)]
            pieces[index[dest//movesDesk(0)][dest%movesDesk(0)]]["index"] = oldind+mult
            index[dest//movesDesk(0)][dest%movesDesk(0)] = -1
        # Двигаем короля
        index[(oldind+mult*2)//movesDesk(0)][(oldind+mult*2)%movesDesk(0)] = index[oldind//movesDesk(0)][oldind%movesDesk(0)]
        pieces[moverid]["index"] = oldind+mult*2
        index[oldind//movesDesk(0)][oldind%movesDesk(0)] = -1
        return True
    else:
        return captureOrMove(pieces, index, moverid, dest)
    return False

def tryRamMove(pieces, index, moverid, dest, ability, promotion):
    if captureOrMove(pieces, index, moverid, dest): # Пробуем подвинуть фигуру
        if promotion>0:
            pieces[moverid]["ptid"]=promotion # И меняем её тип
        if ability:
            pieces[moverid]["ability"]=False # Используем способность, если нужно
        return True
    return False

def tryBeeMove(pieces, index, moverid, dest, ability, promotion):
    if captureOrMove(pieces, index, moverid, dest): # Пробуем подвинуть фигуру
        if ability:
            pieces[moverid]["ability"]=False # Используем способность, если нужно
        return True
    return False






    
