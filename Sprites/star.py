import pygame
import os
from settings import *

class Star(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor=1):
        super().__init__()
        self._load_image(scale_factor)
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False

    def _load_image(self, scale_factor):
        try:
            star_img = os.path.join('assets', 'image', 'star.png')
            self.image = pygame.image.load(star_img).convert_alpha()
            size = int(30 * scale_factor)
            self.image = pygame.transform.scale(self.image, (size, size))
        except:
            size = int(30 * scale_factor)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [
                (15 * scale_factor, 0),
                (20 * scale_factor, 20 * scale_factor),
                (0, 7 * scale_factor),
                (30 * scale_factor, 7 * scale_factor),
                (10 * scale_factor, 20 * scale_factor)
            ]
            pygame.draw.polygon(self.image, (255, 255, 0), points)

    def collect(self):
        if not self.collected:
            self.collected = True
            self.kill()
            return True
        return False