import pygame
import math
from copy import deepcopy

black = (  0,  0,    0) #establishing some constants for code readability
white = (255, 255, 255)
blue =  (  0,   0, 255)
green = (  0, 255,   0)
red =   (255,   0,   0)
clear = (1,1,1)

full = -1

up = 0
right = 1
down = 2
left = 3

class Trace():
    def __init__(self, maze, startpos):
        #starting circle
        self.width = maze.linewidth
        self.radius = self.width/2
        self.xborder = maze.wspace//2
        self.yborder = maze.hspace//2
        self.mazesize = maze.size
        self.mazesquaresize = maze.squaresize
        self.gridsquaresize = maze.gridsquaresize
        self.color = maze.tracecolor
        
        self.origbarriers = maze.barriers
        self.mazebarriers = deepcopy(maze.barriers)#we need the maze barriers and a copy of them, for which we must use deepcopy since it's a nested list
                                                    #the copy will be used to reset barriers to their original values instead of recalculating them
        self.pos = [startpos[0],startpos[1]]
        self.startpos = tuple(startpos)

        self.path = [((self.pos[0] - self.xborder - self.width/2)/(self.mazesquaresize+self.width),
                            (self.pos[1] - self.yborder - self.width/2)/(self.mazesquaresize+self.width)),] #starting grid position for path
        self.pixelpath = [self.startpos]
        self.isonrow = True
        self.isoncolumn = True
        self.xtravelled = 0
        self.xsquarestravelled = 0.0
        self.ytravelled = 0
        self.ysquarestravelled = 0.0

        self.fullradius = int(maze.linewidth*1.15)
        self.currentradius = self.fullradius//3#start circle starts part of the way filled, as it does in game
        self.is_alive = True
        self.is_validated = False
        self.donegrowing = False
        self.fade = 0
        
        self.addStartBorders()

        
    def update(self):
        if self.is_alive and not self.is_validated:
            #starting circle expansion
            if not self.donegrowing:
                if self.currentradius < self.fullradius:
                    self.currentradius += math.ceil((self.fullradius - self.currentradius)/5)#dictates speed of start circle filling
                else:
                    self.donegrowing = True
                    
            #trace head movement
            mousepos = pygame.mouse.get_pos()
            diffx = mousepos[0] - self.pos[0] #diff between center of line head and mouse, not top left corner
            diffy = -mousepos[1] + self.pos[1] #reversed bc display y-axis is flipped
            fractiontomove = 4
            diffmargin = 2#prevents being in between pixels with cursor from making trace head oscillate 1 pixel

            self.ysquarestravelled = self.ytravelled/self.gridsquaresize
            self.xsquarestravelled = self.xtravelled/self.gridsquaresize
            
            if abs(diffy) > abs(diffx):#primary axis is up/down
                
                if self.xsquarestravelled.is_integer(): #trace is on grid column, can move up/down
                    if diffy > diffmargin:#up
                        self.tryMove(diffy/fractiontomove, up)
                    elif diffy < -diffmargin:#down
                        self.tryMove(abs(diffy)/fractiontomove, down)
                else: #can't move up/down, try left/right
                    if diffx > diffmargin:#right
                        self.tryMove(diffx/fractiontomove, right)
                    elif diffx < -diffmargin:#left
                        self.tryMove(abs(diffx)/fractiontomove, left)
                        
                    elif abs(diffy) > self.mazesquaresize//4:#if cursor getting far away, check if can snap to intersection
                        disttoisect = int((self.pos[0] - self.xborder - self.width/2)%(self.mazesquaresize+self.width))
                        if disttoisect <= self.width:#trace is 1 linewidth right of intersection 
                            self.tryMove(disttoisect, left)
                        elif disttoisect >= (self.mazesquaresize+self.width) - self.width:#trace is 1 linewidth left of intersection
                            self.tryMove(self.mazesquaresize + self.width - disttoisect, right)
                            
                            
            else:#primary axis is left/right
                
                if self.ysquarestravelled.is_integer(): #trace is on grid row, can move up/down as long as no border in way
                    if diffx > diffmargin:#right
                        self.tryMove(diffx/fractiontomove, right)
                    elif diffx < -diffmargin:#left
                        self.tryMove(abs(diffx)/fractiontomove, left)
                else: #can't move left/right, try up/down
                    if diffy > diffmargin:#up
                        self.tryMove(diffy/fractiontomove, up)
                    elif diffy < -diffmargin:#down
                        self.tryMove(abs(diffy)/fractiontomove, down)
                    
                    elif abs(diffx) > self.mazesquaresize//4:#if cursor getting far away, check if can snap to intersection
                        disttoisect = int((self.pos[1] - self.yborder - self.width/2)%(self.mazesquaresize+self.width))
                        if disttoisect <= self.width:#trace is 1 linewidth below intersection 
                            self.tryMove(disttoisect,up)
                        elif disttoisect >= (self.mazesquaresize+self.width) - self.width:#trace is one linewidth above intersection
                            self.tryMove(self.mazesquaresize+self.width - disttoisect, down)
        elif not self.is_alive and self.fade < 256:
            self.fade += 2
            
                        
    def tryMove(self,dist_to_move,direction):
        distance = math.ceil(dist_to_move) #always try to move at least 1 pixel
        
        if direction == up:
            for i in range(distance):
                if self.ysquarestravelled.is_integer():
                    if self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending and coords to be added are not redundant
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                        self.addEdges(up)
                    elif len(self.path) > 1:
                        if self.path[0][1]+self.ysquarestravelled > self.path[-2][1] and self.path[-1][0] == self.path[-2][0]: #line is retracting
                            self.popEdges()
                            self.path.pop()
                            self.pixelpath.pop()
                        else:
                            self.popEdges()
                            self.addEdges(up)
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])][up]
                if self.pos[1] - self.radius != self.currentbarrier:
                    self.pos[1] -= 1
                    self.ytravelled -= 1
                    self.ysquarestravelled = self.ytravelled/self.gridsquaresize
                else:
                    return
                
        elif direction == down:
            for i in range(distance):
                if self.ysquarestravelled.is_integer():
                    if self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                        self.addEdges(down)
                    elif len(self.path) > 1:
                        if self.path[0][1]+self.ysquarestravelled < self.path[-2][1] and self.path[-1][0] == self.path[-2][0]: #line is retracting
                            self.popEdges()
                            self.path.pop()
                            self.pixelpath.pop()
                        else:
                            self.popEdges()
                            self.addEdges(down)
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])][down]
                if self.pos[1] + self.radius != self.currentbarrier:
                    self.pos[1] += 1
                    self.ytravelled += 1
                    self.ysquarestravelled = self.ytravelled/self.gridsquaresize
                else:
                    return
                
        elif direction == right:
            for i in range(distance):
                if self.xsquarestravelled.is_integer():
                    if self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                        self.addEdges(right)
                    elif len(self.path) > 1:
                        if self.path[0][0]+self.xsquarestravelled < self.path[-2][0] and self.path[-1][1] == self.path[-2][1]: #line is retracting
                            self.popEdges()
                            self.path.pop()
                            self.pixelpath.pop()
                        else:
                            self.popEdges()
                            self.addEdges(right)
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])][right]
                if self.pos[0] + self.radius != self.currentbarrier:
                    self.pos[0] += 1
                    self.xtravelled += 1
                    self.xsquarestravelled = self.xtravelled/self.gridsquaresize
                else:
                    return
                
        elif direction == left:
            for i in range(distance):
                if self.xsquarestravelled.is_integer():
                    if self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                        self.addEdges(left)
                    elif len(self.path) > 1:
                        if self.path[0][0]+self.xsquarestravelled > self.path[-2][0] and self.path[-1][1] == self.path[-2][1]: #line is retracting
                            self.popEdges()
                            self.path.pop()
                            self.pixelpath.pop()
                        else:
                            self.popEdges()
                            self.addEdges(left)
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])][left]
                if self.pos[0] - self.radius != self.currentbarrier:
                    self.pos[0] -= 1
                    self.xtravelled -= 1
                    self.xsquarestravelled = self.xtravelled/self.gridsquaresize
                else:
                    return 

    def addEdges(self,direction):
        if direction != up:
            if self.path[-1][1] != 0 and self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])-1][down] == None:
                self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])-1][down] = self.yborder + self.path[-1][1]*self.gridsquaresize
        if direction != down:
            if self.path[-1][1] != self.mazesize[1] and self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])+1][up] == None:
                self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])+1][up] = self.yborder + self.path[-1][1]*self.gridsquaresize + self.width
        if direction != right:
            if self.path[-1][0] != self.mazesize[0] and self.mazebarriers[int(self.path[-1][0])+1][int(self.path[-1][1])][left] == None:
                self.mazebarriers[int(self.path[-1][0])+1][int(self.path[-1][1])][left] = self.xborder + self.path[-1][0]*self.gridsquaresize + self.width
        if direction != left:
            if self.path[-1][0] != 0 and self.mazebarriers[int(self.path[-1][0])-1][int(self.path[-1][1])][right] == None:
                self.mazebarriers[int(self.path[-1][0])-1][int(self.path[-1][1])][right] = self.xborder + self.path[-1][0]*self.gridsquaresize
        
    def popEdges(self):
        try:
            self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])+1][up] = self.origbarriers[int(self.path[-1][0])][int(self.path[-1][1])+1][up]
        except:
            pass
        try:
            self.mazebarriers[int(self.path[-1][0])][int(self.path[-1][1])-1][down] = self.origbarriers[int(self.path[-1][0])][int(self.path[-1][1])-1][down]
        except:
            pass
        try:
            self.mazebarriers[int(self.path[-1][0])-1][int(self.path[-1][1])][right] = self.origbarriers[int(self.path[-1][0])-1][int(self.path[-1][1])][right]
        except:
            pass
        try:
            self.mazebarriers[int(self.path[-1][0])+1][int(self.path[-1][1])][left] = self.origbarriers[int(self.path[-1][0])+1][int(self.path[-1][1])][left]
        except:
            pass
        
    def addStartBorders(self):
        if self.path[0][0] != 0 and self.mazebarriers[int(self.path[0][0])-1][int(self.path[0][1])][right] == None:
                self.mazebarriers[int(self.path[0][0])-1][int(self.path[0][1])][right] = self.xborder + self.gridsquaresize*self.path[0][0] + self.width/2 - self.fullradius
        if self.path[0][0] != self.mazesize[0] and self.mazebarriers[int(self.path[0][0])+1][int(self.path[0][1])][left] == None:
                self.mazebarriers[int(self.path[0][0])+1][int(self.path[0][1])][left] = self.xborder + self.gridsquaresize*self.path[0][0] + self.width/2 + self.fullradius
        if self.path[0][1] != 0 and self.mazebarriers[int(self.path[0][0])][int(self.path[0][1])-1][down] == None:
            self.mazebarriers[int(self.path[0][0])][int(self.path[0][1])-1][down] = self.yborder + self.gridsquaresize*self.path[0][1] + self.width/2 - self.fullradius
        if self.path[0][1] != self.mazesize[1] and self.mazebarriers[int(self.path[0][0])][int(self.path[0][1])+1][up] == None:
            self.mazebarriers[int(self.path[0][0])][int(self.path[0][1])+1][up] = self.yborder + self.gridsquaresize*self.path[0][1] + self.width/2 + self.fullradius
        
    def draw(self,display):
        pygame.draw.circle(display, self.color, (self.startpos[0]+1,self.startpos[1]+1), self.currentradius)
        self.pixelpath.append(self.pos)
        for coord in range(len(self.pixelpath)-1):
            pygame.draw.line(display,self.color,(self.pixelpath[coord][0],self.pixelpath[coord][1]),(self.pixelpath[coord+1][0],self.pixelpath[coord+1][1]),self.width)
            pygame.draw.circle(display,self.color,(self.pixelpath[coord][0]+1,self.pixelpath[coord][1]+1),int(self.radius))
        pygame.draw.circle(display,self.color,(self.pos[0]+1,self.pos[1]+1),int(self.radius))
        self.pixelpath.pop()

        
class Maze():
    def __init__(self, display, size, nullzones,
                 symbols, starts, ends, hexagons,
                 linefrac, endfrac,
                 bgcolor, gridcolor, tracecolor):
        self.size = size #tuple with (x,y)
        self.symbols = symbols #tuple with (x,y), relative to squares, not intersections
        self.starts = starts #list of starting point positions
        self.sortEnds(ends) #generates 4 lists of end points, one for each maze side, needed later
        self.hexagons = hexagons #list of hexagon positions
        self.linefrac = linefrac #should be a fraction, i.e. 1/4 for 1/4 the size of squares
        self.endfrac = endfrac #similar to linefrac, the length of the finish point nub section given as a fraction of square size, i.e. 1/4
        self.bgcolor = bgcolor #color of squares and border
        self.gridcolor = gridcolor #color of grid lines
        self.tracecolor = tracecolor #color of trace
        
        self.grid = []
        self.tracedisplay = pygame.Surface((display.get_width(),display.get_height()))
        self.tracedisplay.set_colorkey(clear)#makes everything that's that color transparent
        self.tracedisplay.fill(clear)
        
        for y in range(size[1]):
            self.grid.append([])
            for x in range(size[0]):
                self.grid[y].append(None)
                
        self.generateDimensions(display)
        self.generateNullZonesAndMaze(nullzones,display)
        self.trace = Trace(self,(0,0))#need a dead trace to start out with
        self.trace.is_alive = False
        self.trace.fade = 256
        
    def printMaze(self):
        for i in self.grid:
            for j in i:
                print(j, end=" ")
            print()
            
    def sortEnds(self,ends):
        sortedends = sorted(ends, key=lambda end: end[2])#sorts all ends by direction value in third index
        self.upends = []
        self.rightends = []
        self.downends = []
        self.leftends = []
        for end in sortedends:
            if end[2] == up:
                self.upends.append(end[0]) #adds the positions of the ends along their respective sides
            elif end[2] == right:
                self.rightends.append(end[1])
            elif end[2] == down:
                self.downends.append(end[0])
            else:
                self.leftends.append(end[1])
        self.upends.sort()
        self.rightends.sort()
        self.downends.sort()
        self.leftends.sort()
            
    def generateDimensions(self,display):
        image = display.copy()
        self.screenrect = display.get_rect()
        #get largest possible square size (remember linefrac is fraction of square size, like 1/4)
        #includes space in between squares and 2x line width worth of buffer on both bounding edges
        self.squaresize = self.screenrect.w // (self.size[0] + (self.linefrac*self.size[0]) + 5*self.linefrac)
        #test if that self.squaresize is compatible with vertical dimension, if it bleeds over that means vertical is limiting dimension
        if self.squaresize*(1+self.linefrac)*self.size[1] + 4*self.squaresize*self.linefrac > self.screenrect.h:
            self.squaresize = self.screenrect.h // (self.size[1] + (self.linefrac*self.size[1]) + 5*self.linefrac)
        self.squaresize = int(self.squaresize)
        self.linewidth = int(self.squaresize*self.linefrac)#I need the pixel value of self.linewidth more after this, so this will be useful
        while self.linewidth % 2 == 1:#make the line width always be even so that the trace head circle will fill it completely
            self.squaresize -= 1 #while loop because subtracting 1 from square size doesn't always make linewidth even
            self.linewidth = int(self.squaresize*self.linefrac)
        self.gridsquaresize = self.squaresize + self.linewidth
        self.wspace = int(self.screenrect.w - (self.gridsquaresize*self.size[0] + self.linewidth))
        self.hspace = int(self.screenrect.h - (self.gridsquaresize*self.size[1] + self.linewidth))
        
    def generateNullZonesAndMaze(self,nullcoords,display):
        self.mazeimage = display.copy()
        self.mazeimage.fill(self.bgcolor)

        fullnulls = []
        for nullzone in nullcoords:
            if nullzone[2] == full:
                fullnulls.append(nullzone)
                
        for row in range(self.size[1]):
            for column in range(self.size[0]):
                pixelpos = (int(self.wspace/2 + self.linewidth/2 + column*self.gridsquaresize),
                            int(self.hspace/2 + self.linewidth/2 + row*self.gridsquaresize))
                downrightpixelpos = (int(self.wspace/2 + (column+1)*self.gridsquaresize),
                                    int(self.hspace/2 + (row+1)*self.gridsquaresize))
                if (column,row,full) not in fullnulls:
                    pygame.draw.circle(self.mazeimage,self.gridcolor,(pixelpos[0]+1,pixelpos[1]+1),int(self.linewidth/2))
                    if (column+1,row,full) not in fullnulls and ((column,row),(column+1,row),1) not in nullcoords:
                        pygame.draw.line(self.mazeimage,self.gridcolor,(pixelpos[0],pixelpos[1]),(downrightpixelpos[0]+(self.linewidth/2),pixelpos[1]),self.linewidth)
                    if (column,row+1,full) not in fullnulls and ((column,row),(column,row+1),1) not in nullcoords:
                        pygame.draw.line(self.mazeimage,self.gridcolor,(pixelpos[0],pixelpos[1]),(pixelpos[0],downrightpixelpos[1]+(self.linewidth/2)),self.linewidth)
                #draw circle then line right and down, unless this coord or the next one is fullnull
            if (self.size[0],row,full) not in fullnulls:
                pygame.draw.circle(self.mazeimage,self.gridcolor,(int(self.wspace/2 + self.size[0]*self.gridsquaresize + self.linewidth/2 + 1),
                                                        int(self.hspace/2 + row*self.gridsquaresize + self.linewidth/2 + 1)),int(self.linewidth/2))
                if (self.size[0],row+1,full) not in fullnulls and ((self.size[0],row),(self.size[0],row+1),1) not in nullcoords:
                    pygame.draw.line(self.mazeimage,self.gridcolor,(self.wspace/2 + self.size[0]*self.gridsquaresize + self.linewidth/2,
                                                        self.hspace/2 + row*self.gridsquaresize + self.linewidth/2),
                                                        (self.wspace/2 + self.size[0]*self.gridsquaresize + self.linewidth/2,
                                                        self.hspace/2 + (row+1)*self.gridsquaresize + self.linewidth/2),self.linewidth)
        for column in range(self.size[0]):
            if (column,self.size[1],full) not in fullnulls:
                pygame.draw.circle(self.mazeimage,self.gridcolor,(int(self.wspace/2 + column*self.gridsquaresize + self.linewidth/2 + 1),
                                                                int(self.hspace/2 + self.size[1]*self.gridsquaresize + self.linewidth/2 + 1)),int(self.linewidth/2))
                if (column+1,self.size[1],full) not in fullnulls and ((column,self.size[1]),(column+1,self.size[1]),1) not in nullcoords:
                    pygame.draw.line(self.mazeimage,self.gridcolor,(self.wspace/2 + column*self.gridsquaresize + self.linewidth/2,
                                                                    self.hspace/2 + self.size[1]*self.gridsquaresize + self.linewidth/2),
                                                                    (self.wspace/2 + (column+1)*self.gridsquaresize + self.linewidth/2,
                                                                    self.hspace/2 + self.size[1]*self.gridsquaresize + self.linewidth/2),self.linewidth)
        if (self.size[0],self.size[1],full) not in fullnulls:
            pygame.draw.circle(self.mazeimage,self.gridcolor,(int(self.wspace/2 + self.size[0]*self.gridsquaresize + self.linewidth/2 + 1),
                                                                int(self.hspace/2 + self.size[1]*self.gridsquaresize + self.linewidth/2 + 1)),int(self.linewidth/2))
            
        self.barriers = []
        for column in range(self.size[0]+1):#size + 1 because size describes the number of squares in the maze, not num of grid intersections
            self.barriers.append([])
            for row in range(self.size[1]+1):
                self.barriers[column].append([None,None,None,None])
        #self.barriers will store, for each intersection in the maze, the pixel position of the barriers, should they exist, in each of the 4 directions.
        #these will be used to prevent the trace from going into the nullzones.
        for nullzone in nullcoords:
            #don't forget self.barriers coordinates are in row, column form!
            if nullzone[2] == full:
                if nullzone[0] != 0:
                    barrierleft = int(self.wspace/2 + (nullzone[0]-1)*self.gridsquaresize + self.linewidth)
                    self.barriers[nullzone[0]-1][nullzone[1]][right] = barrierleft
                if nullzone[0] != self.size[0]:
                    barrierright = int(self.wspace/2 + (nullzone[0]+1)*self.gridsquaresize)
                    self.barriers[nullzone[0]+1][nullzone[1]][left] = barrierright
                if nullzone[1] != 0:
                    barriertop = int(self.hspace/2 + (nullzone[1]-1)*self.gridsquaresize + self.linewidth)
                    self.barriers[nullzone[0]][nullzone[1]-1][down] = barriertop
                if nullzone[1] != self.size[1]:
                    barrierbot = int(self.hspace/2 + (nullzone[1]+1)*self.gridsquaresize)
                    self.barriers[nullzone[0]][nullzone[1]+1][up] = barrierbot
                
            elif abs(nullzone[1][0] - nullzone[0][0]) == 1: #horizontal
                barrierleft = int(self.wspace/2 + nullzone[0][0]*self.gridsquaresize + self.linewidth + ((1-nullzone[2])/2)*self.squaresize)
                barrierright = int(self.wspace/2 + nullzone[0][0]*self.gridsquaresize + self.linewidth + ((1-nullzone[2])/2)*self.squaresize + nullzone[2]*self.squaresize)
                self.barriers[nullzone[0][0]][nullzone[0][1]][right] = barrierleft
                self.barriers[nullzone[1][0]][nullzone[1][1]][left] = barrierright
                pygame.draw.line(self.mazeimage,self.bgcolor,(barrierleft+1,self.hspace//2+self.gridsquaresize*nullzone[0][1]+self.linewidth/2),
                                                             (barrierright,self.hspace//2+self.gridsquaresize*nullzone[0][1]+self.linewidth/2),self.linewidth)
            elif abs(nullzone[1][1] - nullzone[0][1]) == 1: #vertical
                barriertop = int(self.hspace/2 + nullzone[0][1]*self.gridsquaresize + self.linewidth + ((1-nullzone[2])/2)*self.squaresize)
                barrierbot = int(self.hspace/2 + nullzone[0][1]*self.gridsquaresize + self.linewidth + ((1-nullzone[2])/2)*self.squaresize + nullzone[2]*self.squaresize)
                self.barriers[nullzone[0][0]][nullzone[0][1]][down] = barriertop
                self.barriers[nullzone[1][0]][nullzone[1][1]][up] = barrierbot
                pygame.draw.line(self.mazeimage,self.bgcolor,(self.wspace//2+self.gridsquaresize*nullzone[0][0]+self.linewidth/2,barriertop+1),
                                                             (self.wspace//2+self.gridsquaresize*nullzone[0][0]+self.linewidth/2,barrierbot),self.linewidth)

        endlength = int(self.endfrac*self.squaresize)
        for column in range(self.size[0]+1):
            if column not in self.upends:
                self.barriers[column][0][up] = self.hspace//2
            else:
                self.barriers[column][0][up] = self.hspace//2 - endlength
                pygame.draw.line(self.mazeimage,self.gridcolor,(self.wspace//2+self.gridsquaresize*column+self.linewidth/2,self.hspace//2 + self.linewidth/2),
                                                                 (self.wspace//2+self.gridsquaresize*column+self.linewidth/2,self.hspace//2 + self.linewidth/2 - endlength),self.linewidth)
                pygame.draw.circle(self.mazeimage,self.gridcolor,(int(self.wspace//2+self.gridsquaresize*column+self.linewidth/2 + 1),int(self.hspace//2 + self.linewidth/2 - endlength + 1)),self.linewidth//2)
                
            if column not in self.downends:
                self.barriers[column][self.size[1]][down] = self.hspace//2 + self.gridsquaresize*self.size[1]+self.linewidth
            else:
                self.barriers[column][self.size[1]][down] = self.hspace//2 + self.gridsquaresize*self.size[1]+self.linewidth + endlength
                pygame.draw.line(self.mazeimage,self.gridcolor,(self.wspace//2+self.gridsquaresize*column+self.linewidth/2,self.hspace//2 + self.gridsquaresize*self.size[1]+self.linewidth/2),
                                                                 (self.wspace//2+self.gridsquaresize*column+self.linewidth/2,self.hspace//2 + self.gridsquaresize*self.size[1]+self.linewidth/2 + endlength),self.linewidth)
                pygame.draw.circle(self.mazeimage,self.gridcolor,(int(self.wspace//2+self.gridsquaresize*column+self.linewidth/2+1),
                                                                  int(self.hspace//2 + self.gridsquaresize*self.size[1]+self.linewidth/2 + endlength+1)),self.linewidth//2)
                
        for row in range(self.size[1]+1):
            if row not in self.rightends:
                self.barriers[self.size[0]][row][right] = self.wspace//2 + self.gridsquaresize*self.size[0]+self.linewidth
            else:
                self.barriers[self.size[0]][row][right] = self.wspace//2 + self.gridsquaresize*self.size[0]+self.linewidth + endlength
                pygame.draw.line(self.mazeimage,self.gridcolor,(self.wspace//2 + self.gridsquaresize*self.size[0]+self.linewidth/2,self.hspace//2 + self.gridsquaresize*row + self.linewidth/2),
                                                                (self.wspace//2 + self.gridsquaresize*self.size[0]+self.linewidth/2 + endlength,self.hspace//2 + self.gridsquaresize*row + self.linewidth/2),self.linewidth)
                pygame.draw.circle(self.mazeimage,self.gridcolor,(int(self.wspace//2 + self.gridsquaresize*self.size[0]+self.linewidth/2 + endlength+1),
                                                                  int(self.hspace//2 + self.gridsquaresize*row + self.linewidth/2+1)),self.linewidth//2)
            if row not in self.leftends:
                self.barriers[0][row][left] = self.wspace//2
            else:
                self.barriers[0][row][left] = self.wspace//2 - endlength
                pygame.draw.line(self.mazeimage,self.gridcolor,(self.wspace//2+self.linewidth/2,self.hspace//2+self.gridsquaresize*row+self.linewidth/2),
                                                             (self.wspace//2+self.linewidth/2-endlength,self.hspace//2+self.gridsquaresize*row+self.linewidth/2),self.linewidth)
                pygame.draw.circle(self.mazeimage,self.gridcolor,(int(self.wspace//2+self.linewidth/2-endlength+1),
                                                                  int(self.hspace//2+self.gridsquaresize*row+self.linewidth/2+1)),self.linewidth//2)
        self.drawStarts(self.mazeimage)
        
    def tryStart(self,mousepos):
        mgridpos = [(mousepos[0] - (self.wspace//2) - self.linewidth//2)/self.gridsquaresize,
                   (mousepos[1] - (self.hspace//2) - self.linewidth//2)/self.gridsquaresize]
        startradius = (self.linewidth*1.1)/(self.squaresize + self.linewidth)
        for start in self.starts:
            if abs(start[0] - mgridpos[0]) < startradius and abs(start[1] - mgridpos[1]) < startradius:
                self.trace = Trace(self,
                                [self.wspace//2 + self.linewidth//2 + start[0]*self.gridsquaresize,
                                self.hspace//2 + self.linewidth//2 + start[1]*self.gridsquaresize])
                return True
            
    def snapToExit(self):
        if self.trace.pos[1] < self.hspace//2 + self.linewidth/4:
            self.trace.tryMove(100000000,up)#just max it out, it will stop trying to move up once it hits the barrier
            return True
        elif self.trace.pos[1] > self.hspace//2 + self.gridsquaresize*self.size[1] + self.linewidth - self.linewidth/4:
            self.trace.tryMove(100000000,down)
            return True
        elif self.trace.pos[0] < self.wspace//2 + self.linewidth/4:
            self.trace.tryMove(100000000,left)
            return True
        elif self.trace.pos[0] > self.wspace//2 + self.gridsquaresize*self.size[0] + self.linewidth - self.linewidth/4:
            self.trace.tryMove(100000000,right)
            return True
        
    def checkSolution(self):
        return True
    
    def update(self):
        self.trace.update()
        
    def drawMaze(self, display):
        display.blit(self.mazeimage,(0,0))
        
    def drawStarts(self,display):
        self.startlist = []
        for startpos in self.starts:
            pygame.draw.circle(display,self.gridcolor,
                                (self.wspace//2 + self.linewidth//2 + startpos[0]*self.gridsquaresize + 1,
				self.hspace//2 + self.linewidth//2 + startpos[1]*self.gridsquaresize + 1),
                                int(self.linewidth*1.15))
        
    def drawTrace(self,display):
        self.tracedisplay.fill(clear)
        self.trace.draw(self.tracedisplay)
        #all the sections of the trace need to be faded as one image, otherwise
        #we get issues with transparent surfaces overlapping and being more opaque
        self.tracedisplay.set_alpha(256 - self.trace.fade)
        display.blit(self.tracedisplay,(0,0))

pygame.init()
displaysize = [800,800]
screen = pygame.display.set_mode(displaysize)
clock = pygame.time.Clock()
m1prev = False
is_alive = False
startupdating = False
done = False

display = screen
size = (1,1)
nullzones = ()#((3,0,full),(2,2,full),((1,1),(2,1),1),((1,1),(1,2),1),((0,0),(1,0),1))#((0,4,full),(0,0,full),(4,0,full),(4,4,full))
symbols = ()
starts = ((0,0),)#((2,3),(3,1))
#reminder: when only one tuple in another tuple, needs comma at end to tell python
#it's a tuple tuple, not just a tuple... lol   i.e. ((1,1),)
ends = ((1,0,up),(0,1,left),(1,1,right),(1,1,down))#((2,0,up),(4,0,right),(4,4,right),(4,4,down),(0,4,down),(0,4,left))
hexagons = ()
linefrac = 1/4
endfrac = 3/10
bgcolor = (0,70,205,255)
gridcolor = (25,25,112,255)
tracecolor = white

testmaze = Maze(display,size,nullzones,symbols,starts,ends,hexagons,linefrac,endfrac,bgcolor,gridcolor,tracecolor)

while not done:
    pygame.event.clear()#won't need to get events from pygame event queue, chuck'em
    mousestates = pygame.mouse.get_pressed()
    if mousestates[0] != m1prev:
        mousepos = pygame.mouse.get_pos()
        if m1prev == False:#mouse being pressed
            testmaze.tryStart(mousepos)
        else:#mouse being released
            if testmaze.snapToExit():
                if testmaze.checkSolution():
                    testmaze.trace.is_validated = True
            else:
                testmaze.trace.is_alive = False
            
        m1prev = mousestates[0]
        
    if mousestates[1]:#close program upon middle mouse
        done = True
        
    screen.fill(testmaze.gridcolor)
    testmaze.drawMaze(screen)
    
    testmaze.update()
    testmaze.drawTrace(screen)
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
