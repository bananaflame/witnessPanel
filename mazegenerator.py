#code for generating maze files:

size = (3,3)
nullzones = ()
squares = ((1,0,black),(1,2,white),(0,2,black),(2,2,black),(0,3,white),(1,3,white),(2,3,white),(0,1,black),(3,0,black),(3,1,black),(3,3,black),(2,0,white))
stars = ()
starts = ((0,4),)
#reminder: when only one tuple in another tuple, needs comma at end to tell python
#it's a tuple tuple, not just a tuple... lol   i.e. ((1,1),)
ends = ((3,4,down),)
hexagons = ()
linefrac = 0.26
endfrac = 1/5
bgcolor = (0,70,205,255)
gridcolor = (25,25,112,255)
tracecolor = white
tracecorrectcolor = (180,180,255)
tracewrongcolor = black
attributes = [size,nullzones,starts,ends,hexagons,squares,stars,linefrac,endfrac,bgcolor,gridcolor,tracecolor,tracecorrectcolor,tracewrongcolor]
attributes = [(3,3), (), ((2, 3),), ((2, 0, 0),), (), (), ((0, 0, (255, 150, 36)),(2,2, (255, 150, 36)),(1, 2, (255, 150, 36)),(0, 2, (255, 150, 36)),(2, 0, (255, 150, 36)),(1, 0, (255, 150, 36)),), 0.3333333333333333, 0.3333333333333333, (120, 120, 138), (50, 50, 54), (255, 255, 255), (255, 150, 36), (0, 0, 0)]
series = "series name"
numinseries = "number_in_series"


if not os.path.exists("puzzles/"+series):
    os.makedirs("puzzles/"+series)
    
mazefile = open("puzzles/"+series+"/"+numinseries+".maze","wb")
pickle.dump(attributes,mazefile,-1)
mazefile.close()
'
