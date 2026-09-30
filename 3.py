health = 100
score = 0
treasure = 0


city = []

for x in range(5):
    city.append([])
    for y in range(5):
        city[x].append(".")
        
        

city[0][0] = "D"   
city[0][4] = "T" 
city[1][3] = "E" 
city[3][1] = "E"
city[3][3] = "P"
city[4][4] = "S"        

def display():
    for x in range(5):
        print(city[x], "\n")
    
def find():
    for x in range(5):
        for y in range(5):
            if  city[x][y] == "D":
                return x, y
    
def count():
    enemies = 0
    for x in range(5):
        for y in range(5):
            if  city[x][y] == "E":
                enemies += 1
                
    print("Enemies:", enemies)
    
def move(dx, dy):
    x, y = find()
    nx, ny = x+dx, y+dy
    if nx > 4 or ny > 4:
        print("Invalid")
        return
    else:
        city[x][y] = "."
        city[nx][ny] = "D"
    
def fight():
    x, y = find()
    nx, ny = x+dx, y+dy
    if nx >  or ny > 4:
        print("Invalid")
        return
    else:
        city[nx][ny] = "."
        
def powerup():
    health += 20

def checkWin():
    x, y, = find()
    if x == 4 and y == 4:
        print("Win")
    else:
        print("You didn't win yet!")
        
def stats():
    print("Health:", health)
    print("Score:", score)
    print("Treasure:", treasure)
        

    
                
                
        
