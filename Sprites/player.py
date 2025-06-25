import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.ground_offset = 10

        self.animations = self._load_all_animations()
        self._validate_animations()
        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(midbottom=(x, y + self.ground_offset))
        self.collision_rect = self._create_collision_rect()

        self.state = 'idle'
        self.facing_right = True
        self.animation_frame = 0
        self.animation_speed = 0.15

        self.speed = 5
        self.jump_power = -15
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False

        self.is_alive = True
        self.is_dying = False
        self.death_animation_complete = False

    def _load_all_animations(self):
        animations = {
            'idle': self._load_animation_frames('player/witch_idle', 6),
            'run': self._load_animation_frames('player/witch_run', 8),
            'death': self._load_animation_frames('player/witch_death', 3)
        }

        fallback = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(fallback, (255, 255, 255), (32, 32), 30)

        for state in animations:
            if not animations[state]:
                animations[state] = [fallback]

        return animations

    def _validate_animations(self):
        for state, frames in self.animations.items():
            if not frames:
                print(f": {state} анимация не загрузилась")
            for i, frame in enumerate(frames):
                if frame.get_size() != (64, 64):
                    print(f"внемляй блин: {state} фрейм {i} не того размера")

    def _load_animation_frames(self, folder_path, frame_count):
        frames = []
        for i in range(frame_count):
            try:
                frame_path = os.path.join('assets', 'animation', folder_path, f'{i}.png')
                frame = pygame.image.load(frame_path).convert_alpha()
                frame = pygame.transform.scale(frame, (64, 64))
                frames.append(frame)
            except Exception as e:
                print(f"ошибка при {folder_path} фрейме {i}: {str(e)}")
                continue
        return frames

    def _create_collision_rect(self):
        return pygame.Rect(
            self.rect.x,
            self.rect.bottom - self.ground_offset,
            self.rect.width,
            self.rect.height
        )

    def update(self, platforms):
        if not self.is_alive or self.is_dying:
            self._update_animation()
            return

        # Гравитация
        self.velocity_y += GRAVITY
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED

        # Движение
        self._handle_movement()
        self._update_position()
        self._handle_collisions(platforms)
        self._update_animation()

    def _handle_movement(self):
        keys = pygame.key.get_pressed()
        self.velocity_x = 0

        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.facing_right = False
            self.state = 'run'
        elif keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.facing_right = True
            self.state = 'run'
        else:
            self.state = 'idle'

    def _update_position(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.bottom = self.rect.bottom - self.ground_offset

    def _handle_collisions(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.collision_rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Падение
                    self.rect.bottom = platform.rect.top + self.ground_offset
                    self.collision_rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:  # Прыжок
                    self.rect.top = platform.rect.bottom + self.ground_offset
                    self.collision_rect.top = platform.rect.bottom
                    self.velocity_y = 0

    def _update_animation(self):
        if not self.animations[self.state]:
            return

        self.animation_frame += self.animation_speed

        if self.state == 'death':
            if self.animation_frame >= len(self.animations['death']):
                self.animation_frame = len(self.animations['death']) - 1
                self.death_animation_complete = True
        else:
            if self.animation_frame >= len(self.animations[self.state]):
                self.animation_frame = 0

        frames = self.animations[self.state]
        frame_index = int(self.animation_frame) % len(frames)
        self.image = frames[frame_index]

        if not self.facing_right and self.state != 'death':
            self.image = pygame.transform.flip(self.image, True, False)

    def handle_input(self):
        if not self.is_alive or self.is_dying:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

    def draw(self, screen, camera_offset):
        if hasattr(self, 'image') and self.image:
            screen.blit(self.image, (self.rect.x - camera_offset, self.rect.y))

    def take_damage(self):
        if self.is_alive and not self.is_dying:
            self.die()

    def die(self):
        self.is_dying = True
        self.state = 'death'
        self.animation_frame = 0
        self.velocity_x = 0
        self.velocity_y = 0

    def is_death_animation_complete(self):
        return self.death_animation_complete