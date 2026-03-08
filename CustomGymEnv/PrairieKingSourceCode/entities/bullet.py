from settings import *

class Bullet:
    def __init__(self, position, damage, motion = None, direction = None):
        self.position = pygame.Vector2(position)
        self.damage = damage

        if motion is not None:
            self.motion = pygame.Vector2(motion)

        elif direction is not None:
            self.motion = self._getMotionFromDirection(direction)

        else: self.motion = pygame.Vector2(0, 0)

    def _getMotionFromDirection(self, direction):
        directions = {
            0 : (0, -8),
            1 : (8, 0),
            2 : (0, 8),
            3 : (-8, 0)
        }

        move = directions.get(direction, (0, 0))
        return pygame.Vector2(move)
