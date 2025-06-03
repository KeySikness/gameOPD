import pygame
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill('red')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 2

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