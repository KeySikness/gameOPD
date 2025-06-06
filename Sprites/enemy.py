import pygame
from settings import *
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = self.load_images()
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 2

    def load_images(self):
        loaded_images = [
            pygame.image.load(os.path.join('assets', 'image', 'monster1.png')).convert_alpha(),
            pygame.image.load(os.path.join('assets', 'image', 'monster2.png')).convert_alpha()
        ]
        return loaded_images


    def update(self):
        # Простое движение врага взад-вперед по горизонтали
        self.rect.x += self.direction * self.speed
        
        # Проверка границ движения и изменение направления
        if hasattr(self, 'min_x') and hasattr(self,'max_x'):
            if self.rect.x <= self.min_x:
                self.rect.x = self.min_x
                self.direction = 1
            elif self.rect.x >= self.max_x:
                self.rect.x = self.max_x
                self.direction = -1