import pygame
import math

black = (  0,  0,    0)
white = (255, 255, 255)
blue =  (  0,   0, 255)
green = (  0, 255,   0)
red =   (255,   0,   0)
clear = (1,1,1)
up = 0
right = 1
down = 2
left = 3
defaultsize = (3,2)
defaultnullzones = (((1,0),(2,0)),#there might be an easier way to store this data
                    ((1,0),(1,1)))




class TraceStart(pygame.sprite.Sprite):
    def __init__(self, maze, pos):
        super().__init__()
        self.fullradius = int(maze.linewidth*1.15)
        self.color = maze.tracecolor
        self.currentradius = self.fullradius//3
        self.donegrowing = False
        self.fade = 0
        self.image = pygame.Surface([self.fullradius*2,self.fullradius*2])
        self.image.fill(clear)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - self.fullradius
        self.rect.y = pos[1] - self.fullradius
        
    def update(self):
        if not self.donegrowing:
            if self.currentradius < self.fullradius:
                self.currentradius += math.ceil((self.fullradius - self.currentradius)/4)
            else:
                self.donegrowing = True
            
    def draw(self, display):
        pygame.draw.circle(display, self.color,
                                (self.rect.x+self.fullradius,self.rect.y+self.fullradius),
                                self.currentradius)
class TraceBody():
    pass

class TraceHead(pygame.sprite.Sprite):
    def __init__(self, maze, pos):
        super().__init__()
        self.width = maze.linewidth
        self.xborder = maze.wspace//2
        self.yborder = maze.hspace//2
        self.mazesquaresize = maze.squaresize
        self.mazewalls = maze.walls
        self.image = pygame.Surface([self.width,self.width])
        self.color = maze.tracecolor
        self.fade = 0
        self.initpos = pos
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - self.width//2# subtract half of width bc gridpos is pixel value for center of an intersection
        self.rect.y = pos[1] - self.width//2
        self.image.fill(clear)
        

    def update(self,):
        mousepos = pygame.mouse.get_pos()
        diffx = mousepos[0] - (self.rect.x + self.width/2) #diff between center of line head and mouse, not top left corner
        diffy = -mousepos[1] + (self.rect.y + self.width/2) #reversed bc display y-axis is flipped
        fractiontomove = 4
        gridpos = [(self.rect.x - self.xborder)/(self.mazesquaresize+self.width),
                   (self.rect.y - self.yborder)/(self.mazesquaresize+self.width)]
        if abs(diffy) > abs(diffx):#primary axis is up/down
            if gridpos[0].is_integer(): #trace is on grid column, can move up/down
                if diffy > 2:
                    self.tryMove(up,diffy/fractiontomove)
                elif diffy < -2:
                    self.tryMove(down,abs(diffy)/fractiontomove)
            else: #can't move up/down, try left/right
                if diffx > 2:
                    self.tryMove(right,diffx/fractiontomove)
                elif diffx < -2:
                    self.tryMove(left,abs(diffx)/fractiontomove)
                elif abs(diffy) > self.mazesquaresize//5:#if cursor getting far away, check if can snap to intersection
                    disttoisect = (self.rect.x - self.xborder)%(self.mazesquaresize+self.width)
                    if disttoisect <= self.width:#trace is 1 linewidth right of intersection 
                        self.tryMove(left,disttoisect)
                    elif disttoisect >= (self.mazesquaresize+self.width) - self.width:#trace is 1 linewidth left of intersection
                        self.tryMove(right,(self.mazesquaresize+self.width) - disttoisect)
        else:#primary axis is left/right
            if gridpos[1].is_integer(): #trace is on grid row, can move up/down as long as no border in way
                if diffx > 2:
                    self.tryMove(right,diffx/fractiontomove)
                elif diffx < -2:
                    self.tryMove(left,abs(diffx)/fractiontomove)
            else: #can't move left/right, try up/down
                if diffy > 2:
                    self.tryMove(up,diffy/fractiontomove)
                elif diffy < -2:
                    self.tryMove(down,abs(diffy)/fractiontomove)
                elif abs(diffx) > self.mazesquaresize//5:#if cursor getting far away, check if can snap to intersection
                    disttoisect = (self.rect.y - self.yborder)%(self.mazesquaresize+self.width)
                    if disttoisect <= self.width:#trace is 1 linewidth below intersection 
                        self.tryMove(up,disttoisect)
                    elif disttoisect >= (self.mazesquaresize+self.width) - self.width:#trace is one linewidth above intersection
                        self.tryMove(down,(self.mazesquaresize+self.width) - disttoisect)
        
                        
    def tryMove(self,direction,dist_to_move):
        distance = math.ceil(dist_to_move) #always try to move at least 1 pixel
        collisions = []
        if direction == up:
            for i in range(distance):
                if not collisions:
                    self.rect.y -= 1 #don't forget display y-axis is reverse
                    collisions = pygame.sprite.spritecollide(self, self.mazewalls, False)
                    for wall in collisions:
                        self.rect.top = wall.rect.bottom
        elif direction == right:
            for i in range(distance):
                if not collisions:
                    self.rect.x += 1
                    collisions = pygame.sprite.spritecollide(self, self.mazewalls, False)
                    for wall in collisions:
                        self.rect.right = wall.rect.left
        elif direction == down:
            for i in range(distance):
                if not collisions:
                    self.rect.y += 1 #don't forget display y-axis is reverse
                    collisions = pygame.sprite.spritecollide(self, self.mazewalls, False)
                    for wall in collisions:
                        self.rect.bottom = wall.rect.top
        elif direction == left:
            for i in range(distance):
                if not collisions:
                    self.rect.x -= 1
                    collisions = pygame.sprite.spritecollide(self,self.mazewalls,False)
                    for wall in collisions:
                        self.rect.left = wall.rect.right
                        
    def draw(self,display):
        pygame.draw.circle(display,self.color,(self.rect.x+self.width//2,self.rect.y+self.width//2),self.width//2)

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        
class Maze():
    def __init__(self, display, size, nullzones,
                 symbols, starts, ends, hexagons,
                 linefrac, bgcolor, gridcolor, tracecolor):
        self.size = size #tuple with (x,y)
        self.nullzones = nullzones #see default above
        self.symbols = symbols #tuple with (x,y), relative to squares, not intersections
        self.starts = starts #list of starting point positions
        self.ends = ends #list of ending point positions
        self.hexagons = hexagons #list of hexagon positions
        self.linefrac = linefrac #should be a fraction, i.e. 1/4 for 1/4 the size of squares
        self.bgcolor = bgcolor #color of squares and border
        self.gridcolor = gridcolor #color of grid lines
        self.tracecolor = tracecolor #color of trace
        self.grid = []
        for y in range(size[0]):
            self.grid.append([])
            for x in range(size[1]):
                self.grid[y].append(0)
        self.generateWalls(display)
        
    def printMaze(self):
        for i in self.grid:
            for j in i:
                print(j, end=" ")
            print()
            
    def generateWalls(self,display):
        image = display.copy()
        self.screenrect = display.get_rect()
        #get largest possible square size (remember linefrac is fraction of square size, like 1/4)
        #includes space in between squares and 1.5x line width worth of buffer on both bounding edges
        self.squaresize = self.screenrect.w // (self.size[0] + (self.linefrac*self.size[0]) + 4*self.linefrac)
        #test if that self.squaresize is compatible with vertical dimension, if it bleeds over vertical is limiting
        if self.squaresize*(1+self.linefrac)*self.size[1] + 4*self.squaresize*self.linefrac > self.screenrect.h:
            self.squaresize = self.screenrect.h // (self.size[1] + (self.linefrac*self.size[1]) + 4*self.linefrac)
        self.squaresize = int(self.squaresize)
        self.linewidth = int(self.squaresize*self.linefrac)#I need the pixel value of self.linewidth more after this, so this will be useful
        if self.linewidth % 2 == 1:#make the line width always be even so that the trace head circle will fill it completely
            self.squaresize -= 1
            self.linewidth = int(self.squaresize*self.linefrac)
        self.wspace = int(self.screenrect.w - ((self.squaresize+self.linewidth)*self.size[0] + self.linewidth))
        self.hspace = int(self.screenrect.h - ((self.squaresize+self.linewidth)*self.size[1] + self.linewidth))
        self.walls = pygame.sprite.Group()
        self.walls.add(Wall(0,0,self.wspace//2,
                            self.screenrect.h,self.bgcolor))#left boundary
        self.walls.add(Wall(((self.squaresize+self.linewidth)*self.size[0] + self.linewidth)+ self.wspace//2,0,
                            self.screenrect.w,self.screenrect.h,self.bgcolor))#right boundary
        self.walls.add(Wall(self.wspace//2,0,
                            self.screenrect.w-self.wspace//2,self.hspace//2,self.bgcolor))#top boundary
        self.walls.add(Wall(self.wspace//2,((self.squaresize+self.linewidth)*self.size[1] + self.linewidth)+self.hspace//2,
                            ((self.squaresize+self.linewidth)*self.size[0] + self.linewidth)+ self.wspace//2,self.screenrect.h,self.bgcolor))#bottom boundary
        #add grid squares, these for loops might be redundant with creation of self.grid earlier, clean up
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                squarex = self.wspace//2+self.linewidth+(x*(self.squaresize+self.linewidth))
                squarey = self.hspace//2+self.linewidth+(y*(self.squaresize+self.linewidth))
                self.walls.add(Wall(squarex,squarey,self.squaresize,self.squaresize,self.bgcolor))
                
    def drawStarts(self,display):
        self.startlist = []
        for startpos in self.starts:
            pygame.draw.circle(display,self.gridcolor,
                                (self.wspace//2 + self.linewidth//2 + startpos[0]*(self.squaresize+self.linewidth),
				self.hspace//2 + self.linewidth//2 + startpos[1]*(self.squaresize+self.linewidth)),
                                int(self.linewidth*1.15))
            
    def tryStart(self,mousepos):
        mgridpos = [(mousepos[0] - (self.wspace//2) - self.linewidth//2)/(self.squaresize+self.linewidth),
                   (mousepos[1] - (self.hspace//2) - self.linewidth//2)/(self.squaresize+self.linewidth)]
        startradius = (self.linewidth*1.1)/(self.squaresize + self.linewidth)
        for start in self.starts:
            if abs(start[0] - mgridpos[0]) < startradius and abs(start[1] - mgridpos[1]) < startradius:
                self.tracelist = self.maketrace((self.wspace//2 + self.linewidth//2 + start[0]*(self.squaresize+self.linewidth),
                                        self.hspace//2 + self.linewidth//2 + start[1]*(self.squaresize+self.linewidth)))
                return True
            
    def maketrace(self,gridpos):
        self.tracegroup = pygame.sprite.Group()
        self.tracegroup.fade = 0
        #add tracebody in here later
        self.tracegroup.add(TraceStart(self,gridpos),TraceHead(self,gridpos))
        
    def update(self,is_alive):
        if is_alive:
            #update maze flashing symbols when wrong
            self.tracegroup.update()
        elif self.tracegroup.fade < 256:
            self.tracegroup.fade += 2
            
        
    def drawMaze(self, display):
        self.walls.draw(display)
        self.drawStarts(display)
        
    def drawTrace(self,display):
        tempdisplay = pygame.Surface((display.get_width(),display.get_height()))
        tempdisplay.set_colorkey(clear)#makes everything that's that color transparent
        tempdisplay.fill(clear)
        for section in self.tracegroup:
            section.draw(tempdisplay)
        #self.tracegroup.draw(tempdisplay)#all the sections of the trace need to be faded as one image, otherwise
                                        #we get issues with transparent surfaces overlapping and being more opaque
        tempdisplay.set_alpha(256 - self.tracegroup.fade)
        display.blit(tempdisplay,(0,0))
        


pygame.init()
displaysize = [800,600]
screen = pygame.display.set_mode(displaysize)
clock = pygame.time.Clock()
m1prev = False
is_alive = False
startupdating = False
done = False

testmaze = Maze(screen,(2,2),(),
                (),((0,2),(2,0)),(),(),#that comma needs to be there to tell python that's a tuple tuple, not just a tuple lol
                1/5,(0,70,205,255),(25,25,112,255), white)

while not done:
    pygame.event.clear()#won't need to get events from event queue, chuck'em
    mousestates = pygame.mouse.get_pressed()
    if mousestates[0] != m1prev:
        if m1prev == False:#mouse being pressed
            mousepos = pygame.mouse.get_pos()
            if testmaze.tryStart(mousepos):
                is_alive = True
                startupdating = True
        else:#mouse being released
            is_alive = False
        m1prev = mousestates[0]
    if mousestates[1] == True:#close program upon middle mouse
        done = True
        
    screen.fill(testmaze.gridcolor)
    testmaze.drawMaze(screen)
    
    if startupdating:
        testmaze.update(is_alive)
        testmaze.drawTrace(screen)
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
