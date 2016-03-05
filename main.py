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

class Maze():
    def __init__(self, display, size, nullzones, symbols, inlines, linefrac, bgcolor, gridcolor):
        self.size = size #tuple with (x,y)
        self.nullzones = nullzones #see default above
        self.symbols = symbols #tuple with (x,y), relative to squares, not intersections
        self.inlines = inlines #starts, ends, and hexagons, unsure of formatting
        self.linefrac = linefrac #should be a fraction, i.e. 1/4 for 1/4 the size of squares
        self.bgcolor = bgcolor #color of squares and border
        self.gridcolor = gridcolor #color of grid lines
        
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
        image.fill(self.bgcolor)
        screenrect = display.get_rect()
        #get largest possible square size (remember linefrac is fraction of square size, like 1/4)
        #includes space in between squares and 1.5x line width worth of buffer on both bounding edges
        self.squaresize = screenrect.w // (self.size[0] + (self.linefrac*self.size[0]) + 4*self.linefrac)
        self.longside = right
        #test if that self.squaresize is compatible with vertical dimension, if it bleeds over vertical is limiting
        if self.squaresize*(1+self.linefrac)*self.size[1] + 4*self.squaresize*self.linefrac > screenrect.h:
            self.squaresize = screenrect.h // (self.size[1] + (self.linefrac*self.size[1]) + 4*self.linefrac)
            self.longside = up
        self.squaresize = int(self.squaresize)
        self.linewidth = int(self.squaresize*self.linefrac)#I need the pixel value of self.linewidth more after this, so this will be useful
        
        self.wspace = int(screenrect.w - ((self.squaresize+self.linewidth)*self.size[0] + self.linewidth))
        self.hspace = int(screenrect.h - ((self.squaresize+self.linewidth)*self.size[1] + self.linewidth))
        
        self.walls = pygame.sprite.Group()
        self.walls.add(Wall(0,0,self.wspace//2,
                            screenrect.h,self.bgcolor))#left boundary
        self.walls.add(Wall(((self.squaresize+self.linewidth)*self.size[0] + self.linewidth)+ self.wspace//2,0,
                            screenrect.w,screenrect.h,self.bgcolor))#right boundary
        self.walls.add(Wall(self.wspace//2,0,
                            screenrect.w-self.wspace//2,self.hspace//2,self.bgcolor))#top boundary
        self.walls.add(Wall(self.wspace//2,((self.squaresize+self.linewidth)*self.size[1] + self.linewidth)+self.hspace//2,
                            ((self.squaresize+self.linewidth)*self.size[0] + self.linewidth)+ self.wspace//2,screenrect.h,self.bgcolor))#bottom boundary
        
        #add grid squares, these for loops might be redundant with creation of self.grid earlier, clean up
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                squarex = self.wspace//2+self.linewidth+(x*(self.squaresize+self.linewidth))
                squarey = self.hspace//2+self.linewidth+(y*(self.squaresize+self.linewidth))
                self.walls.add(Wall(squarex,squarey,self.squaresize,self.squaresize,(50*x,50*y,0)))
                                


    def drawMaze(self, display):
        self.walls.draw(display)#maybe blit instead of drawing walls each time?
        
class Trace(pygame.sprite.Sprite):
    def __init__(self, maze, startx, starty, color):
        super().__init__()
        self.maze = maze
        self.width = maze.linewidth
        self.image = pygame.Surface([self.width,self.width])
        self.color = color
        
        self.rect = self.image.get_rect()
        self.rect.x = startx
        self.rect.y = starty

        self.image.fill(self.color)
        #pygame.draw.circle(self.image,red,(self.rect.x,self.rect.y),5)
        
    def update(self):
        mousepos = pygame.mouse.get_pos()
        diffx = mousepos[0] - (self.rect.x + self.width/2) #diff between center of line head and mouse, not top left corner
        diffy = -mousepos[1] + (self.rect.y+ self.width/2) #reversed bc display y-axis is flipped
        fractiontomove = 6

        gridpos = [(self.rect.x - (self.maze.wspace//2))/(self.maze.squaresize+self.maze.linewidth),
                   (self.rect.y - (self.maze.hspace//2))/(self.maze.squaresize+self.maze.linewidth)]

        if abs(diffy) > abs(diffx):#primary axis is up/down
            if gridpos[0].is_integer(): #trace is on grid column, can move up/down
                if diffy > 2:
                    self.trymove(up,diffy/fractiontomove)
                elif diffy < -2:
                    self.trymove(down,abs(diffy)/fractiontomove)
            else: #can't move up/down, try left/right
                if diffx > 2:
                    self.trymove(right,diffx/fractiontomove)
                elif diffx < -2:
                    self.trymove(left,abs(diffx)/fractiontomove)
                elif abs(diffy) > self.maze.squaresize//2:#if cursor getting far away, check if can snap to intersection
                    disttoisect = (self.rect.x - (self.maze.wspace//2))%(self.maze.squaresize+self.maze.linewidth)
                    if disttoisect <= self.width:#trace is 1 linewidth right of intersection 
                        self.trymove(left,disttoisect)
                    elif disttoisect >= (self.maze.squaresize+self.maze.linewidth) - self.width:#trace is 1 linewidth left of intersection
                        self.trymove(right,(self.maze.squaresize+self.maze.linewidth) - disttoisect)
        else:#primary axis is left/right
            if gridpos[1].is_integer(): #trace is on grid row, can move up/down as long as no border in way
                if diffx > 2:
                    self.trymove(right,diffx/fractiontomove)
                elif diffx < -2:
                    self.trymove(left,abs(diffx)/fractiontomove)
            else: #can't move left/right, try up/down
                if diffy > 2:
                    self.trymove(up,diffy/fractiontomove)
                elif diffy < -2:
                    self.trymove(down,abs(diffy)/fractiontomove)
                elif abs(diffx) > self.maze.squaresize//2:#if cursor getting far away, check if can snap to intersection
                    disttoisect = (self.rect.y - (self.maze.hspace//2))%(self.maze.squaresize+self.maze.linewidth)
                    if disttoisect <= self.width:#trace is 1 linewidth below intersection 
                        self.trymove(up,disttoisect)
                    elif disttoisect >= (self.maze.squaresize+self.maze.linewidth) - self.width:#trace is one linewidth above intersection
                        self.trymove(down,(self.maze.squaresize+self.maze.linewidth) - disttoisect)

    def trymove(self, direction, dist_to_move):
        distance = math.ceil(dist_to_move) #always try to move at least 1 pixel
        collisions = []
        if direction == up:
            for i in range(distance):
                if not collisions:
                    self.rect.y -= 1 #don't forget display y-axis is reverse
                    collisions = pygame.sprite.spritecollide(self, self.maze.walls, False)
                    for wall in collisions:
                        self.rect.top = wall.rect.bottom
        elif direction == right:
            for i in range(distance):
                if not collisions:
                    self.rect.x += 1
                    collisions = pygame.sprite.spritecollide(self, self.maze.walls, False)
                    for wall in collisions:
                        self.rect.right = wall.rect.left
        elif direction == down:
            for i in range(distance):
                if not collisions:
                    self.rect.y += 1 #don't forget display y-axis is reverse
                    collisions = pygame.sprite.spritecollide(self, self.maze.walls, False)
                    for wall in collisions:
                        self.rect.bottom = wall.rect.top
        elif direction == left:
            for i in range(distance):
                if not collisions:
                    self.rect.x -= 1
                    collisions = pygame.sprite.spritecollide(self,self.maze.walls,False)
                    for wall in collisions:
                        self.rect.left = wall.rect.right

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
 
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        
pygame.init()
displaysize = [800,800]
screen = pygame.display.set_mode(displaysize)
clock = pygame.time.Clock()
done = False
testmaze = Maze(screen,(6,5),(),(),(),1/4,blue,green)
#testmaze.printself()

testtrace = Trace(testmaze,100,100,black)
tracelist = pygame.sprite.Group()
tracelist.add(testtrace)

while not done:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
    screen.fill(testmaze.gridcolor)
    testmaze.drawMaze(screen)
    tracelist.update()
    tracelist.draw(screen)
    pygame.display.flip()
    clock.tick(60)
    
    
pygame.quit()
