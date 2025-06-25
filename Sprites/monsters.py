import pygame
import os
import random
from settings import MAX_FALL_SPEED

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_group):
        super().__init__()
        self.platform_group = platform_group
        self.is_alive = True
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 180
        self.platform = None

        self.alive_images = [
            pygame.image.load(os.path.join('assets', 'image', 'monster1.png')).convert_alpha(),
            pygame.image.load(os.path.join('assets', 'image', 'monster2.png')).convert_alpha()
        ]
        self.dead_image = pygame.image.load(os.path.join('assets', 'image', 'monster_death.png')).convert_alpha()
        self.image = random.choice(self.alive_images)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.direction = random.choice([-1, 1])
        self.speed = 4.0
        self.gravity = 0.5
        self.velocity_y = 0
        self.on_ground = False

        self._find_platform()

    def _find_platform(self):
        for platform in self.platform_group:
            if (self.rect.bottom >= platform.rect.top and self.rect.bottom <= platform.rect.bottom and self.rect.centerx >= platform.rect.left and self.rect.centerx <= platform.rect.right):
                self.platform = platform
                break

    def update(self):
        if self.is_dead:
            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.kill()
            return

        if not self.is_alive:
            return

        self._apply_gravity()
        if self.on_ground:
            self._move_horizontally()
        self._check_collisions()

    def die(self):
        """Обработка смерти монстра"""
        self.is_alive = False
        self.is_dead = True
        self.image = self.dead_image

        # Получаем координаты центра монстра
        center_x = self.rect.centerx

        # Создаем новый rect для кучки пыли
        self.rect = self.image.get_rect()

        # Позиционируем:
        self.rect.centerx = center_x  # Центр по X остается тем же

        if self.platform:
            # Ставим кучку пыли прямо на платформу
            self.rect.bottom = self.platform.rect.top
        else:
            # Если платформы нет, ставим на текущую позицию низа монстра
            self.rect.bottom = old_bottom

        self.rect.y += 5  # Опускаем еще на 5 пикселей

    def _apply_gravity(self):
        if not self.on_ground:
            self.velocity_y += self.gravity
            if self.velocity_y > MAX_FALL_SPEED:
                self.velocity_y = MAX_FALL_SPEED
            self.rect.y += self.velocity_y

    def _check_collisions(self):
        self.on_ground = False
        for platform in self.platform_group:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y >= 0 and self.rect.bottom <= platform.rect.bottom + 5:  # +5 допуск
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.platform = platform  # Запоминаем текущую платформу

    def _load_images(self):
        return [
            pygame.image.load(os.path.join('assets', 'image', 'monster1.png')).convert_alpha(),
            pygame.image.load(os.path.join('assets', 'image', 'monster2.png')).convert_alpha(),
        ]

    def _update_death_animation(self):
        self.current_death_frame += 1
        if self.current_death_frame >= self.death_animation_frames:
            self.kill()

    def _move_horizontally(self):
        self.rect.x += self.direction * self.speed

        if not self._has_platform_ahead() or self._hits_wall():
            self.rect.x -= self.direction * self.speed
            self.direction *= -1

    def _has_platform_ahead(self):
        if self.direction == -1:
            foot_x = self.rect.left - 1
        else:
            foot_x = self.rect.right + 1

        foot_y = self.rect.bottom + 1
        check_rect = pygame.Rect(foot_x, foot_y, 2, 2)

        return any(check_rect.colliderect(p.rect) for p in self.platform_group)

    def _hits_wall(self):
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

        # Debug для спрайтов
        # pygame.draw.rect(surface, (255, 0, 0), (draw_x, self.rect.y, self.rect.width, self.rect.height), 1)