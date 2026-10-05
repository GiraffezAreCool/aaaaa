import tkinter as tk

screen = tk.Tk()

health = 100
score = 0
treasure = 0
powerup = False

city = []

running = True

for x in range(5):
    city.append([])
    for y in range(5):
        city[x].append(" . ")
        
        

city[0][0] = "D"   
city[0][4] = "T" 
city[1][3] = "E" 
city[3][1] = "E"
city[3][3] = "P"
city[4][4] = "S"        

def display():
    for widget in screen.winfo_children():
        widget.destroy()
    for x in range(25):
        name = f"square{x}"
        label = tk.Label(screen, text=city[x%5][x//5], font = ("Arial", 65))
        label.grid(padx = 20, pady = 10, column = x%5, row = x//5)

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
    
def move(dx, dy):
    global score, running, powerup
    x, y = find()
    nx, ny = x+dx, y+dy
    if nx > 4 or ny > 4 or nx < 0 or ny < 0:
        print("Invalid")
        return
    else:
        if city[nx][ny] == " . ":
            city[x][y] = " . "
            city[nx][ny] = "D"
        elif city[nx][ny] == "P":
            powerup = True
            city[x][y] = " . "
            city[nx][ny] = "D"
        elif city[nx][ny] == "E":
            fight(nx, ny)
            city[x][y] = " . "
            city[nx][ny] = "D"
        elif city[nx][ny] == "T":
            score += 500
            city[x][y] = " . "
            city[nx][ny] = "D"
        else:
            print("You win")
            city[x][y] = " . "
            city[nx][ny] = "D"
            running = False
    
def fight(nx, ny):
    global score
    if nx > 4 or ny > 4 or nx < 0 or ny <  0 or city[nx][ny] != "E":
        print("Invalid")
        return
    else:
        city[nx][ny] = "."
        score += 100
        
def usepowerup():
    global health
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

screen.title("Dragon Game")
screen.geometry("600x600")
screen.configure(bg="#ffffff")


while running:
    display()
    screen.update()
    valid = False
    while not valid:
        user = input("Move: ")
        if user == "w":
            move(0, -1)
            valid = True
        elif user == "a":
            move(-1, 0)
            valid = True
        elif user == "s":
            move(0, 1)
            valid = True
        elif user == "d":
            move(1, 0)
            valid = True
        elif user == "p" and powerup == True:
            usepowerup()
            valid = True
        else:
            print("Invalid move")
    if powerup == True:
        print("Score:", score, "| Health:", health, "|Powerup: Yes")
    else:
        print("Score:", score, "| Health:", health, "|Powerup: No")
screen.mainloop()
