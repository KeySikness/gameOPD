import pygame
import os

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_group):
        super().__init__()
        self.platform_group = platform_group

        image_path = os.path.join('assets', 'image', 'boss.png')
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.direction = -1
        self.base_speed = 2
        self.enraged_speed = 4
        self.speed = self.base_speed

        self.base_jump_strength = -12
        self.enraged_jump_strength = -18
        self.jump_strength = self.base_jump_strength

        self.max_hp = 5
        self.hp = self.max_hp

        self.enraged = False
        self.enrage_start_time = 0

        self.enrage_duration = 5000         # Длительность ярости
        self.rage_cycle_interval = 8000     # Период между стартами ярости

        self.gravity = 0.5
        self.velocity_y = 0
        self.on_ground = False

        self.jump_cooldown = 1000
        self.last_jump_time = pygame.time.get_ticks()

        self.last_rage_check_time = pygame.time.get_ticks()
        self.waiting_to_calm = False

    def update(self, player):
        current_time = pygame.time.get_ticks()

        # Запускаем ярость каждые N мс
        if not self.enraged and not self.waiting_to_calm:
            if current_time - self.last_rage_check_time >= self.rage_cycle_interval:
                self.enraged = True
                self.enrage_start_time = current_time
                self.speed = self.enraged_speed
                self.jump_strength = self.enraged_jump_strength

        # Проверка окончания ярости
        if self.enraged:
            if current_time - self.enrage_start_time >= self.enrage_duration:
                self.enraged = False
                self.waiting_to_calm = True  # ждем, пока приземлится
                self.last_rage_check_time = current_time

        # Если ждем приземления после ярости
        if self.waiting_to_calm and self.on_ground:
            self.speed = self.base_speed
            self.jump_strength = self.base_jump_strength
            self.waiting_to_calm = False

        self._patrol()

        # В обычном режиме смотрит на игрока
        if not self.enraged:
            self._face_player(player)

        # В ярости действует под гравитацией и прыгает
        if self.enraged or self.waiting_to_calm:
            self._apply_gravity()
            self._check_platform_collision()

    def _patrol(self):
        self.rect.x += self.speed * self.direction
        if not self._has_ground_ahead():
            self.direction *= -1
            self.image = pygame.transform.flip(self.image, True, False)

    def _has_ground_ahead(self):
        check_x = self.rect.midbottom[0] + self.direction * self.rect.width // 2
        check_y = self.rect.bottom + 5
        check_rect = pygame.Rect(check_x, check_y, 5, 5)
        return any(check_rect.colliderect(platform.rect) for platform in self.platform_group)

    def _face_player(self, player):
        if player.rect.centerx > self.rect.centerx and self.direction != 1:
            self.direction = 1
            self.image = pygame.transform.flip(self.image, True, False)
        elif player.rect.centerx < self.rect.centerx and self.direction != -1:
            self.direction = -1
            self.image = pygame.transform.flip(self.image, True, False)

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

                current_time = pygame.time.get_ticks()
                if current_time - self.last_jump_time >= self.jump_cooldown:
                    self.velocity_y = self.jump_strength
                    self.last_jump_time = current_time
                break

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

        bar_width = 100
        bar_height = 10
        hp_ratio = self.hp / self.max_hp
        hp_color = (255, 0, 0)

        bar_x = self.rect.x - camera_x + (self.rect.width - bar_width) // 2
        bar_y = self.rect.y - 20

        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()











