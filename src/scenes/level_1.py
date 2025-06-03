import pygame
import random
import os
from settings import *
from scene_manager import SceneManager
from src.scenes.start_menu import Button
from Sprites import Platform, Player
from src.scenes.game_over import GameOver
from Sprites.clouds import Cloud  # Импортируем класс Cloud из вашего файла

class Star(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor=1):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join('assets', 'image', 'star.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(30 * scale_factor), int(30 * scale_factor)))
        except:
            self.image = pygame.Surface((int(30 * scale_factor), int(30 * scale_factor)), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 255, 0), 
                              [(15 * scale_factor, 0), 
                               (20 * scale_factor, 20 * scale_factor), 
                               (0, 7 * scale_factor), 
                               (30 * scale_factor, 7 * scale_factor), 
                               (10 * scale_factor, 20 * scale_factor)])
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False

    def collect(self):
        if not self.collected:
            self.collected = True
            self.kill()
            return True
        return False

class Level1:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.base_width = WIDTH
        self.base_height = HEIGHT
        self.scale_factor = 1
        self.scale_x = 1
        self.scale_y = 1
        
        # Инициализация групп спрайтов
        self.all_platforms = pygame.sprite.Group()
        self.visible_platforms = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        
        # Инициализация игровых объектов
        self._init_platforms()
        self._init_clouds()
        self._init_stars()
        
        # Игрок
        self.player = Player(100, HEIGHT - 200)
        
        # Интерфейс
        self.font = pygame.font.Font(font_path, 24)
        self.level_font = pygame.font.Font(font_path, 36)
        self.back_button = self._create_back_button()
        
        # Состояние уровня
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.fill(PURPLE_DARK)
        self.camera_offset = 0
        self.stars_collected = 0
        self.total_stars = 3
        self.platform_spacing = 200
        
        # Анимация перехода
        self.transition_alpha = 0
        self.transition_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.showing_completion = False
        self.transition_speed = 5
        
        # Состояние проигрыша
        self.game_over = False
        self.game_over_alpha = 0
        self.game_over_speed = 5
        self.game_over_message = "Уровень не пройден"

    def _init_platforms(self):
        platform_positions = [
            (100, HEIGHT - 50),
            (300, HEIGHT - 100),
            (500, HEIGHT - 150),
            (700, HEIGHT - 200),
            (900, HEIGHT - 100),
            (1100, HEIGHT - 150),
            (1300, HEIGHT - 200),
            (1500, HEIGHT - 50)
        ]
        
        for x, y in platform_positions:
            platform = Platform(x, y)
            self.all_platforms.add(platform)
        
        for i, platform in enumerate(sorted(self.all_platforms.sprites(), key=lambda p: p.rect.x)):
            if i < 5:
                self.visible_platforms.add(platform)

    def _update_visible_platforms(self):
        self.visible_platforms.empty()
        camera_x = self.player.rect.centerx - self.base_width // 2
        
        # Берем все платформы в видимой области + небольшой запас
        for platform in self.all_platforms:
            if (platform.rect.right > camera_x - 100 and 
                platform.rect.left < camera_x + self.base_width + 100):
                self.visible_platforms.add(platform)

    def _init_stars(self):
        sorted_platforms = sorted(self.all_platforms.sprites(), key=lambda p: p.rect.x)
        star_platform_indices = [1, 3, 5]
        
        for index in star_platform_indices:
            if index < len(sorted_platforms):
                platform = sorted_platforms[index]
                x = platform.rect.centerx
                y = platform.rect.top - 50
                self.stars.add(Star(x, y, self.scale_factor))

    def _init_clouds(self):
        cloud_config = [
            {"type": "small", "count": 6},
            {"type": "medium", "count": 4},
            {"type": "big", "count": 3}
        ]
        
        for config in cloud_config:
            for _ in range(config["count"]):  # Используем _ вместо i, так как i не используется
                # Для каждого типа облаков используем разные диапазоны Y
                if config["type"] == "small":
                    y_range = (50, HEIGHT // 3)
                elif config["type"] == "medium":
                    y_range = (HEIGHT // 3, HEIGHT // 2)
                else:  # big
                    y_range = (HEIGHT // 2, HEIGHT * 2 // 3)
                
                x = random.randint(0, WIDTH)
                y = random.randint(*y_range)
                new_cloud = Cloud(x, y, config["type"])
                
                # Проверяем, чтобы облака не пересекались
                too_close = any(
                    abs(new_cloud.rect.x - cloud.rect.x) < new_cloud.min_distance and
                    abs(new_cloud.rect.y - cloud.rect.y) < 100
                    for cloud in self.clouds
                )
                
                if not too_close:
                    self.clouds.add(new_cloud)
                else:
                    # Если облако слишком близко, пробуем снова с другими координатами
                    continue

    def _create_back_button(self):
        return Button(
            "Назад", 
            self.base_width - 170, 20, 
            150, 50,
            pygame.font.Font(font_path, 30),
            PURPLE_MID,
            WHITE,
            self.scale_factor
        )

    def update_layout(self, window_size):
        width, height = window_size
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        self.font = pygame.font.Font(font_path, int(24 * self.scale_factor))
        self.level_font = pygame.font.Font(font_path, int(36 * self.scale_factor))
        
        self.back_button = Button(
            "Назад", 
            int((self.base_width - 170) * self.scale_x), 
            int(20 * self.scale_y),
            int(150 * self.scale_factor), 
            int(50 * self.scale_factor),
            pygame.font.Font(font_path, int(30 * self.scale_factor)),
            PURPLE_MID,
            WHITE,
            self.scale_factor
        )

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.check_click(pygame.mouse.get_pos()):
                SceneManager.get_instance().set('start')

    def update(self):
        # Обновляем состояние наведения на кнопку
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.hovered = self.back_button.is_hovered(mouse_pos)
        
        if self.player.rect.left < 0:
            self.player.rect.left = 0
        
        if self.player.rect.top > HEIGHT and not self.game_over:
            self.game_over = True
            
        if self.game_over and self.game_over_alpha < 255:
            self.game_over_alpha += self.game_over_speed
            if self.game_over_alpha >= 255:
                game_over_scene = SceneManager.get_instance().scenes['game_over']
                game_over_scene.set_message(self.game_over_message)
                SceneManager.get_instance().set('game_over')
                return
                
        if self.game_over:
            return
            
        # Обновляем облака с использованием метода update из класса Cloud
        for cloud in self.clouds:
            cloud.update(self.clouds)
                
        self._update_visible_platforms()
        self.player.handle_input()
        self.player.update(self.visible_platforms)
        
        # Проверка коллизий со звездами
        for star in self.stars:
            if self.player.rect.colliderect(star.rect):
                if star.collect():
                    self.stars_collected += 1
                    
        # Проверка на завершение уровня
        if self.stars_collected >= self.total_stars and not self.showing_completion:
            self.showing_completion = True
            self.transition_alpha = 0
            self.game_over_message = "Уровень пройден!"
            
        if self.showing_completion:
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                SceneManager.get_instance().set('level_completed')

    def render(self, screen):
        current_width, current_height = screen.get_size()
        
        scaled_bg = pygame.transform.scale(self.background, (current_width, current_height))
        screen.blit(scaled_bg, (0, 0))
        
        # Рендерим облака
        for cloud in self.clouds:
            cloud_rect = cloud.rect.copy()
            cloud_rect.x = int(cloud_rect.x * self.scale_x)
            cloud_rect.y = int(cloud_rect.y * self.scale_y)
            cloud_rect.width = int(cloud_rect.width * self.scale_factor)
            cloud_rect.height = int(cloud_rect.height * self.scale_factor)
            scaled_image = pygame.transform.scale(cloud.image, (cloud_rect.width, cloud_rect.height))
            screen.blit(scaled_image, (cloud_rect.x, cloud_rect.y))
        
        camera_x = self.player.rect.centerx - self.base_width // 2
        
        for platform in self.visible_platforms:
            platform_screen_x = int((platform.rect.x - camera_x) * self.scale_x)
            platform_screen_y = int(platform.rect.y * self.scale_y)
            scaled_width = int(platform.rect.width * self.scale_x)
            scaled_height = int(platform.rect.height * self.scale_y)
            scaled_image = pygame.transform.scale(platform.image, (scaled_width, scaled_height))
            screen.blit(scaled_image, (platform_screen_x, platform_screen_y))
        
        for star in self.stars:
            star_screen_x = int((star.rect.x - camera_x) * self.scale_x)
            star_screen_y = int(star.rect.y * self.scale_y)
            scaled_width = int(star.rect.width * self.scale_x)
            scaled_height = int(star.rect.height * self.scale_y)
            scaled_image = pygame.transform.scale(star.image, (scaled_width, scaled_height))
            screen.blit(scaled_image, (star_screen_x, star_screen_y))
        
        player_screen_x = int((self.base_width // 2 - self.player.rect.width // 2) * self.scale_x)
        player_screen_y = int(self.player.rect.y * self.scale_y)
        scaled_width = int(self.player.rect.width * self.scale_x)
        scaled_height = int(self.player.rect.height * self.scale_y)
        
        if self.player.facing_right:
            scaled_player = pygame.transform.scale(self.player.original_image_right, 
                                                 (scaled_width, scaled_height))
            screen.blit(scaled_player, (player_screen_x, player_screen_y))
        else:
            scaled_player = pygame.transform.scale(self.player.original_image_left, 
                                                 (scaled_width, scaled_height))
            screen.blit(scaled_player, (player_screen_x, player_screen_y))
        
        # Рендерим кнопку с анимацией
        self.back_button.draw(screen)
        
        level_text = self.level_font.render("Уровень 1", True, (251, 255, 0))
        text_rect = level_text.get_rect(center=(int(self.base_width // 2 * self.scale_x), 
                                       int(30 * self.scale_y)))
        
        stars_text = self.font.render(f"Звезды: {self.stars_collected}/{self.total_stars}", True, WHITE)
        screen.blit(stars_text, (int(20 * self.scale_x), int(20 * self.scale_y)))
        
        bg_color = (180, 185, 0)
        border_color = (130, 135, 0)
        bg_width = text_rect.width + int(40 * self.scale_factor)
        bg_height = text_rect.height + int(20 * self.scale_factor)
        bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
        bg_rect.center = (int(self.base_width // 2 * self.scale_x), int(30 * self.scale_y))
        
        pygame.draw.rect(screen, bg_color, bg_rect, border_radius=int(12 * self.scale_factor))
        pygame.draw.rect(screen, border_color, bg_rect, border_radius=int(12 * self.scale_factor), 
                        width=int(2 * self.scale_factor))
        screen.blit(level_text, text_rect)
        
        if self.showing_completion:
            if (self.transition_surface.get_width() != current_width or 
                self.transition_surface.get_height() != current_height):
                self.transition_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
            
            self.transition_surface.fill((0, 0, 0, self.transition_alpha))
            screen.blit(self.transition_surface, (0, 0))
            
        if self.game_over:
            if (self.transition_surface.get_width() != current_width or 
                self.transition_surface.get_height() != current_height):
                self.transition_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
            
            self.transition_surface.fill((0, 0, 0, self.game_over_alpha))
            screen.blit(self.transition_surface, (0, 0))