import pygame
import random


pygame.init()




class Object():
    def __init__(self, x, y, board):
        self.x = x
        self.y = y
        self.symbol = "O"
        self.board = board
        self.alive = True
        board.addObject(self)


    def move(self, dx, dy):
        if not self.alive: return
        nx, ny = self.x+dx, self.y+dy
        if (not self.board.isOnBoard(nx, ny)): return
        if ((nx, ny) == self.board.safeZone): return
        if (self.board.board[nx][ny] != ""): return


        self.board.removeObject(self)
        self.x += dx
        self.y += dy
        self.board.addObject(self)




class Player(Object):
    def __init__(self, x, y, board, dragonType):
        super().__init__(x, y, board)
        self.symbol = "D"
        self.dragonType = dragonType
        self.score = 0
        self.key = False
        self.freezes = 2
        self.healUsed = False


        if dragonType == 1:
            self.name = "Fire"
            self.hp = 200
            self.dmg = 2


        elif dragonType == 2:
            self.name = "Tank"
            self.hp = 300
            self.dmg = 1


        else:
            self.name = "Heal"
            self.hp = 200
            self.dmg = 1


        self.maxHp = self.hp
        board.player = self


    def attack(self, dx, dy):
        nx, ny = self.x+dx, self.y+dy
        if (not self.board.isOnBoard(nx, ny)): return


        if (not self.board.isEnemy(nx, ny)):
            self.board.message = "No enemy there"
            return


        enemy = self.board.board[nx][ny]
        enemy.takeDamage(self.dmg)


        if enemy.alive:
            self.board.message = "Enemy took " + str(self.dmg) + " damage"


    def takeDamage(self, dmg):
        self.hp -= dmg
        self.board.message = "Enemy attacked! -" + str(dmg) + " HP"


        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.board.removeObject(self)
            self.board.gameOver = True
            self.board.win = False


    def heal(self):
        if self.dragonType != 3:
            self.board.message = "Only Heal Dragon can do that"
            return False


        if self.healUsed:
            self.board.message = "Heal already used"
            return False


        self.hp += 150
        if self.hp > self.maxHp: self.hp = self.maxHp


        self.healUsed = True
        self.board.message = "+150 HP"
        return True


    def freeze(self):
        if self.board.freezeTurns > 0:
            self.board.message = "Enemies are already frozen"
            return


        if self.freezes <= 0:
            self.board.message = "No freezes left"
            return


        self.freezes -= 1
        self.board.freezeTurns = 2
        self.board.message = "All enemies frozen!"


    def move(self, dx, dy):
        nx, ny = self.x+dx, self.y+dy


        if (not self.board.isOnBoard(nx, ny)):
            self.board.message = "You cannot leave the map"
            return


        if (nx, ny) == self.board.safeZone and not self.key:
            self.board.message = "Exit locked - find the key"
            return


        if (self.board.isOccupied(nx, ny)):
            self.board.message = "Something is blocking you"
            return


        if (self.board.isConsumable(nx, ny)):
            item = self.board.board[nx][ny]


            if type(item) == Treasure:
                self.score += 100
                self.board.treasureCount += 1
                self.board.removeObject(item)
                self.board.message = "Treasure " + str(self.board.treasureCount) + "/5"


            elif type(item) == PowerUp:
                self.hp += 20
                if self.hp > self.maxHp: self.hp = self.maxHp
                self.board.removeObject(item)
                self.board.message = "+20 HP"


            elif type(item) == Key:
                self.key = True
                self.board.removeObject(item)
                self.board.message = "Key collected! Go to S"


        self.board.removeObject(self)
        self.x += dx
        self.y += dy
        self.board.addObject(self)


        if self.board.treasureCount == 5 and not self.board.keySpawned:
            self.board.spawnKey()


        if (self.x == self.board.safeZone[0] and self.y == self.board.safeZone[1]):
            if self.key:
                self.board.gameOver = True
                self.board.win = True
                self.board.message = "You escaped!"




class Enemy(Object):
    def __init__(self, x, y, board, hp=3, dmg=15):
        super().__init__(x, y, board)
        self.hp = hp
        self.dmg = dmg
        self.symbol = "E"


    def takeDamage(self, dmg):
        self.hp -= dmg


        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.board.removeObject(self)
            self.board.player.score += 50
            self.board.message = "Enemy defeated! +50 score"


    def attack(self):
        if not self.alive: return
        if self.board.gameOver: return


        player = self.board.player
        distance = abs(player.x-self.x) + abs(player.y-self.y)


        if distance == 1:
            player.takeDamage(self.dmg)


    def turn(self):
        if not self.alive: return


        move = random.choice([(1,0), (-1,0), (0,1), (0,-1), (0,0)])
        self.move(move[0], move[1])
        self.attack()




class Chaser(Enemy):
    def __init__(self, x, y, board):
        super().__init__(x, y, board, hp=3, dmg=20)
        self.symbol = "C"


    def turn(self):
        if not self.alive: return


        player = self.board.player
        dx, dy = 0, 0


        if abs(player.x-self.x) > abs(player.y-self.y):
            if player.x > self.x: dx = 1
            elif player.x < self.x: dx = -1
        else:
            if player.y > self.y: dy = 1
            elif player.y < self.y: dy = -1


        oldX, oldY = self.x, self.y
        self.move(dx, dy)


        if self.x == oldX and self.y == oldY:
            if dx != 0:
                if player.y > self.y: self.move(0,1)
                elif player.y < self.y: self.move(0,-1)
            else:
                if player.x > self.x: self.move(1,0)
                elif player.x < self.x: self.move(-1,0)


        self.attack()




class Brute(Enemy):
    def __init__(self, x, y, board):
        super().__init__(x, y, board, hp=6, dmg=25)
        self.symbol = "B"
        self.turnCount = 0


    def turn(self):
        if not self.alive: return
        self.turnCount += 1


        if self.turnCount % 2 == 0:
            player = self.board.player
            dx, dy = 0, 0


            if abs(player.x-self.x) > abs(player.y-self.y):
                if player.x > self.x: dx = 1
                elif player.x < self.x: dx = -1
            else:
                if player.y > self.y: dy = 1
                elif player.y < self.y: dy = -1


            self.move(dx, dy)


        self.attack()




class Consumable(Object):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "C"




class Treasure(Consumable):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "T"




class PowerUp(Consumable):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "P"




class Key(Consumable):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "K"




class Wall(Object):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)
        self.symbol = "#"




class Board():
    def __init__(self, width, height, safeZone):
        self.width = width
        self.height = height
        self.safeZone = safeZone
        self.player = None
        self.gameOver = False
        self.win = False
        self.treasureCount = 0
        self.keySpawned = False
        self.freezeTurns = 0
        self.message = "Collect all 5 treasures"
        self.board = []


        for x in range(width):
            self.board.append([])
            for y in range(height):
                self.board[x].append("")


    def addObject(self, obj):
        self.board[obj.x][obj.y] = obj


    def removeObject(self, obj):
        if self.board[obj.x][obj.y] == obj:
            self.board[obj.x][obj.y] = ""


    def isOnBoard(self, x, y):
        return self.width > x >= 0 and self.height > y >= 0


    def isOccupied(self, x, y):
        return self.isOnBoard(x, y) and not (self.board[x][y] == "" or isinstance(self.board[x][y], Consumable))


    def isEnemy(self, x, y):
        return self.isOnBoard(x, y) and isinstance(self.board[x][y], Enemy)


    def isConsumable(self, x, y):
        return self.isOnBoard(x, y) and isinstance(self.board[x][y], Consumable)


    def randomPosition(self, minDistance=0):
        while True:
            x = random.randrange(self.width)
            y = random.randrange(self.height)


            if self.board[x][y] != "": continue
            if (x,y) == self.safeZone: continue
            if (x,y) == (0,0): continue


            if self.player != None:
                distance = abs(x-self.player.x) + abs(y-self.player.y)
                if distance < minDistance: continue


            return x, y


    def spawnKey(self):
        if self.keySpawned: return


        x, y = self.randomPosition()
        Key(x, y, self)


        self.keySpawned = True
        self.message = "All treasures found! Find K"




WIDTH, HEIGHT = 960, 610
CELL = 58
BOARD_X, BOARD_Y = 35, 65


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon City")


font = pygame.font.Font(None, 32)
smallFont = pygame.font.Font(None, 24)
bigFont = pygame.font.Font(None, 52)


BG = (20,25,35)
EMPTY = (38,48,63)
GRID = (75,85,100)
WHITE = (240,240,240)
BLUE = (60,150,255)
RED = (220,70,70)
ORANGE = (235,130,50)
PURPLE = (175,95,230)
YELLOW = (245,205,70)
GREEN = (65,195,105)
GREY = (90,95,105)
CYAN = (60,200,210)




def makeGame(dragonType):
    board = Board(width=10, height=8, safeZone=(9,7))
    player = Player(x=0, y=0, board=board, dragonType=dragonType)


    safeSquares = [(0,0), (1,0), (0,1), (9,7), (8,7), (9,6)]


    wallCount = 0
    while wallCount < 10:
        x, y = board.randomPosition()


        if (x,y) in safeSquares: continue


        Wall(x, y, board)
        wallCount += 1


    for i in range(5):
        x, y = board.randomPosition()
        Treasure(x, y, board)


    for i in range(2):
        x, y = board.randomPosition()
        PowerUp(x, y, board)


    enemies = []


    x, y = board.randomPosition(4)
    enemy1 = Enemy(x, y, board)
    enemies.append(enemy1)


    x, y = board.randomPosition(4)
    enemy2 = Enemy(x, y, board)
    enemies.append(enemy2)


    x, y = board.randomPosition(4)
    chaser1 = Chaser(x, y, board)
    enemies.append(chaser1)


    x, y = board.randomPosition(4)
    chaser2 = Chaser(x, y, board)
    enemies.append(chaser2)


    x, y = board.randomPosition(5)
    brute = Brute(x, y, board)
    enemies.append(brute)


    return board, player, enemies




def drawText(text, fontUsed, colour, x, y):
    img = fontUsed.render(text, True, colour)
    screen.blit(img, (x,y))




def drawBoard(board):
    for x in range(board.width):
        for y in range(board.height):
            drawX = BOARD_X+x*CELL
            drawY = BOARD_Y+(board.height-y-1)*CELL
            colour = EMPTY
            symbol = ""


            if (x,y) == board.safeZone:
                colour = PURPLE
                symbol = "S"


            obj = board.board[x][y]


            if obj != "":
                symbol = obj.symbol


                if isinstance(obj, Player): colour = BLUE
                elif isinstance(obj, Chaser): colour = CYAN
                elif isinstance(obj, Brute): colour = ORANGE
                elif isinstance(obj, Enemy): colour = RED
                elif isinstance(obj, Treasure): colour = YELLOW
                elif isinstance(obj, PowerUp): colour = GREEN
                elif isinstance(obj, Key): colour = WHITE
                elif isinstance(obj, Wall): colour = GREY


            pygame.draw.rect(screen, colour, (drawX,drawY,CELL,CELL))
            pygame.draw.rect(screen, GRID, (drawX,drawY,CELL,CELL), 2)


            if symbol != "":
                textColour = BG if symbol == "T" or symbol == "K" else WHITE
                img = font.render(symbol, True, textColour)
                screen.blit(img, img.get_rect(center=(drawX+CELL//2, drawY+CELL//2)))




def drawStats(board, player):
    x = 650


    drawText("DRAGON CITY", font, WHITE, x, 60)
    drawText("Dragon: "+player.name, smallFont, WHITE, x, 110)
    drawText("HP: "+str(player.hp)+"/"+str(player.maxHp), smallFont, WHITE, x, 140)
    drawText("Damage: "+str(player.dmg), smallFont, WHITE, x, 170)
    drawText("Score: "+str(player.score), smallFont, WHITE, x, 200)
    drawText("Treasure: "+str(board.treasureCount)+"/5", smallFont, WHITE, x, 230)
    drawText("Key: "+("YES" if player.key else "NO"), smallFont, WHITE, x, 260)
    drawText("Freezes: "+str(player.freezes), smallFont, WHITE, x, 290)


    pygame.draw.rect(screen, GREY, (x,325,240,22))
    hpWidth = int(240*(player.hp/player.maxHp))
    pygame.draw.rect(screen, GREEN, (x,325,hpWidth,22))


    drawText("WASD = move", smallFont, WHITE, x, 370)
    drawText("Arrow keys = attack", smallFont, WHITE, x, 400)
    drawText("F = freeze enemies", smallFont, WHITE, x, 430)


    if player.dragonType == 3:
        drawText("H = heal once", smallFont, WHITE, x, 460)


    if board.freezeTurns > 0:
        drawText("FROZEN: "+str(board.freezeTurns)+" turns", smallFont, CYAN, x, 500)


    drawText(board.message, smallFont, WHITE, 35, 560)




def drawSelect():
    drawText("CHOOSE YOUR DRAGON", bigFont, WHITE, 250, 100)
    drawText("1   Fire Dragon - 2 damage", font, RED, 290, 210)
    drawText("2   Tank Dragon - 300 HP", font, GREEN, 290, 270)
    drawText("3   Heal Dragon - heal once", font, CYAN, 290, 330)




def drawEnd(board, player):
    cover = pygame.Surface((WIDTH, HEIGHT))
    cover.set_alpha(215)
    cover.fill(BG)
    screen.blit(cover, (0,0))


    if board.win:
        title = "YOU WIN!"
    else:
        title = "GAME OVER"


    img = bigFont.render(title, True, WHITE)
    screen.blit(img, img.get_rect(center=(WIDTH//2, HEIGHT//2-60)))


    score = font.render("Score: "+str(player.score), True, WHITE)
    screen.blit(score, score.get_rect(center=(WIDTH//2, HEIGHT//2)))


    restart = font.render("R = restart     M = choose dragon", True, WHITE)
    screen.blit(restart, restart.get_rect(center=(WIDTH//2, HEIGHT//2+55)))




dragonType = None
board = None
player = None
enemies = []


clock = pygame.time.Clock()
running = True




while running:
    acted = False


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False


            if dragonType == None:
                if event.key == pygame.K_1:
                    dragonType = 1
                elif event.key == pygame.K_2:
                    dragonType = 2
                elif event.key == pygame.K_3:
                    dragonType = 3


                if dragonType != None:
                    board, player, enemies = makeGame(dragonType)


                continue


            if board.gameOver:
                if event.key == pygame.K_r:
                    board, player, enemies = makeGame(dragonType)


                elif event.key == pygame.K_m:
                    dragonType = None


                continue


            if event.key == pygame.K_w:
                player.move(0,1)
                acted = True


            elif event.key == pygame.K_a:
                player.move(-1,0)
                acted = True


            elif event.key == pygame.K_s:
                player.move(0,-1)
                acted = True


            elif event.key == pygame.K_d:
                player.move(1,0)
                acted = True


            elif event.key == pygame.K_UP:
                player.attack(0,1)
                acted = True


            elif event.key == pygame.K_LEFT:
                player.attack(-1,0)
                acted = True


            elif event.key == pygame.K_DOWN:
                player.attack(0,-1)
                acted = True


            elif event.key == pygame.K_RIGHT:
                player.attack(1,0)
                acted = True


            elif event.key == pygame.K_f:
                player.freeze()


            elif event.key == pygame.K_h:
                if player.heal():
                    acted = True


    if dragonType != None and acted and not board.gameOver:

        if board.freezeTurns > 0:
            board.freezeTurns -= 1


        else:
            for enemy in enemies:
                if not board.gameOver:
                    enemy.turn()

    screen.fill(BG)

    if dragonType == None:
        drawSelect()

    else:
        drawBoard(board)
        drawStats(board, player)
        if board.gameOver:
            drawEnd(board, player)

    pygame.display.update()
    clock.tick(60)

pygame.quit()





