import pygame
import random
from settings import *
from Sprites.platform import Platform

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_group, monster_type=1):
        super().__init__()
        
        self.type = monster_type
        image_path = f'assets/image/monster{monster_type}.png'
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = self.original_image
        self.rect = self.original_image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 2.0 
        self.gravity = GRAVITY
        self.max_fall_speed = MAX_FALL_SPEED
        
        self.platform_group = platform_group
        self.direction = random.choice([-1, 1])  
        self.platform = None
        
        self._find_platform()
        if self.platform:
            self.rect.bottom = self.platform.rect.top
    
    def _find_platform(self):
        for platform in self.platform_group:
            if (self.rect.colliderect(platform.rect) and 
                abs(self.rect.bottom - platform.rect.top) < 10):
                self.platform = platform
                return
        self.platform = None
    
    def update(self):
        self.velocity_y += self.gravity
        if self.velocity_y > self.max_fall_speed:
            self.velocity_y = self.max_fall_speed
        
        self.velocity_x = self.direction * self.speed

        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self._check_platform_collision()
        
        if self.platform:
            if (self.direction > 0 and self.rect.right > self.platform.rect.right) or \
               (self.direction < 0 and self.rect.left < self.platform.rect.left):
                self.direction *= -1 
    
    def _check_platform_collision(self):
        if self.platform:
            if not self.rect.colliderect(self.platform.rect) or \
               abs(self.rect.bottom - self.platform.rect.top) > 10:
                self.platform = None
        
        if not self.platform and self.velocity_y > 0:
            self._find_platform()
            if self.platform:
                self.rect.bottom = self.platform.rect.top
                self.velocity_y = 0
    
    def draw(self, surface, camera_x=0):
        x = self.rect.x - camera_x
        surface.blit(self.image, (x, self.rect.y))