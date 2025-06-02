import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Загрузка изображения
        try:
            self.image = pygame.image.load(os.path.join('assets', 'image', 'witch.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (64, 64))
        except:
            # Запасной вариант, если изображение не загрузилось
            self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 255), (32, 32), 32)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        self.jump_power = -15
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True
        self.world_x = x  # Глобальная позиция игрока в мире

    def update(self, platforms):
        # Гравитация
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Проверка коллизий с платформами
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Падаем вниз
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Двигаемся вверх
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Движение влево/вправо
        if keys[pygame.K_a]:
            # Полное ограничение движения влево у края экрана
            if self.rect.left - self.speed > 0:  # Проверяем, не выйдем ли за границу
                self.rect.x -= self.speed
                self.world_x -= self.speed
            else:
                # Если пытаемся выйти за границу - ставим точно у края
                self.rect.left = 0
                self.world_x = self.rect.x
            self.facing_right = False
            
        if keys[pygame.K_d]:
            # Двигаемся вправо без ограничений
            self.rect.x += self.speed
            self.world_x += self.speed
            self.facing_right = True
        
        # Прыжок
        if keys[pygame.K_w] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

    def draw(self, screen, camera_offset):
        # Отображаем игрока с учетом смещения камеры
        screen.blit(
            self.image if self.facing_right else pygame.transform.flip(self.image, True, False),
            (self.rect.x - camera_offset, self.rect.y)
        )
