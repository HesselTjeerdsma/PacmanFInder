import os.path
from logging import DEBUG

# ----- Constants -----
# Root directory of the project (absolute path)
PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))

# RGB colors for pygame
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

COLOR_PINK = (255, 105, 180)

# ----- Settings -----
# Debug properties
LOGGING_LEVEL = DEBUG
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEBUG_PLAYER = False

# Caption
WINDOW_CAPTION = 'Pacman'

# Map properties
MAP_DIR = 'maps'
MAP = 'flux_floor9.svg'

# Proxy IP
ALLOWED_PROXIES = ['192.168.100.12']  # TODO: set it as input parameter from __main__

# Registration API
REGISTRATION_IP = '0.0.0.0'
REGISTRATION_PORT = 50000
# Pacman:Ghost ratio
PG_RATIO = 1

# Event API
EVENT_PORT = 50001

# Scoring
SCORE_FOOD = 10
SCORE_CHERRY = 50
SCORE_ENERGIZER = 10
SCORE_HIT_PACMAN = 200
SCORE_HIT_GHOST = 200

# Timers
TIMER_QUARANTINE = 10
TIMER_ENERGIZER = 0
CHERRY_AVG_LIFETIME = 10
CHERRY_AVG_GRACE = 25

# Pixel:meter ratio
PM_RATIO = 0.05  # 1600px:80m
JUMP_LIMIT = 2*1000  # Millimeters; 1 meter limit

