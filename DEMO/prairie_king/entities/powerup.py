import pygame
from ..constants import TILESIZE

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, groups, power_type: str):
        super().__init__(groups)
        self.power_type = power_type
        self.lifetime = 720
        self.flash_start = 180

        self._load_sprite()
        self.rect = self.image.get_rect(center=pos)

    def _load_sprite(self):
        try:
            if self.power_type == "coffee":
                img = pygame.image.load('assets/JOPK_Coffee.png').convert_alpha()
            elif self.power_type == "machinegun":
                img = pygame.image.load('assets/JOPK_MachineGun.png').convert_alpha()
            elif self.power_type == "shotgun":
                img = pygame.image.load('assets/JOPK_Shotgun.png').convert_alpha()
            elif self.power_type == "wheel":
                img = pygame.image.load('assets/JOPK_Wheel.png').convert_alpha()
            elif self.power_type == "star":
                img = pygame.image.load('assets/JOPK_Star.png').convert_alpha()
            else:
                img = pygame.image.load('assets/JOPK_Coffee.png').convert_alpha()

            self.image = pygame.transform.scale_by(img, 1)
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 255, 100), (TILESIZE//2, TILESIZE//2), TILESIZE//2)

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

    def is_flashing(self):
        return self.lifetime <= self.flash_start