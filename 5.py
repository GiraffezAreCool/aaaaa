import pygame

pygame.init()


BG = (20,25,35)
WHITE = (240,240,240)
BLUE = (60,150,255)
RED = (220,70,70)
PURPLE = (175,95,230)
GREEN = (65,195,105)
GREY = (90,95,105)

class Board():
    def __init__(self, width, height, safeZone):
        self.width = width
        self.height = height
        self.board = []
        self.safeZone = safeZone
        for x in range(width):
            self.board.append([])
            for y in range(height):
                self.board[x].append("")


    def addObject(self, obj):
        self.board[obj.x][obj.y] = obj


    def removeObject(self, obj):
        self.board[obj.x][obj.y] = ""


    def printBoard(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[x][self.width-y-1] == "": print(".", end="")
                else: print(self.board[x][self.width-y-1].symbol, end="")
            print()


    def isOnBoard(self, x, y):
        return self.width > x >= 0 and self.height > y >= 0


    def isOccupied(self, x, y):
        return self.isOnBoard(x, y) and not (self.board[x][y] == "" or type(self.board[x][y]) == Consumable)

    def isEnemy(self, x, y):
        return self.isOnBoard(x, y) and type(self.board[x][y]) == Enemy

    def isPlayer(self, x, y):
        return self.isOnBoard(x, y) and type(self.board[x][y]) == Player

    def isConsumable(self, x, y):
        return self.isOnBoard(x, y) and type(self.board[x][y]) == Consumable

    def renderBoard(self):
        for x in range(self.width):
            for y in range(self.height):
                dx = 50+x*50
                dy = 50+(self.height-y-1)*50
                colour = ""
                if self.board[x][y] != "":
                    match self.board[x][y].symbol:
                        case "P": colour = BLUE
                        case "E": colour = RED
                        case "C": colour = GREEN
                        case "T": colour = PURPLE

                    pygame.draw.rect(screen, colour, (dx,dy,50,50))

                    img = font.render(self.board[x][y].symbol, True, WHITE)
                    screen.blit(img, img.get_rect(center=(dx+50//2, dy+50//2)))
                else:
                    pygame.draw.rect(screen, GREY, (dx,dy,50,50))



class Object():
    def __init__(self, x, y, board:Board):
        self.x = x
        self.y = y
        self.symbol = "O"
        self.board = board
        board.addObject(self)


    def move(self, dx, dy):
        nx, ny = self.x+dx, self.y+dy
        if (not self.board.isOnBoard(nx, ny)): return
        if (self.board.isOccupied(nx, ny)): return
        self.board.removeObject(self)
        self.x += dx
        self.y += dy
        self.board.addObject(self)






class Player(Object):
    def __init__(self, x, y, board, hp, dmg):
        super().__init__(x, y, board)
        self.hp = hp
        self.dmg = dmg
        self.symbol = "P"
        self.score = 0


    def attack(self, dx, dy):
        if (not self.board.isOnBoard(self.x+dx, self.y+dy)): return
        if (not self.board.isEnemy(self.x+dx, self.y+dy)): return
        self.board.board[self.x+dx][self.y+dy].takeDamage(self.dmg)

    def takeDamage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            #end screen or smth
            pass

    def move(self, dx, dy):
        nx, ny = self.x+dx, self.y+dy
        if (not self.board.isOnBoard(nx, ny)): return
        if (self.board.isOccupied(nx, ny)): return
        if (self.board.isConsumable(nx, ny)):
            self.hp += self.board.board[nx][ny].hp
            self.dmg += self.board.board[nx][ny].dmg
            self.score += self.board.board[nx][ny].score
            print("I consume now")
        self.board.removeObject(self)
        self.x += dx
        self.y += dy
        self.board.addObject(self)
        if (self.x == self.board.safeZone[0] and self.y == self.board.safeZone[1]):
            #win screen or smth
            print("yay")
            pass




class Enemy(Object):
    def __init__(self, x, y, board:Board, hp, dmg, attackPattern, patrolPath):
        super().__init__(x, y, board)
        self.hp = hp
        self.dmg = dmg
        self.symbol = "E"
        self.attackPattern = attackPattern
        self.patrolPath = patrolPath
        self.patrolCycle = 0
    




    def takeDamage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.board.removeObject(self)

    def attack(self):
        if (not self.isPlayerInRange()): return
        player.takeDamage(self.dmg)
        


    def isPlayerInRange(self):
        cx = self.attackPattern[0][0]
        cy = self.attackPattern[0][1]
        pattern = self.attackPattern[1]
        for y in range(len(pattern)):
            for x in range(len(pattern[y])):
                if pattern[x][y] == 1 and self.board.isPlayer(self.x + (x-cx), self.y + (y-cy)):
                    return True


        return False


    def patrol(self):
        self.move(patrolPath[self.patrolCycle][0], patrolPath[self.patrolCycle][1])
        self.patrolCycle+=1
        if self.patrolCycle >= len(patrolPath):
            self.patrolCycle = 0


class Consumable(Object):
    def __init__(self, x, y, board, hp=0, dmg=0, score=0, symbol="C"):
        super().__init__(x, y, board)
        self.symbol = symbol
        self.hp = hp
        self.dmg = dmg
        self.score = score




b = Board(width=5,height=5,safeZone=(4,4))
player = Player(x=0, y=0, board=b, hp=10, dmg=1)
attackPattern = ((1,1),[
[0, 1, 0],
[1, 0, 1],
[0, 1, 1],
])


patrolPath = [(1,0), (1,0), (0,1), (0,1), (-1,0), (-1, 0), (0,-1), (0,-1)]


enemy = Enemy(x=2, y=2, board=b, hp=3, dmg=1, attackPattern=attackPattern, patrolPath=patrolPath)
consumable = Consumable(x=1, y=1, board=b, hp=3, dmg=10, symbol="C")
consumable = Consumable(x=3, y=1, board=b, symbol="T", score=10)
b.addObject(player)
b.addObject(enemy)
b.addObject(consumable)


screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Dragon City")

font = pygame.font.Font(None, 32)

clock = pygame.time.Clock()

screen.fill(BG)
b.renderBoard()
img = font.render(f"Health: {player.hp}", True, WHITE)
screen.blit(img, (300,50))
img = font.render(f"Damage: {player.dmg}", True, WHITE)
screen.blit(img, (300,70))
img = font.render(f"Score: {player.score}", True, WHITE)
screen.blit(img, (300,90))
pygame.display.update()
doneAction = False
while True:
    #inp = input()
    #match inp.lower():
    #    case "w":
    #        player.move(0,1)
    #    case "a":
    #        player.move(-1,0)
    #    case "s":
    #        player.move(0,-1)
    #    case "d":
    #        player.move(1,0)
    #    case "aw":
    #        player.attack(0,1)
    #    case "aa":
    #        player.attack(-1,0)
    #    case "as":
    #        player.attack(0,-1)
    #    case "ad":
    #        player.attack(1,0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit()

        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_w:
                    player.move(0,1)
                case pygame.K_a:
                    player.move(-1,0)
                case pygame.K_s:
                    player.move(0,-1)
                case pygame.K_d:
                    player.move(1,0)
                case pygame.K_UP:
                    player.attack(0,1)
                case pygame.K_LEFT:
                    player.attack(-1,0)
                case pygame.K_DOWN:
                    player.attack(0,-1)
                case pygame.K_RIGHT:
                    player.attack(1,0)
            doneAction = True
    if doneAction:           
        print(player.x, player.y)
        b.printBoard()
        if (enemy.hp > 0):
            enemy.patrol()
            enemy.attack()
        screen.fill(BG)
        b.renderBoard()
        img = font.render(f"Health: {player.hp}", True, WHITE)
        screen.blit(img, (300,50))
        img = font.render(f"Damage: {player.dmg}", True, WHITE)
        screen.blit(img, (300,70))
        img = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(img, (300,90))

        pygame.display.update()
        clock.tick(60)
        doneAction = False




