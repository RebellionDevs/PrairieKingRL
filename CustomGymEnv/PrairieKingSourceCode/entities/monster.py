import random
import math
import pygame

TILE_SIZE = 16
MONSTER_ANImATION_DELAY = 500

class CowboyMonster:
    def __init__(self, which, health, speed, position):
        self.type = which
        self.health = health
        self.speed = speed
        self.position = pygame.Rect(position[0], position[1], TILE_SIZE, TILE_SIZE) if position else None

        self.movement_animation_timer = 0.0
        self.movement_direction = 0
        self.moved_last_turn = False
        self.opposite_motion_guy = random.choice([True, False])
        self.invisible = False
        self.special = False
        self.unintrested = False
        self.flyer = False
        self.tint = (255, 255, 255)
        self.flash_color = (255, 0, 0)
        self.flash_color_timer = 0.0
        self.ticks_since_last_movement = 0
        self.acceleration = [0.0, 0.0]
        self.target_position = (0, 0)

        if health is None or speed is None:
            self.init_by_type(position)

        def init_by_type(self, position):
            self.position = pygame.Rect(position[0], position[1], TILE_SIZE, TILE_SIZE)

            if self.type == 0:
                self.speed = 2
                self.health = 1
                self.unintrested = random.random() < 0.25
                if self.unintrested:
                    self.target_position = (
                        random.randint(2, 13) * TILE_SIZE,
                        random.randint(2, 13) * TILE_SIZE,
                    )

            