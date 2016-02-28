import pygame

black = (  0,  0,    0)
white = (255, 255, 255)
blue =  (  0,   0, 255)
green = (  0, 255,   0)
red =   (255,   0,   0)

up = 0
right = 1

defaultsize = (3,2)
defaultnullzones = (((1,0),(2,0)),#there might be an easier way to store this data
                    ((1,0),(1,1)))

class Maze():
    def __init__(self, display, size, nullzones, symbols, inlines, linewidth, bgcolor, gridcolor):
        self.size = size #tuple with (x,y)
        self.nullzones = nullzones #see default above
        self.symbols = symbols #tuple with (x,y), relative to squares, not intersections
        self.inlines = inlines #starts, ends, and hexagons, unsure of formatting
        self.linewidth = linewidth #should be a fraction, i.e. 1/4 for 1/4 the size of squares
        self.bgcolor = bgcolor
        self.gridcolor = gridcolor
        
        self.grid = []
        for y in range(size[0]):
            self.grid.append([])
            for x in range(size[1]):
                self.grid[y].append(0)

        self.generateMazeImage(display)
        
    def printMaze(self):
        for i in self.grid:
            for j in i:
                print(j, end=" ")
            print()
            
    def generateMazeImage(self,display):
        image = display.copy()
        image.fill(self.bgcolor)
        screenrect = display.get_rect()
        print(screenrect)
        print(screenrect.w)
        print(screenrect.h)
        #get largest possible square size (remember linewidth is fraction of square size, like 1/4)
        #includes space in between squares and 1 line width worth of buffer around the edges
        squaresize = screenrect.w // (self.size[0] + (2*self.linewidth*self.size[0]) + self.linewidth)
        print("first squaresize is "+str(squaresize))
        self.longside = right
        print(str(self.size[1])+"is self size 1")
        print("if "+str(squaresize*(1+self.linewidth)*self.size[1])+str(squaresize*self.linewidth)+"greater than "+str(screenrect.h))
        if squaresize*(1+self.linewidth)*self.size[1] + squaresize*self.linewidth > screenrect.h:
            squaresize = screenrect.h // (self.size[1] + (2*self.linewidth*self.size[1]) + self.linewidth)
            print("squaresize is vertical, - "+str(squaresize)) 
            self.longside = up
        squaresize = int(squaresize)
        
        widthspace = int(screenrect.w - (squaresize*(1+self.linewidth)*self.size[0] + squaresize*self.linewidth))
        heightspace = int(screenrect.h - (squaresize*(1+self.linewidth)*self.size[1] + squaresize*self.linewidth))

        print("widthspace is: "+str(widthspace))
        print("heightspace is: "+str(heightspace))

        
        self.walls = pygame.sprite.Group()
        self.walls.add(Wall(0,0,widthspace//2,screenrect.h,red))#left boundary
        self.walls.add(Wall(screenrect.w-widthspace//2,0,screenrect.w,screenrect.h,red))
        print("adding wall: ")
        print(str(widthspace//2)+", 0, "+str(screenrect.w-widthspace//2)+", "+str(heightspace//2))
        self.walls.add(Wall(widthspace//2,0,screenrect.w-widthspace//2,heightspace//2,red))
        self.walls.add(Wall(widthspace//2,screenrect.h-heightspace//2,screenrect.w-widthspace//2,screenrect.h,red))
        

    def drawMaze(self, display):
        self.walls.draw(display)

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
testmaze = Maze(screen,(2,2),(),(),(),1/6,blue,green)
#testmaze.printself()
            
while not done:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
    #screen.fill(white)
    testmaze.drawMaze(screen)
    pygame.display.flip()
    clock.tick(60)
    
    
pygame.quit()

