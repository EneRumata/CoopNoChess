import pygame
import json

from sys import exit as endWindow
from os import path as filePath
from random import randrange as randomInt

global lastobjid # ID последнего объекта
global sharedfont # Шрифт по умолчанию
global mainobject # Основной слой для окна программы
global menudata # Параметры окна-меню
global ticButtons # Автовыключаемые кнопки
global intevents # События интерфейса
global currentSelection # Выбранный выпадающий список (или текстовая кнопка)
global localization # Файл с текстом подсказок и тп

class mainProgramWindow:
    def __init__(self):
        global lastobjid
        global sharedfont
        global mainobject
        global menudata
        global ticButtons
        global intevents
        global currentSelection
        global localization
        currentSelection = {}
        ticButtons = []
        lastobjid = -1
        
        pygame.init()
        pygame.display.set_caption('coopNoChess')
        
        # Загружаем json файлы и настраиваем окно
        self.jsonPref = {}
        self.jsonPref["player"] = self.loadJSON("json\\properties\\player")["pref"]
        self.jsonPref["window"] = self.loadJSON("json\\properties\\window")["resolution"][self.jsonPref["player"]["resolution"]]
        print("self.jsonPref['window'] is "+str(self.jsonPref["window"]))
        self.jsonPref["pNames"] = self.loadJSON("json\\interface\\randomNames")["names"]
        self.jsonPref["pColors"] = self.loadJSON("json\\interface\\playerColors")["colors"]
        self.jsonPref["wColors"] = self.loadJSON("json\\interface\\windowColors")["colors"]
        self.jsonPref["menu"] = self.loadJSON("json\\interface\\menu")["elements"]
        self.jsonPref["levels"] = self.loadJSON("json\\game\\levels")["levels"]
        self.jsonPref["types"] = self.loadJSON("json\\game\\types")["types"]
        self.jsonPref["localization"] = self.loadJSON("json\\interface\\stringsAndNames")
        # Загружаем текст в глобальную переменную
        localization = self.jsonPref["localization"]
                    
        ### НАСТРОЙКИ ОТОБРАЖЕНИЯ
        
        # Шрифт
        sharedfont = {}
        sharedfont["font"] = pygame.font.Font(self.jsonPref["window"]["font"], self.jsonPref["window"]["fontScale"])
        sharedfont["offset"] = self.jsonPref["window"]["fontOffset"]
        #print(sharedfont)

        # Окно игры
        self.mainWindow = pygame.display.set_mode(self.jsonPref["window"]["resolution"])

        # Создаём меню игры
        handevents = [] # События ввода пользователем 
        intevents = [] # События работы интерфейса
        
        self.objects = self.createMenuObjects()
        mainobject = self.objects["background"] # Основной слой игры
        
        currentSelection["menulayer"] = False # Текущий элемент на экране
        currentSelection["halfmenu"] = self.objects["playmenu"]
        currentSelection["OBJECT"] = False

        # Основный цикл игры
        menudata = [self.objects,
                    self.jsonPref["window"]["buttonwidth"],
                    self.jsonPref["window"]["buttonheight"],
                    self.jsonPref["window"]["offset"],
                    self.jsonPref["window"]["resolution"],
                    self.jsonPref["wColors"][self.jsonPref["window"]["wColor"]]]
        (objects, w, h, f, r, c) = menudata
        clock = pygame.time.Clock()
        is_running = True
        
        # Переключалка в полноэкранный
        #pygame.display.toggle_fullscreen()
        # Переключалка в окно без рамки
        #pygame.display.set_mode(self.jsonPref["window"]["resolution"],pygame.NOFRAME)
        
        while is_running:
            #time_delta = clock.tick(60)/1000.0

            self.ticForButtons()
            for event in pygame.event.get(): # Запоминаем события ввода пользователя перед изменением состояния меню 
                if event.type == pygame.QUIT:
                    is_running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if mainobject.collidepoint(event.pos):
                        target = self.recForInChilds(mainobject, event.pos)
                        if target:
                            #print(str(type(target))+"''"+target.name+"'' clicked!")
                            if getSelectedDd() and target != getSelectedDd() and not(type(target) in (dropboxitem,dropboxlayer)):
                                print("!")
                                handevents.append([getSelectedDd(),"actions"]) # Очищаем выбранный объект
                            if type(target) in (button,textbox,dbutton,dropbox):
                                if not(target.disabled):
                                    handevents.append([target,"actions"])
                            elif type(target)==dropboxitem:
                                if not(target.parent.mainparent.disabled):
                                    handevents.append([target,"actions"])

            for event in handevents: # Для каждого события ввода пользователя запускаем обработку, которая
                target = event[0] # Которая сама добавил в глобальную переменную события изменений интерфейса
                b = False
                #print('interface event is '+target.name+" "+str(event[1:]))
                if type(target) in (button,dropbox,textbox,dbutton,dropboxitem):
                    act = event[1]
                    if act == "actions":
                        b = target.actions()

                if b and target.changeSizeOnAct and target.parent:
                    target.parent.updateColorPointAndSize()
            handevents.clear()

            event = intevents.pop() if len(intevents)>0 else False
            while event: # Пиздец я рот ебал конкретно этой хуйни, как же я с ней намучился из-за своей тупости, просто ёбнешься
                # Цикл настоящих событий
                objects = menudata[0]
                etype = event[0]
                ttype = type(event[1])
                target = event[1]
                act = event[2]
                print('happened event is '+str(ttype)+" "+target.name+" "+str(act))
                #==============================================================================================================
                # События изменения элементов интерфейса
                if target.name == "play" and act == "activate":
                    currentSelection["menulayer"] = changeChild(objects["menulayer"],currentSelection["menulayer"],objects["halfmenu"])
                elif target.name == "newgame" and act == "activate":
                    currentSelection["halfmenu"] = changeChild(objects["halfmenu"],currentSelection["halfmenu"],objects["lobby"])
                    objects["quit"].enable()
                elif target.name == "loadgame" and act == "activate":
                    currentSelection["halfmenu"] = changeChild(objects["halfmenu"],currentSelection["halfmenu"],objects["lobby"])
                    objects["quit"].enable()
                elif target.name in ("quit","cancelgame") and act == "activate":
                    currentSelection["halfmenu"] = changeChild(objects["halfmenu"],currentSelection["halfmenu"],objects["playmenu"])
                    objects["quit"].disable()
                # 
                #==============================================================================================================
                event = intevents.pop() if len(intevents)>0 else False
                
            # Рисуем основной объект и показываем его на экране
            self.objects["background"].draw()
            self.mainWindow.blit(self.objects["background"].surf, self.objects["background"].point)
            
            # Обновить рисунок основного окна
            pygame.display.update()

        # После цикла игры
        pygame.quit()
        endWindow()

    def loadJSON(self, s): # Функция загрузки JSON файла
        path = s + ".json"
        if filePath.exists(path):
            with open(path,'r', encoding='utf-8') as file:
                try:
                    loaded = json.load(file)
                except:
                    print("json.load error, loadJSON")
                    return False
                return loaded
        else:
            print(path)
            print("Path not found, __loadJSON")
            return False
        print("wtf, __loadJSON")
        return False

    def recForInChilds(self, obj, point):
        i = len(obj.childs)-1
        while i>=0:
            b = self.recForInChilds(obj.childs[i],point)
            if b:
                return b
            i -= 1
        b = obj.collidepoint(point)
        return obj if b else False

    def createMenuObjects(self): # Создаём объекты меню
        objects = {}
        w = self.jsonPref["window"]["buttonwidth"]
        h = self.jsonPref["window"]["buttonheight"]
        f = self.jsonPref["window"]["offset"]
        r = self.jsonPref["window"]["resolution"]
        c = self.jsonPref["wColors"][self.jsonPref["window"]["wColor"]]
        
        elem = self.loadJSON("json\\interface\\menu")["elements"]
        for name in elem:
            #print("name="+name)
            obj = eval(elem[name]["createFunction"]) # Создаём объект
            objects[name] = obj # Сохраняем новый объект в словарь
            if obj.parent:
                obj.parent.childs.append(obj)
            obj.updatePoint = elem[name]["updatePoint"] # Сохраняем для него строковые функции обновления
            obj.updateSize = elem[name]["updateSize"]
            obj.updateChilds = elem[name]["updateChilds"] # Создаём список детей для запуска у них функции обновления
        return objects

    def updateMenuObjectsColorsPointsAndSizes(self, parentobject): # Обновляем цвета, точки и размеры объектов меню
        parentobject.updateColorPointAndSize(self)

    def ticForButtons(self):
        global ticButtons
        for b in ticButtons:
            b.ticForStateDrop()

def setSelectedDd(new):
    global currentSelection
    currentSelection["OBJECT"] = new
    return new

def getSelectedDd():
    global currentSelection
    return currentSelection["OBJECT"]

def changeChild(parent, old, new):
    if old:
        parent.childs.remove(old)
    parent.childs.append(new)
    parent.updateColorPointAndSize()
    return new
    
def inteventsAdd(event):
    global intevents
    intevents.append(event)
    
class image: # КАРТИНКА
    def __init__(self, size, style, colors, part=[], alpha=False, point=False, pic=False, text="", font=False, align="middle"):
        self.startpoint = point
        self.rebuildimage(size, style, colors, part=part, alpha=alpha, point=point, pic=pic, text=text, font=font, align=align)

    def applyBoundariesLayer(self, directions, distances, colornames, colors, sprite):
        w = sprite.get_width()
        h = sprite.get_height()
        for i in range(1,len(distances)-1,1):
            # i -  цвет 1, 2, 3 и
            # off - int 0, 1, 2
            off = sum(distances[(i+1):])
            bold = distances[i]
            if "top" in directions:
                temp = pygame.Surface((w,bold)) # Создаём горизонтальную поверхность
                temp.fill(colors[colornames[i]]) # Заливаем цветом i
                self.surf.blit(temp,(0,off)) # Крепим к нужной точке
            if "bottom" in directions:
                temp = pygame.Surface((w,bold)) # Создаём горизонтальную поверхность
                temp.fill(colors[colornames[i]]) # Заливаем цветом i
                self.surf.blit(temp,(0,h-1-off)) # Крепим к нужной точке
            if "left" in directions:
                temp = pygame.Surface((bold,h)) # Создаём вертикальную поверхность
                temp.fill(colors[colornames[i]]) # Заливаем цветом i
                self.surf.blit(temp,(off,0)) # Крепим к нужной точке
            if "right" in directions:
                temp = pygame.Surface((bold,h)) # Создаём вертикальную поверхность
                temp.fill(colors[colornames[i]]) # Заливаем цветом i
                self.surf.blit(temp,(w-1-off,0)) # Крепим к нужной точке
        return sprite
        
        
    def rebuildimage(self, size, style, colors, part=[], alpha=False, point=False, pic=False, text="", font=False, align="middle"):
        global sharedfont
        global localization
        self.size = size
        self.style = style
        self.colors = colors
        self.part = part
        if alpha: # Alpha
            self.alpha = alpha
        else:
            self.alpha = 255
        if self.startpoint: # Point
            self.point = self.startpoint
        else:
            self.point = [0,0]
        self.pic = pic
        self.text = text
        self.font = font
        self.align = align
        
        offset = self.colors["boundaries"]
        clr = self.colors["codes"]
        if self.style[0:-1] == "button":
            c = self.colors["map"][0+int(self.style[-1])]
        elif self.style[0:-1] == "textbox":
            c = self.colors["map"][4+int(self.style[-1])]
        elif self.style == "layer":
            c = self.colors["map"][8]
        elif self.style == "textlayer":
            c = self.colors["map"][9]
        elif self.style == "dbbutton":
            self.point[0] += self.size[0]-self.size[1] # Смещаем точку крепления слоя
            c = self.colors["map"][10]
        elif self.style == "dbitem":
            c = self.colors["map"][11]
        elif self.style == "dblayer":
            c = self.colors["map"][12]
        elif self.style == "slider":
            c = self.colors["map"][13]
        elif self.style == "slbutton":
            c = self.colors["map"][14]
        elif self.style == "dropbutton":
            c = self.colors["map"][15]
        else:
            return False


        # Создаём слой-рисунок
        if "text" in self.part:
            if font:
                f = font
            else:
                f = sharedfont
            t = localization["short"][str(text)] if text in localization["short"] else text
            self.surf = f["font"].render(t,True,clr[c[4]])
            if self.style == "dbbutton":
                self.point = ( (size[1]-self.surf.get_width())/2 + size[0] - size[1], (size[1]-self.surf.get_height())/2 )
            else:
                if align == "left":
                    self.point = ( f["offset"], (size[1]-self.surf.get_height())/2 )
                elif align == "right":
                    self.point = ( size[0]-self.surf.get_width()-f["offset"], (size[1]-self.surf.get_height())/2 )
                else:#align == "middle"
                    self.point = ( (size[0]-self.surf.get_width())/2, (size[1]-self.surf.get_height())/2 )
        else:
            (tab,w) = (size[0]-size[1],size[1]) if self.style in ("dbbutton","slbutton") else (0,size[0])
            h = size[1]
            if "empty" in self.part: # Если слой без границ
                offsumm = sum(offset)
                self.surf = pygame.Surface((size[0]-tab-offsumm*2,size[1]-offsumm*2)) # Создаём слой без границ
                self.surf.fill(clr[c[0]]) # Заливаем цветом
                self.point = [self.point[0]+offsumm,self.point[1]+offsumm] # И смещаем точку крепления слоя
            else: # Если слой с границами
                self.surf = pygame.Surface((size[0]-tab,size[1])) # Создаём слой нужного размера
                self.surf.fill(clr[c[0]]) # Заливаем цветом
                d = ["top","bottom","left","right"] if "all" in self.part else self.part # Собираем границы
                self.applyBoundariesLayer(d,offset,c,clr,self.surf) # Рисуем границы

        # Устанавливаем прозрачность слоя
        self.surf.set_alpha(self.alpha)
        
        return self.surf

class superLayer: # РОДИТЕЛЬСКИЙ СЛОЙ
    def __init__(self, name, parent, point, size):
        global lastobjid
        lastobjid += 1
        self.changeSizeOnAct = False
        self.id = lastobjid # ID объекта
        self.name = name # Имя
        self.parent = parent # Текущий родитель
        self.childs = [] # Дочерние классы
        self.point = point # Положение объекта
        self.size = size # Размеры объекта
        self.surf = pygame.Surface(size) # Поверхность
        self.surf.set_colorkey(self.surf.get_at((0,0))) # И делаем её прозрачной
        self.images = [] 
        if parent: # Область
            self.rect = pygame.Rect((parent.rect.x+point[0]),(parent.rect.y+point[1]),size[0],size[1])
        else:
            self.rect = pygame.Rect(point[0],point[1],size[0],size[1])

    def collidepoint(self, point):
        return self.rect.collidepoint(point)
        
    def draw(self):
        (x, y) = (self.parent.rect.x,self.parent.rect.y) if self.parent else (0, 0)
        if (x+self.point[0], y+self.point[1]) != (self.rect.x,self.rect.y):
            self.rect.x = x + self.point[0]
            self.rect.y = y + self.point[1]
        for im in self.images:
            self.surf.blit(im.surf,im.point)
        for ch in self.childs:
            ch.draw()
            self.surf.blit(ch.surf,ch.point)

    def updateColorPointAndSizeSelf(self):
        global menudata
        (objects, w, h, f, r, c) = menudata
        p = eval(self.updatePoint)
        s = eval(self.updateSize)
        self.point = p
        self.size = s
        self.surf = pygame.Surface(s) # Поверхность
        self.surf.set_colorkey(self.surf.get_at((0,0))) # И делаем её прозрачной
        for im in self.images:
            im.rebuildimage(s,im.style,c,im.part,im.alpha,im.startpoint,im.pic,im.text,im.font,im.align)
        if self.parent: # Область
            self.rect.x = self.parent.rect.x+self.point[0]
            self.rect.y = self.parent.rect.y+self.point[1]
        else:
            self.rect.x = self.point[0]
            self.rect.y = self.point[1]
        self.rect.width = self.size[0]
        self.rect.height = self.size[1]
        
    def updateColorPointAndSizeChilds(self):
        global menudata
        objects = menudata[0]
        for name in self.updateChilds: # Имена всех детообъектов
            #print(objects[name].name)
            objects[name].updateColorPointAndSize()
        
    def updateColorPointAndSize(self):
        self.updateColorPointAndSizeSelf()
        self.updateColorPointAndSizeChilds()
        
    def actions(self):
        return False
        
class layer(superLayer): # СЛОЙ
    def __init__(self, name, parent, colors, point, size, alpha=False, text="", style="layer", part=False):
        super().__init__(name, parent, point, size)
        self.closed = False
        self.dbut = False # Связанный объект класса кнопка сокрытия
        p = part if part!=False else ["empty"] if style=="layer" else ["all"]
        im = image(self.size,style,colors,alpha=alpha,part=p)# Слои
        self.images.append(im)
        if text!="":
            im = image(self.size,style,colors,alpha=alpha,part=["text"],text=text)
            self.images.append(im)

    def setImages(self):
        self.surf = pygame.Surface(self.size)
        for im in self.images:
            im.rebuildimage(self.size, im.style, im.colors)
            
    def close(self):
        self.closed = True
        self.point = self.allpoints[1]
        self.size = self.allsizes[1]
        self.setImages()
            
    def open(self):
        self.closed = False
        self.point = self.allpoints[0]
        self.size = self.allsizes[0]
        self.setImages()
        
    def updateColorPointAndSizeSelf(self):
        global menudata
        (objects, w, h, f, r, c) = menudata
        if self.dbut and self.dbut.state:
            p = eval(self.dbut.layHidenPoint)
            s = eval(self.dbut.layHidenSize)
        else:
            if type(self)!=dropboxlayer:
                p = eval(self.updatePoint)
            s = eval(self.updateSize)
        self.point = p
        self.size = s
        self.surf = pygame.Surface(s) # Поверхность
        if s[1]>0:
            self.surf.set_colorkey(self.surf.get_at((0,0))) # И делаем её прозрачной
        for im in self.images:
            im.rebuildimage(s,im.style,c,im.part,im.alpha,p,im.pic,im.text,im.font,im.align)
        if self.parent: # Область
            self.rect.x = self.parent.rect.x+self.point[0]
            self.rect.y = self.parent.rect.y+self.point[1]
        else:
            self.rect.x = self.point[0]
            self.rect.y = self.point[1]
        self.rect.width = self.size[0]
        self.rect.height = self.size[1]
        
class button(superLayer): # КНОПКА
    def __init__(self, name, parent, colors, point, size, stateDrop=True, disabled=False, text="", align="middle", style="button", part=["all"]):
        super().__init__(name, parent, point, size)
        self.onePerDrop = False # Не только 1 активный объект, не деактивируется от нажатия на что-то ещё
        self.disabled = disabled # Заблокирована
        self.state = False # Выбрана
        self.stateDrop = stateDrop # Одноразовая, state возвращается в False через пару игровых тиков
        self.tics = 0
        ### Слои
        self.buttonimages = [[],[],[],[]]
        self.textimages = [[],[],[],[]]
        for i in range(4):
            im = image(size,style+str(i),colors,part=part)
            self.buttonimages[i].append(im)
            im = image(size,style+str(i),colors,part=["text"],text=text,align=align)
            self.textimages[i].append(im)
        self.images.clear()
        i = 2 if self.disabled else 0
        self.images.extend(self.buttonimages[i])
        self.images.extend(self.textimages[i])
        ###
        
    def setImages(self):
        self.images.clear()
        if self.disabled:
            if self.state:
                i = 3
            else:
                i = 2
        else:
            if self.state:
                i = 1
            else:
                i = 0
        self.images.extend(self.buttonimages[i])
        self.images.extend(self.textimages[i])
    
    def disable(self):
        if not(self.disabled):
            self.disabled = True
            self.setImages()
            inteventsAdd([button,self,"disable"])
            return True
        else:
            return False
        
    def enable(self):
        if self.disabled:
            self.disabled = False
            self.setImages()
            inteventsAdd([button,self,"enable"])
            return True
        else:
            return False

    def activate(self):
        global ticButtons
        if not(self.state):
            self.state = True
            if self.stateDrop:
                self.tics = 3 # Ставим 3 кадра на деактивацию кнопки
                ticButtons.append(self) # И добавляем её в список
            self.setImages()
            if self.onePerDrop:
                setSelectedDd(self)
            inteventsAdd([button,self,"activate"])
            return True
        else:
            return False

    def deactivate(self):
        if self.state:
            self.state = False
            self.setImages()
            if self.onePerDrop:
                setSelectedDd(False)
            inteventsAdd([button,self,"deactivate"])
            return True
        else:
            return False

    def ticForStateDrop(self):
        if self.stateDrop:
            if self.tics>0:
                self.tics -= 1
            else:
                self.deactivate()

    def actions(self):
        if self.disabled:
            return False
        else:
            if self.state:
                if not(self.stateDrop):
                    return self.deactivate()
                else:
                    return False
            else:
                return self.activate()

class dropboxitem(superLayer): # ЭЛЕМЕНТ ВЫПАДАЮЩЕГО СПИСКА
    def __init__(self, name, parent, colors, point, size, text="", align="left", part=["all"]):
        super().__init__(name, parent, point, size)
        im = image(size,"dbitem",colors,part=["all"])# Слои
        self.images.append(im)
        self.text = text
        im = image(size,"dbitem",colors,part=["text"],text=text,align=align)# Слои
        self.images.append(im)
        
    def actions(self):
        p = self.parent.mainparent
        if p.disabled:
            return False
        else:
            if p.state:
                p.changeSelection(self)
                p.deactivate()
                return True
            else:
                return False

class dropboxlayer(superLayer): # СЛОЙ ВЫПАДАЮЩЕЙ ЧАСТИ ВЫПАДАЮЩЕГО СПИСКА
    def __init__(self, name, parent, colors, point, size, items, row=1, part=["all"]):
        super().__init__(name, parent, point, size)
        self.mainparent = False # Настоящий родитель
        im = image(size,"dblayer",colors,part=part)# Слои
        self.images.append(im)
        self.childs = items
        for it in items:
            it.parent = self
        self.row = row
        self.rebuildsurf()

    def rebuildsurf(self):
        l = len(self.childs)
        w = self.childs[0].size[0]
        h = self.childs[0].size[1]
        r = self.row
        for i in range(l):
            #print(self.childs[i].name+" "+str((i%r)*w)+" "+str((i//r)*h))
            self.childs[i].point = ((i%r)*w,
                          (i//r)*h
                          )
        self.rect.height = h*( ((l-1)//r) + 1 )
        self.rect.width = w*r
        self.size = (self.rect.width, self.rect.height)
        self.surf = pygame.Surface(self.size)
        for im in self.images:
            im.rebuildimage(self.size, im.style, im.colors)
    
    def updateColorPointAndSize(self):
        super().updateColorPointAndSize()
        self.rebuildsurf()
        
class dropbox(button): # ВЫПАДАЮЩИЙ СПИСОК
    def __init__(self, name, parent, colors, point, size, dtype, dropboxlayer, part=["all"]):
        super().__init__(name, parent, colors, point, size, stateDrop=False, text=dropboxlayer.childs[0].text, align="left", part=part)
        self.onePerDrop = True # Только 1 активный объект, деактивируется от нажатия на что-то ещё
        self.dblayer = dropboxlayer
        dropboxlayer.mainparent = self
        self.curritem = self.dblayer.childs[0]
        self.type = dtype # 0 - со "стрелочкой", 1 - нажатием, 2 - при наведении
        if dtype==0:
            ### Слои
            for i in range(4):
                im = image(size,"dbbutton",colors, part=["all"])
                self.buttonimages[i].append(im)
            im = image(size,"dbbutton",colors,part=["text"],text="v")
            self.textimages[0].append(im)
            im = image(size,"dbbutton",colors,part=["text"],text="^")
            self.textimages[1].append(im)
            im = image(size,"dbbutton",colors,part=["text"],text="v")
            self.textimages[2].append(im)
            im = image(size,"dbbutton",colors,part=["text"],text="^")
            self.setImages()
            ###

    def addItem(self, item):
        self.dblayer.childs.append(item)
        self.dblayer.rebuildsurf()

    def hideLayer(self):
        if self.dblayer.parent:
            p = self.dblayer.parent
            p.childs.remove(self.dblayer) # Убираем слой с экрана
            self.dblayer.parent = False

    def setLayerAtRightPoint(self, p):
        # w=
        if self.point[0]+self.dblayer.size[0] <= p.size[0]:
            w = self.point[0]
        else:
            w = self.point[0]+self.dblayer.size[0]-self.dblayer.size[0]
        # h=
        if self.point[1]+self.dblayer.size[1] <= p.size[1]:
            h = self.point[1]+self.size[1]
        else:
            h = self.point[1]-self.dblayer.size[1]
        self.dblayer.point = (w,h)
        
    def showLayer(self):
        global mainobject
        p = mainobject
        self.setLayerAtRightPoint(p) # Устанавливаем слою точку
        if not(self.dblayer.parent):
            p.childs.append(self.dblayer) # Добавляем слой на экран
            self.dblayer.parent = p

    def changeSelection(self,newitem):
        for obj in self.textimages:
            print(obj[0])
            im = obj[0]
            im.rebuildimage(im.size,im.style,im.colors,im.part,im.alpha,im.startpoint,im.pic, newitem.text ,im.font,im.align)
        self.setImages()
        inteventsAdd([dropbox,self,"selection"])
        return True
        
    def deactivate(self):
        if super().deactivate():
            self.hideLayer()
            return True
        else:
            return False
        
    def activate(self):
        if super().activate():
            self.showLayer()
            return True
        else:
            return False
        
    def actions(self):
        if self.disabled:
            return False
        else:
            if self.state:
                if not(self.stateDrop):
                    return self.deactivate()
                else:
                    return False
            else:
                return self.activate()
            
    def updateColorPointAndSize(self):
        global mainobject
        super().updateColorPointAndSize()
        self.setLayerAtRightPoint(mainobject)

class textbox(button): # ТЕКСТОВОЕ ПОЛЕ
    def __init__(self, name, parent, colors, point, size, text="", deftext="", align="left", maxlen=999, onlynumbers = False, part=["all"]):
        if text!="":
            super().__init__(name, parent, colors, point, size, stateDrop=False, text=text, align=align, style="textbox", part=part)
        else:
            super().__init__(name, parent, colors, point, size, stateDrop=False, text=deftext, align=align, style="textbox", part=part)
        self.onePerDrop = True # Только 1 активный объект, деактивируется от нажатия на что-то ещё
        self.colors = colors
        self.align = align
        self.deftext = []
        for s in deftext:
            self.deftext.append(s)
        self.text = []
        for s in text:
            self.text.append(s)
        self.maxlen = 999
        self.onlynumbers = onlynumbers

    def updateSurf(self):
        t = "".extend(self.text) if len(self.text)>0 else "".extend(self.deftext)
        ### Слои
        for i in range(4):
            im = image(self.size,"textbox"+str(i),self.colors,part=["text"],text=t)
            self.textimages[i].clear()
            self.textimages[i].append(im)
        self.setImages()
        ###
        
    def addSymbol(self, symbol):
        if (symbol in ("0","1","2","3","4","5","6","7","8","9") or not(self.onlynumbers)) and len(self.text)<self.maxlen:
            self.text.append(symbol)
            self.updateSurf()
        inteventsAdd([textbox,self,"textchange","".entend(self.text) if len(self.text)>0 else "".entend(self.deftext)])
        return True
        
    def removeSymbol(self, symbol):
        if len(self.text)>0:
            self.text.pop(-1)
            self.updateSurf()
        inteventsAdd([textbox,self,"textchange","".entend(self.text) if len(self.text)>0 else "".entend(self.deftext)])
        return True
    
class dbutton(button): # КНОПКА СОКРЫТИЯ СЛОЯ
    def __init__(self, name, parent, colors, point, size, lay, meval, layval, text="", align="middle", style="button", part=["all"]):
        super().__init__(name, parent, colors, point, size, stateDrop=False, text=text, align=align, style=style, part=part)
        self.changeSizeOnAct = True
        
        self.hidenPoint = meval[0] if meval else False
        self.hidenSize = meval[1] if meval else False
        
        self.lay = lay # Связанный слой
        lay.dbut = self
        
        self.layHidenPoint = layval[0] if layval else False
        self.layHidenSize = layval[1] if layval else False

    def activate(self):
        global menudata
        if super().activate():
            (objects, w, h, f, r, c) = menudata
            self.lay.point = eval(self.layHidenPoint)
            self.lay.size = eval(self.layHidenSize)
            self.lay.rect.x = self.lay.point[0]
            self.lay.rect.y = self.lay.point[1]
            self.lay.rect.width = self.lay.size[0]
            self.lay.rect.height = self.lay.size[1]
            self.point =  eval(self.hidenPoint)
            self.size =  eval(self.hidenSize)
            self.rect.x = self.point[0]
            self.rect.y = self.point[1]
            self.rect.width = self.size[0]
            self.rect.height = self.size[1]
            return True
        else:
            return False
        
    def deactivate(self):
        global menudata
        if super().deactivate():
            (objects, w, h, f, r, c) = menudata
            self.lay.point = eval(self.lay.updatePoint)
            self.lay.size = eval(self.lay.updateSize)
            self.lay.rect.x = self.lay.point[0]
            self.lay.rect.y = self.lay.point[1]
            self.lay.rect.width = self.lay.size[0]
            self.lay.rect.height = self.lay.size[1]
            self.point =  eval(self.updatePoint)
            self.size =  eval(self.updateSize)
            self.rect.x = self.point[0]
            self.rect.y = self.point[1]
            self.rect.width = self.size[0]
            self.rect.height = self.size[1]
            return True
        else:
            return False
        
    def updateColorPointAndSizeSelf(self):
        global menudata
        (objects, w, h, f, r, c) = menudata
        if self.state:
            p = eval(self.hidenPoint)
            s = eval(self.hidenSize)
        else:
            p = eval(self.updatePoint)
            s = eval(self.updateSize)
        self.point = p
        self.size = s
        self.surf = pygame.Surface(self.size) # Поверхность
        self.surf.set_colorkey(self.surf.get_at((0,0))) # И делаем её прозрачной
        for im in self.images:
            im.rebuildimage(s,im.style,c,im.part,im.alpha,p,im.pic,im.text,im.font,im.align)
        if self.parent: # Область
            self.rect.x = self.parent.rect.x+self.point[0]
            self.rect.y = self.parent.rect.y+self.point[1]
        else:
            self.rect.x = self.point[0]
            self.rect.y = self.point[1]
        self.rect.width = self.size[0]
        self.rect.height = self.size[1]

class sliderBar(layer):
    def __init__(self, name, parent, colors, point, size, slbut, alpha=False, text="", style="slider", part=False):
        super().__init__(name, parent, colors, point, size, alpha=alpha, text=text, style=style, part=part)
        self.childs.append(slbut)

class slider(layer):
    def __init__(self, name, parent, colors, point, size, lay, slbar, alpha=False, text="", style="slider", part=False):
        super().__init__(name, parent, colors, point, size, alpha=alpha, text=text, style=style, part=part)
        self.childs.append(lay)
        self.childs.append(slbar)
        self.lay = lay
        self.slbar = slbar






if __name__ == "__main__":
     mainWindow = mainProgramWindow()





