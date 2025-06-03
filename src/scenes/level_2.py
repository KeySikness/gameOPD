import pygame
import random
from settings import *
from scene_manager import SceneManager
from src.scenes.start_menu import Button
from Sprites import Platform, Player
from Sprites.clouds import Cloud
from Sprites.star import Star
from Sprites.enemy import Enemy

class Level2:
    def __init__(self):
        self.config = LEVEL2_CONFIG  # Загружаем конфигурацию
        self._init_base_variables()
        self.reset()

    def _init_base_variables(self):
        """Инициализация базовых переменных"""
        self.base_width = WIDTH
        self.base_height = HEIGHT
        self.scale_factor = 1
        self.scale_x = 1
        self.scale_y = 1
        self.font = pygame.font.Font(font_path, 24)
        self.level_font = pygame.font.Font(font_path, 36)

    def reset(self):
        """Полный сброс уровня"""
        self._init_sprite_groups()
        self._init_game_objects()
        self._init_game_state()
        self._init_ui_elements()

    def _init_sprite_groups(self):
        """Создание групп спрайтов"""
        self.game_objects = pygame.sprite.Group() 
        self.all_platforms = pygame.sprite.Group()
        self.visible_platforms = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

    def _init_game_objects(self):
        """Создание игровых объектов"""
        self.player = Player(*self.config['player_start_pos'])
        self._create_platforms()
        self._create_clouds()
        self._create_stars()
        self._create_enemies()
        self.game_objects.add(self.player)

    def _init_game_state(self):
        """Инициализация состояния игры"""
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.fill(self.config['background_color'])
        self.camera_offset = 0
        self.stars_collected = 0
        self._init_transition_effects()

    def _init_transition_effects(self):
        """Настройка эффектов перехода"""
        self.transition_alpha = 0
        self.transition_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.showing_completion = False
        self.game_over = False
        self.game_over_alpha = 0
        self.game_over_message = "Уровень не пройден"

    def _init_ui_elements(self):
        """Создание UI элементов"""
        self.back_button = Button(
            "Назад", 
            self.base_width - 170, 20, 
            150, 50,
            pygame.font.Font(font_path, 30),
            PURPLE_MID,
            WHITE,
            self.scale_factor
        )
        # Устанавливаем параметры границы
        self.back_button.border_color = WHITE
        self.back_button.border_width = 3
        self.back_button.rendered_text = self.back_button.font.render(self.back_button.text, True, self.back_button.text_color)

    def _create_enemies(self):
            for x, y in self.config['enemies_pos']:
                self.enemies.add(Enemy(x, y))

    def _create_platforms(self):
        """Генерация платформ из конфига"""
        for x, y in self.config['platform_positions']:
            self.all_platforms.add(Platform(x, y))
        self._update_visible_platforms()

    def _create_stars(self):
        """Размещение звезд на платформах"""
        platforms = sorted(self.all_platforms.sprites(), key=lambda p: p.rect.x)
        for idx in self.config['star_indices']:
            if idx < len(platforms):
                platform = platforms[idx]
                self.stars.add(Star(platform.rect.centerx, platform.rect.top - 50, self.scale_factor))

    def _create_clouds(self):
        """Генерация облаков с проверкой пересечений"""
        for config in self.config['cloud_config']:
            for _ in range(config["count"]):
                self._attempt_add_cloud(config)

    def _attempt_add_cloud(self, config):
        """Попытка добавить облако без пересечений"""
        x = random.randint(0, WIDTH)
        y = random.randint(*config["y_range"])
        cloud = Cloud(x, y, config["type"])
        
        if not any(abs(cloud.rect.x - c.rect.x) < cloud.min_distance and
            abs(cloud.rect.y - c.rect.y) < 100
            for c in self.clouds
        ):
            self.clouds.add(cloud)

    def _update_visible_platforms(self):
        """Обновление видимых платформ относительно камеры"""
        self.visible_platforms.empty()
        camera_x = self.player.rect.centerx - self.base_width // 2
        
        for platform in self.all_platforms:
            if (platform.rect.right > camera_x - 100 and 
                platform.rect.left < camera_x + self.base_width + 100):
                self.visible_platforms.add(platform)

    def update_layout(self, window_size):
        """Обработка изменения размера окна"""
        width, height = window_size
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        # Масштабирование шрифтов
        self.font = pygame.font.Font(font_path, int(24 * self.scale_factor))
        self.level_font = pygame.font.Font(font_path, int(36 * self.scale_factor))
        
        # Обновление кнопки (не создаём новую, а изменяем существующую)
        self.back_button.rect.x = int((self.base_width - 170) * self.scale_x)
        self.back_button.rect.y = int(20 * self.scale_y)
        self.back_button.rect.width = int(150 * self.scale_factor)
        self.back_button.rect.height = int(50 * self.scale_factor)
        self.back_button.font = pygame.font.Font(font_path, int(30 * self.scale_factor))
        self.back_button.scale_factor = self.scale_factor
        self.back_button.border_width = int(3 * self.scale_factor)
        self.back_button.rendered_text = self.back_button.font.render(self.back_button.text, True, self.back_button.text_color)

    def handle_event(self, event):
        """Обработка событий"""
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.check_click(pygame.mouse.get_pos()):
                SceneManager.get_instance().set('start')

    def update(self):
        """Основной игровой цикл"""
        self._update_button_state()
        self._check_game_over()
        
        if not self.game_over:
            self._update_game_objects()
            self._check_level_completion()

    def _update_button_state(self):
        """Обновление состояния кнопки"""
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.hovered = self.back_button.is_hovered(mouse_pos)

    def _check_game_over(self):
        """Проверка условий проигрыша"""
        if self.player.rect.top > HEIGHT and not self.game_over:
            self.game_over = True
            
        if self.game_over and self.game_over_alpha < 255:
            self.game_over_alpha += 5
            if self.game_over_alpha >= 255:
                self._transition_to_scene('game_over')

    def _update_game_objects(self):
        """Обновление игровых объектов"""
        for cloud in self.clouds:
            cloud.update(self.clouds)
                
        self._update_visible_platforms()
        self.player.handle_input()
        self.player.update(self.visible_platforms)
        self._check_star_collisions()

    def _check_star_collisions(self):
        """Проверка сбора звезд"""
        for star in self.stars:
            if self.player.rect.colliderect(star.rect) and star.collect():
                self.stars_collected += 1

    def _check_level_completion(self):
        """Проверка завершения уровня"""
        if self.stars_collected >= self.config['total_stars'] and not self.showing_completion:
            self.showing_completion = True
            self.transition_alpha = 0
            self.game_over_message = "Уровень пройден!"
            
        if self.showing_completion:
            self.transition_alpha += 5
            if self.transition_alpha >= 255:
                self._transition_to_scene('level_completed')

    def _transition_to_scene(self, scene_name):
        """Переход на другую сцену"""
        if scene_name == 'game_over':
            game_over_scene = SceneManager.get_instance().scenes['game_over']
            game_over_scene.set_message(self.game_over_message)
        SceneManager.get_instance().set(scene_name)

    def render(self, screen):
        """Отрисовка всего уровня"""
        current_size = screen.get_size()
        self._render_background(screen, current_size)
        self._render_game_objects(screen)
        self._render_ui(screen, current_size)
        self._render_transitions(screen, current_size)

    def _render_background(self, screen, current_size):
        """Отрисовка фона"""
        scaled_bg = pygame.transform.scale(self.background, current_size)
        screen.blit(scaled_bg, (0, 0))

    def _render_game_objects(self, screen):
        """Отрисовка игровых объектов"""
        camera_x = self.player.rect.centerx - self.base_width // 2
        
        # Отрисовка облаков
        for cloud in self.clouds:
            self._render_sprite(screen, cloud.image, cloud.rect)
        
        # Отрисовка платформ
        for platform in self.visible_platforms:
            self._render_sprite(screen, platform.image, platform.rect, camera_x)
        
        # Отрисовка звезд
        for star in self.stars:
            self._render_sprite(screen, star.image, star.rect, camera_x)
        
        # рисуем энемис
        for enemy in self.enemies:
            self._render_sprite(screen, enemy.image, enemy.rect, camera_x)

        # Отрисовка игрока
        player_img = (self.player.original_image_right if self.player.facing_right 
                     else self.player.original_image_left)
        self._render_player(screen, player_img)

    def _render_sprite(self, screen, image, rect, camera_x=0):
        """Отрисовка спрайта с масштабированием"""
        x = int((rect.x - camera_x) * self.scale_x)
        y = int(rect.y * self.scale_y)
        scaled_size = (
            int(rect.width * self.scale_factor),
            int(rect.height * self.scale_factor)
        )
        scaled_img = pygame.transform.scale(image, scaled_size)
        screen.blit(scaled_img, (x, y))

    def _render_player(self, screen, image):
        """Специальная отрисовка игрока (центрированная)"""
        x = int((self.base_width // 2 - self.player.rect.width // 2) * self.scale_x)
        y = int(self.player.rect.y * self.scale_y)
        scaled_size = (
            int(self.player.rect.width * self.scale_x),
            int(self.player.rect.height * self.scale_y)
        )
        scaled_img = pygame.transform.scale(image, scaled_size)
        screen.blit(scaled_img, (x, y))

    def _render_ui(self, screen, current_size):
        """Отрисовка интерфейса"""
        self.back_button.draw(screen)
        self._render_level_header(screen)
        self._render_stars_counter(screen)

    def _render_level_header(self, screen):
        """Отрисовка заголовка уровня"""
        level_text = self.level_font.render(
            self.config['level_name'], 
            True, 
            self.config['level_color']
        )
        text_rect = level_text.get_rect(center=(
            int(self.base_width // 2 * self.scale_x), 
            int(30 * self.scale_y)
        ))
        
        # Фон заголовка
        bg_width = text_rect.width + int(40 * self.scale_factor)
        bg_height = text_rect.height + int(20 * self.scale_factor)
        bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
        bg_rect.center = (
            int(self.base_width // 2 * self.scale_x), 
            int(30 * self.scale_y)
        )
        
        colors = self.config['ui_colors']
        pygame.draw.rect(screen, colors['bg'], bg_rect, border_radius=int(12 * self.scale_factor))
        pygame.draw.rect(screen, colors['border'], bg_rect, 
                        border_radius=int(12 * self.scale_factor), 
                        width=int(2 * self.scale_factor))
        screen.blit(level_text, text_rect)

    def _render_stars_counter(self, screen):
        """Отрисовка счетчика звезд"""
        stars_text =self.font.render(
            f"Звезды: {self.stars_collected}/{self.config['total_stars']}", 
            True, 
            WHITE
        )
        screen.blit(stars_text, (int(20 * self.scale_x), int(20 * self.scale_y)))

    def _render_transitions(self, screen, current_size):
        """Отрисовка переходов между сценами"""
        if self.transition_surface.get_size() != current_size:
            self.transition_surface = pygame.Surface(current_size, pygame.SRCALPHA)
        
        if self.showing_completion:
            self.transition_surface.fill((0, 0, 0, self.transition_alpha))
            screen.blit(self.transition_surface, (0, 0))
            
        if self.game_over:
            self.transition_surface.fill((0, 0, 0, self.game_over_alpha))
            screen.blit(self.transition_surface, (0, 0))