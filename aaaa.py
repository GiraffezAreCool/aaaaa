import pygame
import random
pygame.init()
# Projection of screen
W = 960
H = 610
screen =pygame.display.set_mode((W,H))
pygame.display.set_caption("Tuff Dragon City")
# Colour and blocks
ROWS = 8
COLS = 10
CELL = 58
BOARD_X = 35
BOARD_Y = 65
EMPTY = (38,48,63)
GRID = (75,85,100)
BG = (20,25,35)
font = pygame.font.Font(None,32)
small = pygame.font.Font(None,24)
big = pygame.font.Font(None,42)

BG = (20,25,35)
WHITE = (240,240,240)
BLUE = (60,150,255)
RED = (220,70,70)
PURPLE = (175,95,230)
GREEN = (65,195,105)
YELLOW = (200,150,25)
GREY = (90,95,105)
ORANGE = (200,100,0)
MAROON = (200,10,100)

# Parent class
class Object():
    def __init__(self,x,y,board):
        self.x = x
        self.y = y
        self.board = board
        self.symbol = "O"
        board.addObject(self)

    # Movement :)
    def move(self, dx, dy):
        nx = self.x+dx
        ny = self.y+dy
        if not self.board.On(nx,ny):
            return
        if self.board.board[nx][ny]!= "":
            return
        if (nx,ny) == self.board.safeZone:
            return
        self.board.removeObject(self)
        self.x =nx
        self.y= ny
        self.board.addObject(self)

# User playing the game and stats

class Player(Object):
    def __init__(self, x, y, board, DT):
        super().__init__(x, y, board)
        self.symbol ="D"
        self.score = 0
        self.alive = True
        self.dt = DT
        # Dragon type
        if DT== 1:
            self.name = "Fire"
            self.hp = 100
            self.dmg = 2
        elif DT == 2:
            self.name = "Tank"
            self.hp = 150
            self.dmg = 1
        else:
            self.name = "Heal"
            self.hp = 100
            self.dmg = 1
        # Healllinggg + feezzingg
        self.maxHp = self.hp
        self.healUsed = False
        self.freezes = 2
        board.player = self
        # Set that player doesn't have key
        self.key = False

    # Collects items and adds points
    def move(self, dx,dy):
        nx = self.x+dx
        ny = self.y+dy

        if not self.board.On(nx,ny):
            return

        if (nx,ny) == self.board.safeZone and not self.key:
            print("EXIT LOCKED :(  -  GET KEY")
            return

        if self.board.occupied(nx,ny):
            return

        item =self.board.board[nx][ny]

        # Validating collection of items
        if isinstance(item, Treasure):
            self.score+= 100
            self.board.removeObject(item)

        elif isinstance(item, Key):
            self.key = True
            self.board.removeObject(item)
            print("KEY FOUND!!!!")

        self.board.removeObject(self)
        self.x = nx
        self.y = ny
        self.board.addObject(self)

        # WIN
        if (self.x,self.y) == self.board.safeZone and self.key:
            self.board.levelComplete = True
            print("LEVEL COMPLETE!")

    # Attack !!
    def attack(self, dx, dy):
        nx = self.x+dx
        ny = self.y+dy

        if not self.board.On(nx,ny):
            return

        if not self.board.EP(nx,ny):
            return

        enemy = self.board.board[nx][ny]
        enemy.takeDamage(self.dmg)

    # Player gets attacked :(

    def takeDamage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.board.gameOver = True
            print("YOU DIED :(")

    # Healing :)
    def heal(self):
        if self.dt != 3:
            return False
        if self.healUsed:
            print("HEAL ALREADY USED :(")
            return False
        if self.hp == self.maxHp:
            print("HP ALREADY FULL")
            return False

        self.hp +=30

        if self.hp> self.maxHp:
            self.hp =self.maxHp

        self.healUsed = True
        print("HEALED +30 HP")
        return True

    # Freezing enemies :))))

    def freeze(self):
        if self.board.freezeTurns > 0:
            print("ENEMIES ALREADY FROZEN")
            return
        if self.freezes <= 0:
            print("NO FREEZES LEFT :(")
            return

        self.freezes -= 1
        self.board.freezeTurns = 2

        print("ENEMIES FROZEN!!!!")

# Wall object - basically just sits there :(
class Wall(Object):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "#"

# Basic enemy - very simple
class Enemy(Object):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "E"
        # Level boost = stronger but more rewardss
        LB= board.level-1
        self.hp = 3 + LB//3
        self.dmg = 15 + (LB//3)*2
        self.alive = True
        self.reward = 50 + LB*5

    # Defeat enemy
    def takeDamage(self, dmg):
        self.hp -= dmg

        if self.hp <= 0:
            self.alive = False
            self.board.removeObject(self)
            self.board.player.score += self.reward

    # Close... Oh nooo
    def attack(self):
        player = self.board.player
        dis = abs(player.x-self.x) + abs(player.y-self.y)
        if dis == 1:
            player.takeDamage(self.dmg)

    # Enemy turn - random movement 
    def turn(self):
        if not self.alive:
            return
        move = random.choice([(1,0), (-1,0), (0,1), (0,-1), (0,0)])
        self.move(move[0], move[1])
        self.attack()

# Enemy that follows the player - soooo annoying
class Chaser(Enemy):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "C"

        # Level boost = stronger but more rewardss
        LB = board.level-1
        
        self.dmg = 10 + (LB//3)*2
        self.reward = 75 + LB*7

    def turn(self):
        if not self.alive:
            return
        player = self.board.player
        dx = 0
        dy = 0
        if abs(player.x-self.x) > abs(player.y-self.y):
            if player.x > self.x:
                dx = 1
            elif player.x < self.x:
                dx = -1
        else:
            if player.y > self.y:
                dy = 1
            elif player.y < self.y:
                dy = -1

        oldX = self.x
        oldY = self.y

        self.move(dx, dy)

        # Tries different direction if there is a wall
        if self.x == oldX and self.y == oldY:

            if dx != 0:
                if player.y > self.y:
                    self.move(0,1)
                elif player.y < self.y:
                    self.move(0,-1)
            else:
                if player.x > self.x:
                    self.move(1,0)
                elif player.x < self.x:
                    self.move(-1,0)

        self.attack()

# Big slow enemy - absolute unit
class Brute(Enemy):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "B"

        # Level boost = stronger but more rewardss
        LB= board.level-1

        self.hp = 4 + LB//2
        self.dmg = 25 + (LB//3)*2
        self.turnCount = 0
        self.reward = 100 + LB*10

    def turn(self):
        if not self.alive:
            return
        self.turnCount += 1
        if self.turnCount % 2 == 0:
            super().turn()

# Stuff the dragon can collect :)
class Consumable(Object):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)

# Moneeyyyy
class Treasure(Consumable):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "T"

# Key to escape :)
class Key(Consumable):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "K"

# Board storage system
class Board():
    def __init__(self, w, h, safeZone, level):

        # Validation and values
        self.level =level
        self.width =w
        self.height= h
        self.levelComplete = False
        self.gameOver = False       
        self.player = None
        self.freezeTurns = 0


        # Safe zone system
        self.safeZone = safeZone
        self.board =[]

        for x in range(w):
            self.board.append([])
            for y in range(h):
                self.board[x].append("")

    # Locates the enemy
    def EP(self, x, y):
        return self.On(x,y) and isinstance(self.board[x][y], Enemy)
    
    # Specific place of object
    def addObject(self,obj):
        self.board[obj.x][obj.y] = obj
    def removeObject(self, obj):
        if self.board[obj.x][obj.y]== obj:
            self.board[obj.x][obj.y] =""
    def On(self, x, y):
        return self.width> x>= 0 and self.height>y >= 0

    # Checks if square is occupied, in the case that there are no consumables
    def occupied(self, x, y):
        return self.board[x][y] !="" and not isinstance(self.board[x][y], Consumable)

    # Random position of walls
    def rP(self):
        while True:
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if self.board[x][y] != "":
                continue

            # Makes sure dragon doesn't get trapped
            if (x,y) == (1,0) or (x,y) == (0,1):
                continue

            # Nothing spawns on safe zone
            if (x,y) ==self.safeZone:
                continue

            return x, y

    # Checks if one place can reach another
    def CR(self, start, target):
        queue= [start]
        visited= [start]
        while len(queue) > 0:
            x, y =queue.pop(0)
            if (x,y) == target:
                return True
            for dx, dy in [(1,0),(-1,0), (0,1),(0,-1)]:
                nx = x+dx
                ny = y+dy

                if not self.On(nx,ny):
                    continue
                if (nx,ny) in visited:
                    continue
                if isinstance(self.board[nx][ny],Wall):
                    continue
                visited.append((nx,ny))
                queue.append((nx,ny))
        return False

# Makes a fresh game
def makeGame(DT, level=1, score=0, hp=None):

    nC = min(2 + (level-1)//2, 5)
    cC = min(1 + (level-1)//3, 3)
    bC = min(1 + (level-1)//4, 2)

    # Keep making maps until one is possible
    while True:
        board = Board(COLS, ROWS, (9,7), level)
        player = Player(0, 0, board, DT)
        # Creating the wallss
        for i in range(10):
            x, y = board.rP()
            Wall(x, y, board)
        # Choose key position
        keyX, keyY = board.rP()
        # Check  dragon + KEY + ZONNEEEE
        if board.CR((0,0), (keyX,keyY)) and board.CR((keyX,keyY), board.safeZone):
            break


    player.score = score

    if hp != None:
        player.hp = hp

    # Creating key

    Key(keyX, keyY, board)
    # Creating treasures
    for i in range(5):
        x, y = board.rP()
        Treasure(x, y, board)




    # Creating normal enemies
    enemies = []
    for i in range(nC):
        x,y = board.rP()
        enemy = Enemy(x, y, board)
        enemies.append(enemy)

    # Creating chasers
    for i in range(cC):
        x, y = board.rP()
        chaser = Chaser(x, y, board)
        enemies.append(chaser)

    # Creating brutes
    for i in range(bC):
        x, y = board.rP()
        brute =Brute(x, y, board)
        enemies.append(brute)

    return board, player, enemies

DT = None
board = None
player = None
enemies = []

# Quick design pathway
def draw(text, fontUsed, colour, x, y):
    img = fontUsed.render(text, True, colour)
    screen.blit(img, (x,y))

# Grid formation
def drawGrid(board):
    for x in range(COLS):
        for y in range(ROWS):
            drawX = BOARD_X+x*CELL
            drawY = BOARD_Y+y*CELL

            
            # The goat safe zone area
            if (x,y) == board.safeZone:
                img = font.render("S",True,WHITE)
                pygame.draw.rect(screen,GREEN,(drawX,drawY,CELL,CELL))
                screen.blit(img,img.get_rect(center=(drawX+CELL//2,drawY+CELL//2)))

            obj = board.board[x][y]
            colour = GREY
            if obj != "":
                match obj.symbol:
                    case "D": colour = BLUE
                    case "K": colour = YELLOW
                    case "E": colour = RED
                    case "C": colour = ORANGE
                    case "T": colour = PURPLE
                    case "B": colour = MAROON
                pygame.draw.rect(screen,colour,(drawX,drawY,CELL,CELL))
                img = font.render(obj.symbol, True, WHITE)
                screen.blit(img, img.get_rect(center=(drawX+CELL//2, drawY+CELL//2)))
            pygame.draw.rect(screen, GRID,(drawX,drawY,CELL,CELL), 1)

# Visual representation - saves progress
def drawStats(board, player):
    x = 650

    draw("TUFF DRAGON CITY", big, WHITE, x, 70)

    draw("Dragon: "+player.name, small, WHITE, x, 110)
    draw("Score: "+str(player.score), small, WHITE, x, 140)
    draw("Level: "+str(board.level), small, WHITE, x, 175)
    draw("Key: "+("YES" if player.key else "NO"), small, WHITE, x, 210)
    draw("Damage: "+str(player.dmg), small, WHITE, x, 280)
    draw("HP: "+str(player.hp), small, WHITE, x, 245)

    draw("WASD = move", small, WHITE, x, 340)
    draw("Arrows = attack", small, WHITE, x, 375)
    draw("Find K then reach S", small, WHITE, x, 420)
    draw("T = bonus points", small, WHITE, x, 455)

    # Freezing process only
    draw("Freezes: "+str(player.freezes), small, WHITE, x, 490)
    draw("F = freeze enemies", small, WHITE, x, 520)
    if board.freezeTurns > 0:
        draw("FROZEN: "+str(board.freezeTurns), small, WHITE, x, 310)
    # Healing process only
    if player.dt == 3:
        draw("Heal: "+("USED" if player.healUsed else "READY"), small, WHITE, x, 550)
        draw("H = heal", small, WHITE, x, 580)

# Choose tuff dragons
def drawSelect():
    draw("CHOOSE YOUR DRAGON", big, WHITE, 320, 100)
    draw("1 - Fire Dragon", font, WHITE, 350, 210)
    draw("100 HP  |  2 Damage", small, WHITE, 370, 245)
    draw("2 - Tank Dragon", font, WHITE, 350, 310)
    draw("150 HP  |  1 Damage", small, WHITE, 370, 345)
    draw("3 - Heal Dragon", font, WHITE, 350, 410)
    draw("100 HP  |  1 Damage", small, WHITE, 370, 445)

# Game over screen
def drawEnd(player):
    cover = pygame.Surface((W,H))
    cover.set_alpha(215)
    cover.fill(BG)
    screen.blit(cover,(0,0))

    draw("GAME OVER", big, WHITE, 385, 230)
    draw("Score: "+str(player.score), font, WHITE, 415, 295)
    draw("R = restart", font, WHITE, 400, 350)
clock = pygame.time.Clock()
running = True

# Main and outputs stuff :)
while running:

    # Did player take turn?
    acted = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard connection
        if event.type == pygame.KEYDOWN:

            # Dragon selection using keys
            if DT == None:
                if event.key == pygame.K_1:
                    DT =1
                elif event.key == pygame.K_2:
                    DT= 2
                elif event.key == pygame.K_3:
                    DT = 3
                if DT != None:
                    board, player, enemies = makeGame(DT)
                continue

            # Restart key
            if board.gameOver:
                if event.key == pygame.K_r:
                    board, player, enemies = makeGame(DT)
                continue

            # Movement
            if event.key == pygame.K_w:
                player.move(0,-1)
                acted = True
            elif event.key == pygame.K_s:
                player.move(0,1)
                acted = True
            elif event.key == pygame.K_a:
                player.move(-1,0)
                acted = True
            elif event.key == pygame.K_d:
                player.move(1,0)
                acted = True

            # Attack + heal + freeze
            elif event.key == pygame.K_UP:
                player.attack(0,-1)
                acted = True
            elif event.key == pygame.K_DOWN:
                player.attack(0,1)
                acted = True
            elif event.key == pygame.K_LEFT:
                player.attack(-1,0)
                acted = True
            elif event.key == pygame.K_RIGHT:

                
                player.attack(1,0)
                acted = True
            elif event.key == pygame.K_h:
                if player.heal():
                    acted = True
            elif event.key == pygame.K_f:
                player.freeze()
    # Next level
    if DT != None and board.levelComplete:

        OS = player.score
        OH = player.hp
        nextLevel = board.level+ 1

        board, player, enemies =makeGame(DT, nextLevel, OS, OH)

        acted = False

    if DT != None and acted and not board.gameOver:



        if board.freezeTurns > 0:
            board.freezeTurns -= 1
        else:
            for enemy in enemies:
                if board.gameOver:
                    break
                enemy.turn()
    # Output everything and display and choose dragon
    screen.fill(BG)
    if DT == None:
        drawSelect()




    else:
        drawGrid(board)
        drawStats(board, player)
        if board.gameOver:
            drawEnd(player)

    pygame.display.update()
    clock.tick(60)


    
pygame.quit()






