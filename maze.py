import pygame

mazesize = (3,3)
if mazesize[0] > mazesize[1]:
    mazeislong = True
else:
    mazeislong = False
        

defaultgrid = []
for i in range(mazesize[0]+1):#make default grid
    defaultgrid.append([])
    for j in range(mazesize[1]):
        defaultgrid[i].append(j)
        

'''displaywidth = 1920#actual values go here
displayheight = 1080
displayspace = 
gridsquareside = displayheight/mazesides
'''

def getgridpos(mousex,mousey):
    if mousex < displayspace or mousex > displaywidth-displayspace:
        return (-1,-1)#outside maze region
    gridx = int((mousex-displayspace)/gridsquareside)#non-exception grid values
    gridy = int(mousey/gridsquareside)
    #"extra" pixels included in last grid square
    if mousex >= displayspace+(gridsquareside*mazeside):
        gridx = mazeside-1
    if mousey > gridsquareside*mazeside:
        gridy = mazeside-1
    return (gridx,gridy)

class Maze():
    def __init__(self, grid = defaultgrid):
        self.grid = grid
    def printself(self):
        for i in self.grid:
            for j in i:
                print(j, end=" ")
            print()

testmaze = Maze()
testmaze.printself()
