import pygame
from math import pi

class CowboyPowerup:
    def __init__(self, which, position, duration):
        self.which = which
        self.position = position
        self.duration = duration
        self.yOffset = 0.0

    def update(self, dt = 1.0):
        self.duration -= dt

        self.yOffset = (self.yOffset + 0.1) % (2 * pi)

    def should_draw(self):
        if self.duration <= 0: return False
        if self.duration > 2000: return True
        return (int(self.duration) // 200) % 2 == 0
    
    def draw(self, screen, spritesheet, top_left):
        if not self.should_draw(): return

        src_rect = pygame.Rect(272 + self.which * 16, 1808, 16, 16)

        draw_x = top_left[0] + self.position[0]
        draw_y = top_left[1] + self.position[1] + self.yOffset

        sprite = spritesheet.subsurface(src_rect)
        scaled = pygame.transform.scale(sprite, (48, 48))

        screen.blit(scaled, (draw_x - 24, draw_y - 24))