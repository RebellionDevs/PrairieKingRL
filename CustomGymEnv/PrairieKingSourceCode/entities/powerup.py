import pygame
import math

class Powerup:
    def __init__(self, which, position, duration):
        self.which = which
        self.position = pygame.Vector2(position)
        self.duration = duration
        self.yOffset = 0.0

    def update(self, dt):
        self.duration -= dt
        self.yOffset = math.sin(pygame.time.get_ticks() * 0.005) * 5

    def draw(self, screen, tilesheet, topLeftScreen):
        if self.duration > 2000 or (self.duration // 200) % 2 == 0:
            sourceRect = pygame.Rect(272 + self.which * 16, 1808, 16, 16)

            drawPos = (
                topLeftScreen[0] + self.position.x,
                topLeftScreen[1] + self.position.y + self.yOffset
            )

            tempSurface = pygame.Surface((16, 16), pygame.SRCALPHA)
            tempSurface.blit(tilesheet, (0, 0), sourceRect)

            finalImage = pygame.transform.scale(tempSurface, (48, 48))
            screen.blit(finalImage, drawPos)
