import pygame

BASE_TILE_SIZE = 16
PIXEL_ZOOM = 3
TILE_SIZE = BASE_TILE_SIZE * PIXEL_ZOOM

MAP_WIDTH = 16
MAP_HEIGHT = 16

SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE
FPS = 60

bulletSpeed = 8
lootChance = 0.05
coinChance = 0.05
lootDuration = 7500
powerupDuration = 10000
playerSpeed = 3.0
orcSpeed = 2
ogreSpeed = 1
ghostSpeed = 3
spikeySpeed = 3
spikeyHealth = 2
cactusDanceDelay = 800
playerMotionDelay = 100
playerFootStepDelay = 20
deathDelay = 3000

MAP_BARIER1 = 0
MAP_BARIER2 = 1
MAP_ROCKY1 = 2
MAP_DESERT = 3
MAP_GRASSY = 4
MAP_CACTUS = 5
MAP_FENCE = 7
MAP_TRENCH1 = 8
MAP_TRENCH2 = 9
MAP_BRIDGE = 10

orc = 0
ghost = 1
ogre = 2
mummy = 3
devil = 4
mushroom = 5
spikey = 6
dracula = 7
desert = 0
woods = 2
graveyard = 1

POWERUP_LOG = -1
POWERUP_SKULL = -2
coin1 = 0
coin5 = 1
POWERUP_SPREAD = 2
POWERUP_RAPIDFIRE = 3
POWERUP_NUKE = 4
POWERUP_ZOMBIE = 5
POWERUP_SPEED = 6
POWERUP_SHOTGUN = 7
POWERUP_LIFE = 8
POWERUP_TELEPORT = 9
POWERUP_SHERIFF = 10
POWERUP_HEART = -3

ITEM_FIRESPEED1 = 0
ITEM_FIRESPEED2 = 1
ITEM_FIRESPEED3 = 2
ITEM_RUNSPEED1 = 3
ITEM_RUNSPEED2 = 4
ITEM_LIFE = 5
ITEM_AMMO1 = 6
ITEM_AMMO2 = 7
ITEM_AMMO3 = 8
ITEM_SPREADPISTOL = 9
ITEM_STAR = 10
ITEM_SKULL = 11
ITEM_LOG = 12

option_retry = 0
option_quit = 1

runSpeedLevel : int
fireSpeedLevel : int
ammoLevel : int
whichRound : int
spreadPistol  : bool

waveDuration = 80000
betweenWaveDuration = 5000

monsters = []
borderTiles = set()
playerPosition = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
playerBoundingBox = pygame.Rect(0, 0, 48, 48)
merchantBox = pygame.Rect(0, 0, 0, 0)
noPickUpBox = pygame.Rect(0, 0, 0, 0)

playerMovementDirections = []
playerShootingDirections = []
shootingDelay = 300
shotTimer : int
motionPause : int
bulletdamage : int
lives = 3
coins : int
score : int
bullets = []
enemyBullets = []

map_data = [[0 for _ in range(16)] for _ in range(16)]
next_map = [[0 for _ in range(16)] for _ in range(16)]
spawn_queue = [[] for _ in range(4)]

topLeftScreenCoordinate = pygame.Vector2(0, 0)

cactusDanceTimes : float
playerMotionAnimationTimer : float
behaviourAfterMotionPause = None #Function Pointer

monsterChances = [
    pygame.Vector2(0.014, 0.4),
    pygame.Vector2(0, 0),
    pygame.Vector2(0, 0),
    pygame.Vector2(0, 0),
    pygame.Vector2(0, 0),
    pygame.Vector2(0, 0),
    pygame.Vector2(0, 0)
]

shoppingCarpetNoPickup = pygame.Rect(0, 0, 0, 0)
activePowerups = {}

powerups = []
temporaryAnimatedSpriteList = []
heldItem = None #For powerup object

world = 0

gameOverOption : int
gameRestartTimer : int
fadeThenQuitTimer : int

waveTimer = 80000
betweenWaveTimer = 5000
whichWave : int

monsterConfusionTimer : int
zombieModeTimer : int
shoppingTimer : int
holdItemTimer : int
newMapPosition : int
playerInvincibleTimer : int
screenFlash : int
gopherTrainPosition : int
endCutsceneTimer : int
endCutscenePhase : int
startTimer : int
deathTimer : float

onStartMenu : bool
shopping : bool
gopherRunning : bool
store : bool
merchantLeaving : bool
merchantArriving : bool
merchantShopOpen : bool
waitingForPlayerToMoveDownAMap : bool
scrollingMap : bool
hasGopherAppeared : bool
shootOutLevel : bool
gopherTrain : bool
playerJumped : bool
endCutscene : bool
gameOver : bool

storeItems = {}

quitVar : bool
died : bool

gopherBox = pygame.Rect(0, 0, 0, 0)
gopherMotion = pygame.Vector2(0, 0)
binds = {}
buttonHeldState = set()
buttonHeldFrames = {}

targetMonster = None #For monster object