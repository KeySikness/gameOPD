import pygame
import os
import random
from settings import MAX_FALL_SPEED

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_group):
        super().__init__()
        self.platform_group = platform_group

        # Загрузка изображений
        self.images = self._load_images()
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect(topleft=(x, y))

        # Движение
        self.direction = random.choice([-1, 1])
        self.speed = 1.5
        self.gravity = 0.5
        self.velocity_y = 0
        self.on_ground = False

    def _load_images(self):
        return [
            pygame.image.load(os.path.join('assets', 'image', 'monster1.png')).convert_alpha(),
            pygame.image.load(os.path.join('assets', 'image', 'monster2.png')).convert_alpha()
        ]

    def update(self):
        self._apply_gravity()
        if self.on_ground:
            self._move_horizontally()
        self._check_collisions()

    def _apply_gravity(self):
        if not self.on_ground:
            self.velocity_y += self.gravity
            if self.velocity_y > MAX_FALL_SPEED:
                self.velocity_y = MAX_FALL_SPEED
            self.rect.y += self.velocity_y

    def _move_horizontally(self):
        # Пробуем шагнуть
        self.rect.x += self.direction * self.speed

        # Если нет платформы впереди или удар в стену — разворачиваемся
        if not self._has_platform_ahead() or self._hits_wall():
            self.rect.x -= self.direction * self.speed  # Откат шага
            self.direction *= -1

    def _has_platform_ahead(self):
        """Проверка: есть ли под ногой в направлении движения платформа"""
        if self.direction == -1:
            foot_x = self.rect.left - 1
        else:
            foot_x = self.rect.right + 1

        foot_y = self.rect.bottom + 1
        check_rect = pygame.Rect(foot_x, foot_y, 2, 2)

        return any(check_rect.colliderect(p.rect) for p in self.platform_group)

    def _hits_wall(self):
        """Проверка: есть ли платформа прямо сбоку, как стена"""
        self.rect.x += self.direction * 1
        collided = any(self.rect.colliderect(p.rect) for p in self.platform_group)
        self.rect.x -= self.direction * 1
        return collided

    def _check_collisions(self):
        self.on_ground = False
        for platform in self.platform_group:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y >= 0 and self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True

    def draw(self, surface, camera_x=0):
        draw_x = self.rect.x - camera_x
        surface.blit(self.image, (draw_x, self.rect.y))