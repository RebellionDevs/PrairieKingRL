import pygame
from entities.powerup import CowboyPowerup

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

SPRITESHEET_PATH = "assets/Cursors.png"

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()  

powerup = CowboyPowerup(2, (320, 240), 10000)

running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    powerup.update(dt=dt)

    screen.fill((20, 20, 40))

    powerup.draw(screen, spritesheet, (0, 0))

    font = pygame.font.SysFont("arial", 20)
    text = font.render(f"duration: {powerup.duration:.0f} | offset: {powerup.yOffset:.2f}", True, (200, 200, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()

pygame.quit()