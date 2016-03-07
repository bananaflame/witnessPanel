import pygame
import math

black = (  0,  0,    0)
white = (255, 255, 255)
blue =  (  0,   0, 255)
green = (  0, 255,   0)
red =   (255,   0,   0)
up = 0
right = 1
down = 2
left = 3
defaultsize = (3,2)
defaultnullzones = (((1,0),(2,0)),#there might be an easier way to store this data
                    ((1,0),(1,1)))

class TraceStart(pygame.sprite.Sprite):
    def __init__(self, position, radius, color):
        super().__init__()
        self.fullradius = radius
        self.color = color
        self.currentradius = self.fullradius//3
        self.is_alive = True
        self.image = pygame.Surface([radius*2,radius*2])
        self.image.set_colorkey((1,1,1))#makes everything that's that color transparent
        self.rect = self.image.get_rect()
        self.rect.y = position[0] - radius
        self.rect.x = position[1] - radius
        
        
    def draw(self, display):#only sprite groups have draw method, only need one trace head so I put this in
        display.blit(self.image, self.rect)
        
class TraceBody():
    pass

class TraceHead(pygame.sprite.Sprite):
    def __init__(self, startpos, color, width):
        super().__init__()
        self.width = width
        self.image = pygame.Surface([self.width,self.width])
        self.color = color
        self.timedead = 0
        self.rect = self.image.get_rect()
        self.rect.x = startpos[0]
        self.rect.y = startpos[1]
        self.image.fill((1,1,1))
        self.image.set_colorkey((1,1,1))#makes everything that's that color transparent
        pygame.draw.circle(self.image,self.color,(self.width//2,self.width//2),self.width//2)
        
    def draw(self, display):#only sprite groups have draw method, only need one trace head so I put this in
        display.blit(self.image, self.rect)

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
        self.longside = right
        #test if that self.squaresize is compatible with vertical dimension, if it bleeds over vertical is limiting
        if self.squaresize*(1+self.linefrac)*self.size[1] + 4*self.squaresize*self.linefrac > self.screenrect.h:
            self.squaresize = self.screenrect.h // (self.size[1] + (self.linefrac*self.size[1]) + 4*self.linefrac)
            self.longside = up
        self.squaresize = int(self.squaresize)
        self.linewidth = int(self.squaresize*self.linefrac)#I need the pixel value of self.linewidth more after this, so this will be useful
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
                                int(self.linewidth*1.1))
            
    def tryStart(self,mousepos):
        mgridpos = [(mousepos[0] - (self.wspace//2) - self.linewidth//2)/(self.squaresize+self.linewidth),
                   (mousepos[1] - (self.hspace//2) - self.linewidth//2)/(self.squaresize+self.linewidth)]
        startradius = (self.linewidth*1.1)/(self.squaresize + self.linewidth)
        for start in self.starts:
            if abs(start[0] - mgridpos[0]) < startradius and abs(start[1] - mgridpos[1]) < startradius:
                self.tracestart = TraceStart((self.wspace//2 + self.linewidth//2 + start[0]*(self.squaresize+self.linewidth),
                                                self.hspace//2 + self.linewidth//2 + start[1]*(self.squaresize+self.linewidth)),
                                                int(testmaze.linewidth*1.1),
                                                self.tracecolor)
                self.tracebody = TraceBody()
                self.tracehead = TraceHead((self.wspace//2 + start[0]*(self.squaresize+self.linewidth),
                                                 self.hspace//2 + start[1]*(self.squaresize+self.linewidth)),
                                                 self.tracecolor, self.linewidth)
                return True
            
    def update(self):
        #updateMaze() for flashing wrong symbols
        self.updateTraceStart()
        self.updateTraceBody()
        self.updateTraceHead()
        
    def updateTraceStart(self):#if I didn't have the update methods for the three sections of trace in Maze class,
                                        #I would need to pass maze data to each object's update() for collisions and stuff
        self.tracestart.image.fill((1,1,1))
        if self.tracestart.fullradius - self.tracestart.currentradius > 10:
            self.tracestart.currentradius += 5
        elif self.tracestart.currentradius < self.tracestart.fullradius:
            self.tracestart.currentradius += 1
        pygame.draw.circle(self.tracestart.image, self.tracecolor,
                          (self.tracestart.fullradius,self.tracestart.fullradius),
                           self.tracestart.currentradius)
        
        
    def updateTraceBody(self):
        pass
    
    def updateTraceHead(self):
        mousepos = pygame.mouse.get_pos()
        diffx = mousepos[0] - (self.tracehead.rect.x + self.tracehead.width/2) #diff between center of line head and mouse, not top left corner
        diffy = -mousepos[1] + (self.tracehead.rect.y + self.tracehead.width/2) #reversed bc display y-axis is flipped
        fractiontomove = 4
        gridpos = [(self.tracehead.rect.x - (self.wspace//2))/(self.squaresize+self.linewidth),
                   (self.tracehead.rect.y - (self.hspace//2))/(self.squaresize+self.linewidth)]
        if abs(diffy) > abs(diffx):#primary axis is up/down
            if gridpos[0].is_integer(): #trace is on grid column, can move up/down
                if diffy > 2:
                    self.tryMoveTraceHead(up,diffy/fractiontomove)
                elif diffy < -2:
                    self.tryMoveTraceHead(down,abs(diffy)/fractiontomove)
            else: #can't move up/down, try left/right
                if diffx > 2:
                    self.tryMoveTraceHead(right,diffx/fractiontomove)
                elif diffx < -2:
                    self.tryMoveTraceHead(left,abs(diffx)/fractiontomove)
                elif abs(diffy) > self.squaresize//5:#if cursor getting far away, check if can snap to intersection
                    disttoisect = (self.tracehead.rect.x - (self.wspace//2))%(self.squaresize+self.linewidth)
                    if disttoisect <= self.tracehead.width:#trace is 1 linewidth right of intersection 
                        self.tryMoveTraceHead(left,disttoisect)
                    elif disttoisect >= (self.squaresize+self.linewidth) - self.tracehead.width:#trace is 1 linewidth left of intersection
                        self.tryMoveTraceHead(right,(self.squaresize+self.linewidth) - disttoisect)
        else:#primary axis is left/right
            if gridpos[1].is_integer(): #trace is on grid row, can move up/down as long as no border in way
                if diffx > 2:
                    self.tryMoveTraceHead(right,diffx/fractiontomove)
                elif diffx < -2:
                    self.tryMoveTraceHead(left,abs(diffx)/fractiontomove)
            else: #can't move left/right, try up/down
                if diffy > 2:
                    self.tryMoveTraceHead(up,diffy/fractiontomove)
                elif diffy < -2:
                    self.tryMoveTraceHead(down,abs(diffy)/fractiontomove)
                elif abs(diffx) > self.squaresize//5:#if cursor getting far away, check if can snap to intersection
                    disttoisect = (self.tracehead.rect.y - (self.hspace//2))%(self.squaresize+self.linewidth)
                    if disttoisect <= self.tracehead.width:#trace is 1 linewidth below intersection 
                        self.tryMoveTraceHead(up,disttoisect)
                    elif disttoisect >= (self.squaresize+self.linewidth) - self.tracehead.width:#trace is one linewidth above intersection
                        self.tryMoveTraceHead(down,(self.squaresize+self.linewidth) - disttoisect)
            
    def tryMoveTraceHead(self,direction,dist_to_move):
        distance = math.ceil(dist_to_move) #always try to move at least 1 pixel
        collisions = []
        if direction == up:
            for i in range(distance):
                if not collisions:
                    self.tracehead.rect.y -= 1 #don't forget display y-axis is reverse
                    collisions = pygame.sprite.spritecollide(self.tracehead, self.walls, False)
                    for wall in collisions:
                        self.tracehead.rect.top = wall.rect.bottom
        elif direction == right:
            for i in range(distance):
                if not collisions:
                    self.tracehead.rect.x += 1
                    collisions = pygame.sprite.spritecollide(self.tracehead, self.walls, False)
                    for wall in collisions:
                        self.tracehead.rect.right = wall.rect.left
        elif direction == down:
            for i in range(distance):
                if not collisions:
                    self.tracehead.rect.y += 1 #don't forget display y-axis is reverse
                    collisions = pygame.sprite.spritecollide(self.tracehead, self.walls, False)
                    for wall in collisions:
                        self.tracehead.rect.bottom = wall.rect.top
        elif direction == left:
            for i in range(distance):
                if not collisions:
                    self.tracehead.rect.x -= 1
                    collisions = pygame.sprite.spritecollide(self.tracehead,self.walls,False)
                    for wall in collisions:
                        self.tracehead.rect.left = wall.rect.right
                        
    def drawMaze(self, display):
        self.walls.draw(display)
        self.drawStarts(display)
        
    def drawTrace(self,display):
        self.tracestart.draw(display)
        #self.tracebody.draw(display)
        self.tracehead.draw(display)
        


pygame.init()
displaysize = [700,700]
screen = pygame.display.set_mode(displaysize)
clock = pygame.time.Clock()
m1prev = False
is_alive = False
startupdating = False
done = False

testmaze = Maze(screen,(3,3),(),
                (),((0,0),(1,1)),(),(),
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
        testmaze.update()
        testmaze.drawTrace(screen)
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
