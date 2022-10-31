# Base Template - Game options/Settings

TITLE = "Doodle Jump"
WIDTH = 480             # width of game window
HEIGHT = 600            # height of game window
FPS = 60                # frames per second
FONT_NAME = 'arial'
HS_FILE = "highscore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20         # power of jump

# GAME PROPERTIES
BOOST_POWER = 60
POW_SPAWN_PCT = 7
MOB_FREQ = 5000          # In milliseconds, i.e. 5 seconds
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2

# Starting platforms
PLATFORM_LIST = [(0, HEIGHT - 60),
                (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                (125, HEIGHT - 350),
                (350, 200),
                (175, 100)]

# Colors (R,G,B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = LIGHTBLUE

# MUSIC PROPERTIES
VOLUME = 0.25
VOLUME_JUMP = 0.3
VOLUME_BOOST = 0.35
FADEOUT = 500