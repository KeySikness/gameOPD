import pygame
import random
from settings import *
from Sprites.platform import Platform


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_group):
        super().__init__()
        self.platform_group = platform_group
        self.images = self.load_images()
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 1.5
        self.gravity = 0.5
        self.on_ground = False
        self.max_fall_speed = MAX_FALL_SPEED
        self.direction = random.choice([-1,1])

    def load_images(self):
        loaded_images = [
            pygame.image.load(os.path.join('assets', 'image', 'monster1.png')).convert_alpha(),
            pygame.image.load(os.path.join('assets', 'image', 'monster2.png')).convert_alpha()
        ]
        return loaded_images

    def update(self):
        self._patrol()
        self._apply_gravity()
        self._check_platform_collision()

    def _patrol(self):
        self.rect.x += self.speed * self.direction
        if not self._has_ground_ahead():
            self.direction *= -1

    def _has_ground_ahead(self):
        check_x = self.rect.midbottom[0] + self.direction * self.rect.width // 2
        check_y = self.rect.bottom + 5
        check_rect = pygame.Rect(check_x, check_y, 5, 5)
        return any(check_rect.colliderect(platform.rect) for platform in self.platform_group)

    def _apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def _check_platform_collision(self):
        self.on_ground = False
        for platform in self.platform_group:
            if self.rect.colliderect(platform.rect) and self.velocity_y >= 0:
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True

    def draw(self, surface, camera_x=0):
        x = self.rect.x - camera_x
        surface.blit(self.image, (x, self.rect.y))