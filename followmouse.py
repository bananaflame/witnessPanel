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

class Trace(pygame.sprite.Sprite):
    def __init__(self,startx,starty, width):
        super().__init__()
        self.image = pygame.Surface([width,width])
        self.width = width
        
        self.rect = self.image.get_rect()
        self.rect.x = startx
        self.rect.y = starty

        self.image.fill(red)
        #pygame.draw.circle(self.image,red,(self.rect.x,self.rect.y),5)
        

    def update(self,walls):
        
        mousepos = pygame.mouse.get_pos()
        diffx = mousepos[0] - (self.rect.x + self.width/2) #diff between center of line head and mouse, not top left corner
        diffy = -mousepos[1] + (self.rect.y+ self.width/2) #reversed bc display y-axis is flipped

        #determine primary axis
        if abs(diffy) > abs(diffx):
            primeaxis = up
        else:
            primeaxis = right
        #determine primary direction, can maybe be cleaned up
        if primeaxis == right:#x is primary axis
            if diffx > 0:
                primedir = right
            else:
                primedir = left
                
            if diffy > 0:
                secdir = up
            else:
                secdir = down
        else:#y is primary axis
            if diffy > 0 :
                primedir = up
            else:
                primedir = down

            if diffx > 0:
                secdir = right
            else:
                secdir = left

        if primeaxis == up and abs(diffy) > 3:
            if not self.trymove(primedir, abs(diffy/10), walls):
                self.trymove(secdir, abs(diffx/10), walls)
        if primeaxis == right and abs(diffx) > 3:
            if not self.trymove(primedir, abs(diffx/10), walls):
                self.trymove(secdir, abs(diffy/10), walls)
                #this doesn't work with hypot
                #probably need to rearrange trymove, have multiple based on directions

    def trymove(self, direction, distance, walls):
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
#pygame.mouse.set_visible(False)
displaysize = [600,400]
screen = pygame.display.set_mode(displaysize)
clock = pygame.time.Clock()
done = False

testtrace = Trace(0,0,15)
tracelist = pygame.sprite.Group()
tracelist.add(testtrace)

wall = Wall(100,100,40,40,blue)
wall2 = Wall(155,100,40,40,blue)
wall3 = Wall(210,100,40,40,blue)
wall4 = Wall(100,155,40,40,blue)
wall5 = Wall(155,155,40,40,blue)
wall6 = Wall(210,155,40,40,blue)
wall7 = Wall(100,50,150,35,blue)
wall8 = Wall(65,50,35,135,blue)
walllist = pygame.sprite.Group()
walllist.add(wall,wall2,wall3,wall4,wall5,wall6,wall7,wall8)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #close window on quit
            done = True 

    screen.fill(white)
    tracelist.update(walllist)
    tracelist.draw(screen)
    walllist.draw(screen)
    pygame.display.flip()
    clock.tick(60)
    
    
pygame.quit()
