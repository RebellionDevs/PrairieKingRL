
class CowboyBullet:
    def __init__(self, position, motion, damage):
        self.position = position
        self.damage = damage

        if isinstance(motion, tuple):
            self.motion = motion
        else:
            d = motion
            dirs = [(0, -8), (8, 0), (0, 8), (-8, 0)]
            self.motion = dirs[d]