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
        squaresize = screenrect.w // (self.size[0] + (self.linefrac*self.size[0]) + 4*self.linefrac)
        self.longside = right
        #test if that squaresize is compatible with vertical dimension, if it bleeds over vertical is limiting
        if squaresize*(1+self.linefrac)*self.size[1] + squaresize*self.linefrac > screenrect.h:
            squaresize = screenrect.h // (self.size[1] + (self.linefrac*self.size[1]) + 4*self.linefrac)
            self.longside = up
        squaresize = int(squaresize)
        self.linewidth = int(squaresize*self.linefrac)#I need the pixel value of self.linewidth more after this, so this will be useful
        
        widthspace = int(screenrect.w - ((squaresize+self.linewidth)*self.size[0] + self.linewidth))
        heightspace = int(screenrect.h - ((squaresize+self.linewidth)*self.size[1] + self.linewidth))
        
        self.walls = pygame.sprite.Group()
        self.walls.add(Wall(0,0,widthspace//2,
                            screenrect.h,self.bgcolor))#left boundary
        self.walls.add(Wall(((squaresize+self.linewidth)*self.size[0] + self.linewidth)+ widthspace//2,0,
                            screenrect.w,screenrect.h,self.bgcolor))#right boundary
        self.walls.add(Wall(widthspace//2,0,
                            screenrect.w-widthspace//2,heightspace//2,self.bgcolor))#top boundary
        self.walls.add(Wall(widthspace//2,((squaresize+self.linewidth)*self.size[1] + self.linewidth)+heightspace//2,
                            ((squaresize+self.linewidth)*self.size[0] + self.linewidth)+ widthspace//2,screenrect.h,self.bgcolor))#bottom boundary
        
        #add grid squares, these for loops might be redundant with creation of self.grid earlier, clean up
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                squarex = widthspace//2+self.linewidth+(x*(squaresize+self.linewidth))
                squarey = heightspace//2+self.linewidth+(y*(squaresize+self.linewidth))
                print("Making wall with "+str(squarex)+", "+str(squarey)+", "+str(squarex+squaresize)+", "+str(squarey+squaresize))
                self.walls.add(Wall(squarex,squarey,squaresize,squaresize,(50*x,50*y,0)))
                                


    def drawMaze(self, display):
        self.walls.draw(display)#maybe blit instead of drawing walls each time?
        
class Trace(pygame.sprite.Sprite):
    def __init__(self,startx,starty, width, color):
        super().__init__()
        self.image = pygame.Surface([width,width])
        self.width = width
        self.color = color
        
        self.rect = self.image.get_rect()
        self.rect.x = startx
        self.rect.y = starty

        self.image.fill(self.color)
        #pygame.draw.circle(self.image,red,(self.rect.x,self.rect.y),5)
        
    def update(self,walls):
        mousepos = pygame.mouse.get_pos()
        diffx = mousepos[0] - (self.rect.x + self.width/2) #diff between center of line head and mouse, not top left corner
        diffy = -mousepos[1] + (self.rect.y+ self.width/2) #reversed bc display y-axis is flipped
        fractiontomove = 6
        if abs(diffy) > abs(diffx):#primary axis is up/down
            if abs(diffy) > 3:#prevents movement when cursor close enough to center
                if diffy > 0 :
                    can_move_prime = self.trymove(up,abs(diffy)/fractiontomove,walls)
                else:
                    can_move_prime = self.trymove(down,abs(diffy)/fractiontomove,walls)

                if not can_move_prime and abs(diffx) > 3:
                    if diffx > 0:
                        self.trymove(right,abs(diffx)/fractiontomove,walls)
                    else:
                        self.trymove(left,abs(diffx)/fractiontomove,walls)
        else:#primary axis is left/right
            if abs(diffx) > 3:
                if diffx > 0:
                    can_move_prime = self.trymove(right,abs(diffx)/fractiontomove,walls)
                else:
                    can_move_prime = self.trymove(left,abs(diffx)/fractiontomove,walls)
                    
                if not can_move_prime and abs(diffy) > 3:
                    if diffy > 0:
                        self.trymove(up,abs(diffy)/fractiontomove,walls)
                    else:
                        self.trymove(down,abs(diffy)/fractiontomove,walls)

    def trymove(self, direction, dist_to_move, walls):
        distance = math.ceil(dist_to_move) #always try to move at least 1 pixel
        if direction == up:
            self.rect.y -= distance #don't forget display y-axis is reverse
            collisions = pygame.sprite.spritecollide(self, walls, False)
            for wall in collisions:
                self.rect.top = wall.rect.bottom
                return False
        elif direction == right:
            self.rect.x += distance
            collisions = pygame.sprite.spritecollide(self, walls, False)
            for wall in collisions:
                self.rect.right = wall.rect.left
                return False
        elif direction == down:
            self.rect.y += distance #don't forget display y-axis is reverse
            collisions = pygame.sprite.spritecollide(self, walls, False)
            for wall in collisions:
                self.rect.bottom = wall.rect.top
                return False
        elif direction == left:
            self.rect.x -= distance
            collisions = pygame.sprite.spritecollide(self,walls,False)
            for wall in collisions:
                self.rect.left = wall.rect.right
                return False
        return True

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
 
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        
pygame.init()
displaysize = [600,400]
screen = pygame.display.set_mode(displaysize)
clock = pygame.time.Clock()
done = False
testmaze = Maze(screen,(3,3),(),(),(),1/6,blue,green)
#testmaze.printself()

testtrace = Trace(100,100,testmaze.linewidth,black)
tracelist = pygame.sprite.Group()
tracelist.add(testtrace)

while not done:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
    screen.fill(testmaze.gridcolor)
    testmaze.drawMaze(screen)
    tracelist.update(testmaze.walls)
    tracelist.draw(screen)
    pygame.display.flip()
    clock.tick(60)
    
    
pygame.quit()
