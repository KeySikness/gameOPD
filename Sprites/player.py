import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            original_image = pygame.image.load(os.path.join('assets', 'image', 'witch.png')).convert_alpha()
            self.image = pygame.transform.scale(original_image, (64, 64))
            self.original_image_right = self.image
            self.original_image_left = pygame.transform.flip(self.image, True, False)
        except:
            self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 255), (32, 32), 32)
            self.original_image_right = self.image
            self.original_image_left = pygame.transform.flip(self.image, True, False)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        self.jump_power = -15
        self.velocity_y = 0
        self.velocity_x = 0  
        self.on_ground = False
        self.facing_right = True
        self.world_x = x

        # Новое: параметры здоровья
        self.max_health = 3
        self.health = self.max_health
        self.is_alive = True

    def update(self, platforms, stars=None):  
        if not self.is_alive:
            return  # не обновляем, если игрок мертв

        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.facing_right = True

        self.rect.x += self.velocity_x
        self.world_x = self.rect.x

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
                self.world_x = self.rect.x

        self.velocity_y += GRAVITY
        if self.velocity_y > PLAYER_SPEED:
            self.velocity_y = PLAYER_SPEED
        
        self.rect.y += self.velocity_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

        if stars:
            for star in stars:
                if self.rect.colliderect(star.rect):
                    star.collect() 

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

    def draw(self, screen, camera_offset):
        if not self.facing_right:
            screen.blit(self.original_image_left, (self.rect.x - camera_offset, self.rect.y))
        else:
            screen.blit(self.original_image_right, (self.rect.x - camera_offset, self.rect.y))

    def take_damage(self):
        if self.is_alive:
            self.health -= 1
            print(f"Игрок получил урон! Здоровье: {self.health}")
            if self.health <= 0:
                self.die()

    def die(self):
        self.is_alive = False
        print("Игрок погиб")

