import pygame, sys, os
import pygame.locals
from pygame.locals import *
from pygase import Client


### SETUP ###
FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
DARKRED       = (155,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKBLUE  = (  0, 0,   155)
BLUE      = (  0, 0,   255)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

catImg = pygame.image.load('cat.png')
mouseImg = pygame.image.load('mouse.png')

# class con cua class pygase de thiet lap cac event handler va cac bien game dac biet.
class ChaseClient(Client):
    def __init__(self):
        super().__init__()
        self.player_id = None
        # backend se gui su kien "PLAER_CREATED" de tra loi su kien "JOIN".
        self.register_event_handler("PLAYER_CREATED", self.on_player_created)

    # "PLAYER_CREATED" event handler.
    def on_player_created(self, player_id):
        # Id nay duoc backend gan cho player
        self.player_id = player_id


# Khoi tao client.
client = ChaseClient()

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    # Ket noi client voi server, nhap ip, port va ten nhan vat.
    client.connect_in_thread(hostname=input("Server ip (type 'localhost' if you are server): "), port=int(input("Port (same with server port): ")))
    client.dispatch_event("JOIN", input("Player name: "))
    # Doi cho den khi su kien "PLAYER_CREATED" da duoc xu li.
    while client.player_id is None:
        pass
    # Thiet lap ban dau pygame.
    keys_pressed = set()  # tat ca phim dang duoc nhan.
    FPSCLOCK = pygame.time.Clock()
    # Khoi tao man hinh pygame.
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 12)
    pygame.display.set_caption('The Cat!')

    # Chay man hinh intro game.
    showStartScreen()

    # Vong lap game.
    game_loop_is_running = True
    while game_loop_is_running:
        dt = FPSCLOCK.tick(15)
        # Xoa man hinh.
        DISPLAYSURF.fill((0, 0, 0))
        drawGrid()
        # Xu li su kien dau vao pygame.
        for event in pygame.event.get():
            if event.type == QUIT:
                game_loop_is_running = False
            if event.type == KEYDOWN:
                keys_pressed.add(event.key)
            if event.type == KEYUP:
                keys_pressed.remove(event.key)
        # Xu li di chuyen player.
        dx, dy = 0, 0
        if pygame.locals.K_DOWN in keys_pressed:
            dy += CELLSIZE
        elif pygame.locals.K_UP in keys_pressed:
            dy -= CELLSIZE
        elif pygame.locals.K_RIGHT in keys_pressed:
            dx += CELLSIZE
        elif pygame.locals.K_LEFT in keys_pressed:
            dx -= CELLSIZE
        # Truy cap trang thai game.
        with client.access_game_state() as game_state:
            # Bao server ve su kien di chuyen player.
            old_position = game_state.players[client.player_id]["position"]
            client.dispatch_event(
                event_type="MOVE",
                player_id=client.player_id,
                new_position=((old_position[0] + dx) % WINDOWWIDTH, (old_position[1] + dy) % WINDOWHEIGHT),
            )
            for player_id, player in game_state.players.items():
                if player_id == client.player_id:
                    # Xanh la: Ban.
                    color = GREEN
                    dark_color = DARKGREEN
                    isTheCat = 1 if (client.player_id==game_state.TheCat_id) else 0
                elif player_id == game_state.TheCat_id:
                    # Do: nhan vat TheCat.
                    color = RED
                    dark_color = DARKRED
                    isTheCat = 1
                else:
                    # Xanh lam: Nhung nguoi choi khac.
                    color = BLUE
                    dark_color = DARKBLUE
                    isTheCat = 0
                x, y = [int(coordinate) for coordinate in player["position"]]
                drawPlayerGamer(x, y, dark_color, color, isTheCat) #!
        
        drawScore('Green: Yourself', None, WINDOWWIDTH - 350, 10)
        drawScore('Red: The Cat', None, WINDOWWIDTH - 350, 40)
        drawScore('Blue: Others', None, WINDOWWIDTH - 350, 70)
        drawScore('No red on screen, you are The Cat', None, WINDOWWIDTH - 350, 100)

        pygame.display.flip()
    # Disconnect neu thoat game va shutdown server.
    client.disconnect(shutdown_server=True)
    
    # Clean up.
    terminate()


def drawPlayerGamer(x, y, edge_color, color, isTheCat):
    playerSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, edge_color, playerSegmentRect)
    playerInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
    pygame.draw.rect(DISPLAYSURF, color, playerInnerSegmentRect)
    if isTheCat==0:
        DISPLAYSURF.blit(mouseImg, (x,y,CELLSIZE-8,CELLSIZE-8))
    else:
        DISPLAYSURF.blit(catImg, (x,y,CELLSIZE-8,CELLSIZE-8))


def drawGrid():
    '''
    Ham ve luoi
    '''
    # ve duong doc
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    # ve duong ngang
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

def drawPressKeyMsg():
    '''
    Ham ve dong chu 'Press a key to play' tai man hinh bat dau
    '''
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def terminate():
    '''
    pygame.quit() & sys.exit(0)
    '''
    pygame.quit()
    os._exit(0)

def drawScore(player,score, x, y):
    '''
    Ham hien thi diem nguoi choi
    '''
    if score == None:
        scoreSurf = BASICFONT.render(player, True, WHITE)
    else:
        scoreSurf = BASICFONT.render('Score ' + player + ': %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (x, y)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def checkForKeyPress():
    '''
    Ham check su kien nhan phim
    + thoat khi co phim Esc duoc nhan
    + thoat khi co su kien QUIT trong event queue
    '''

    # neu co su kien QUIT trong hang doi 'event'.
    # thi thoat.
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP) # lay ds 'event' KEYUP
    if len(keyUpEvents) == 0:
        return None
    # neu su kien dau ds la Esc key thi thoat
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def showStartScreen():
    '''
    Ham hien thi hieu ung dau chuong trinh
    + hai dong chu khac mau xoay voi 2 goc do khac nhau tao hieu ung
    '''
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('The Cat!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('The Cat!', True, GREEN)

    # Goc cua dong 'titleSurf1'.
    degrees1 = 0
    # Goc cua dong 'titleSurf2'.
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        # chen hieu ung xoay cho dong 'titleSurf1'
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        # chen hieu ung xoay cho dong 'titleSurf1'.
        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue.
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame.
        degrees2 += 7 # rotate by 7 degrees each frame.

### MAIN PROCESS ###

if __name__ == "__main__":
    main()
    