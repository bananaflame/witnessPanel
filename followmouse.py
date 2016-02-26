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

        if abs(diffy) > abs(diffx):#primary axis is up/down
            if abs(diffy) > 3:#prevents movement when cursor close enough to center
                if diffy > 0 :
                    can_move_prime = self.trymove(up,abs(diffy)/10,walls)
                else:
                    can_move_prime = self.trymove(down,abs(diffy)/10,walls)

                if not can_move_prime and abs(diffx) > 3:
                    if diffx > 0:
                        self.trymove(right,abs(diffx)/10,walls)
                    else:
                        self.trymove(left,abs(diffx)/10,walls)
        else:#primary axis is left/right
            if abs(diffx) > 3:
                if diffx > 0:
                    can_move_prime = self.trymove(right,abs(diffx)/10,walls)
                else:
                    can_move_prime = self.trymove(left,abs(diffx)/10,walls)
                    
                if not can_move_prime and abs(diffy) > 3:
                    if diffy > 0:
                        self.trymove(up,abs(diffy)/10,walls)
                    else:
                        self.trymove(down,abs(diffy)/10,walls)

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
