import pygame
import random
from settings import *
from scene_manager import SceneManager
from src.scenes.start_menu import Button
from Sprites import Platform, Player
from Sprites.clouds import Cloud
from Sprites.star import Star

class Level1:
    def __init__(self):
        self.config = LEVEL1_CONFIG
        self._init_base_variables()
        self.reset()

    def _init_base_variables(self):
        self.base_width = WIDTH
        self.base_height = HEIGHT
        self.scale_factor = 1
        self.scale_x = 1
        self.scale_y = 1
        self.font = pygame.font.Font(font_path, 24)
        self.level_font = pygame.font.Font(font_path, 36)

    def reset(self):
        self._init_sprite_groups()
        self._init_game_objects()
        self._init_game_state()
        self._init_ui_elements()

    def _init_sprite_groups(self):
        self.game_objects = pygame.sprite.Group()
        self.all_platforms = pygame.sprite.Group()
        self.visible_platforms = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()

    def _init_game_objects(self):
        self.player = Player(*self.config['player_start_pos'])
        self._create_platforms()
        self._create_clouds()
        self._create_stars()
        self.game_objects.add(self.player)

    def _init_game_state(self):
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.fill(self.config['background_color'])
        self.camera_offset = 0
        self.stars_collected = 0
        self._init_transition_effects()

    def _init_transition_effects(self):
        self.transition_alpha = 0
        self.transition_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.showing_completion = False
        self.game_over = False
        self.game_over_alpha = 0
        self.game_over_message = "Уровень не пройден"

    def _init_ui_elements(self):
        self.back_button = Button(
            "Назад",
            self.base_width - 170, 20,
            150, 50,
            pygame.font.Font(font_path, 30),
            PURPLE_MID,
            WHITE,
            self.scale_factor
        )
        self.back_button.border_color = WHITE
        self.back_button.border_width = 3
        self.back_button.rendered_text = self.back_button.font.render(self.back_button.text, True,
                                                                      self.back_button.text_color)

    def _create_platforms(self):
        for x, y in self.config['platform_positions']:
            platform = Platform(x, y)
            platform.rect.x = x
            platform.rect.y = y
            self.all_platforms.add(platform)
        self._update_visible_platforms()

    def _create_stars(self):
        platforms = sorted(self.all_platforms.sprites(), key=lambda p: p.rect.x)
        for idx in self.config['star_indices']:
            if idx < len(platforms):
                platform = platforms[idx]
                star = Star(platform.rect.centerx, platform.rect.top - 50, self.scale_factor)
                self.stars.add(star)

    def _create_clouds(self):
        for config in self.config['cloud_config']:
            for _ in range(config["count"]):
                self._attempt_add_cloud(config)

    def _attempt_add_cloud(self, config):
        x = random.randint(0, WIDTH)
        y = random.randint(*config["y_range"])
        cloud = Cloud(x, y, config["type"])

        if not any(
                abs(cloud.rect.x - c.rect.x) < cloud.min_distance and
                abs(cloud.rect.y - c.rect.y) < 100
                for c in self.clouds
        ):
            self.clouds.add(cloud)

    def _update_visible_platforms(self):
        self.visible_platforms.empty()
        camera_x = self.player.rect.centerx - self.base_width // 2

        for platform in self.all_platforms:
            if (platform.rect.right > camera_x - 100 and
                    platform.rect.left < camera_x + self.base_width + 100):
                self.visible_platforms.add(platform)

    def update_layout(self, window_size):
        width, height = window_size
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.scale_factor = min(self.scale_x, self.scale_y)

        self.font = pygame.font.Font(font_path, int(24 * self.scale_factor))
        self.level_font = pygame.font.Font(font_path, int(36 * self.scale_factor))

        self.back_button.rect.x = int((self.base_width - 170) * self.scale_x)
        self.back_button.rect.y = int(20 * self.scale_y)
        self.back_button.rect.width = int(150 * self.scale_factor)
        self.back_button.rect.height = int(50 * self.scale_factor)
        self.back_button.font = pygame.font.Font(font_path, int(30 * self.scale_factor))
        self.back_button.scale_factor = self.scale_factor
        self.back_button.border_width = int(3 * self.scale_factor)
        self.back_button.rendered_text = self.back_button.font.render(self.back_button.text, True,
                                                                      self.back_button.text_color)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.check_click(pygame.mouse.get_pos()):
                SceneManager.get_instance().set('start')

    def update(self):
        self._update_button_state()
        self._check_game_over()

        if not self.game_over:
            self._update_game_objects()
            self._check_level_completion()

    def _update_button_state(self):
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.hovered = self.back_button.is_hovered(mouse_pos)

    def _check_game_over(self):
        if (self.player.rect.top > HEIGHT or
                (hasattr(self.player, 'is_death_animation_complete') and
                 self.player.is_death_animation_complete()) and not self.game_over):
            self.game_over = True

        if self.game_over and self.game_over_alpha < 255:
            self.game_over_alpha += 5
        if self.game_over_alpha >= 255:
            self._transition_to_scene('game_over')

    def _update_game_objects(self):
        for cloud in self.clouds:
            cloud.update(self.clouds)

        self._update_visible_platforms()
        self.player.handle_input()
        self.player.update(self.visible_platforms)

        stars_to_remove = []
        for star in self.stars:
            if self.player.rect.colliderect(star.rect):
                if star.collect():
                    stars_to_remove.append(star)
                    self.stars_collected += 1

        for star in stars_to_remove:
            self.stars.remove(star)

    def _check_level_completion(self):
        if self.stars_collected >= self.config['total_stars'] and not self.showing_completion:
            self.showing_completion = True
            self.transition_alpha = 0
            self.game_over_message = "Уровень пройден!"

            level_completed = SceneManager.get_instance().scenes.get('level_completed')
            if level_completed:
                level_completed.set_current_level('level1')

        if self.showing_completion:
            self.transition_alpha += 5
            if self.transition_alpha >= 255:
                self._transition_to_scene('level_completed')

    def _transition_to_scene(self, scene_name):
        if scene_name == 'game_over':
            game_over_scene = SceneManager.get_instance().scenes['game_over']
            game_over_scene.set_message(self.game_over_message)
        SceneManager.get_instance().set(scene_name)

    def render(self, screen):
        current_size = screen.get_size()
        self._render_background(screen, current_size)
        self._render_game_objects(screen)
        self._render_ui(screen, current_size)
        self._render_transitions(screen, current_size)

    def _render_background(self, screen, current_size):
        scaled_bg = pygame.transform.scale(self.background, current_size)
        screen.blit(scaled_bg, (0, 0))

    def _render_game_objects(self, screen):
        camera_x = self.player.rect.centerx - self.base_width // 2

        for cloud in self.clouds:
            self._render_sprite(screen, cloud.image, cloud.rect)

        for platform in self.visible_platforms:
            self._render_sprite(screen, platform.image, platform.rect, camera_x)

        for star in self.stars:
            self._render_sprite(screen, star.image, star.rect, camera_x)

        # Рендеринг игрока
        self.player.draw(screen, camera_x)

    def _render_sprite(self, screen, image, rect, camera_x=0):
        x = int((rect.x - camera_x) * self.scale_x)
        y = int(rect.y * self.scale_y)
        scaled_size = (
            int(rect.width * self.scale_factor),
            int(rect.height * self.scale_factor)
        )
        scaled_img = pygame.transform.scale(image, scaled_size)
        screen.blit(scaled_img, (x, y))

    def _render_ui(self, screen, current_size):
        self.back_button.draw(screen)
        self._render_level_header(screen)
        self._render_stars_counter(screen)

    def _render_level_header(self, screen):
        level_text = self.level_font.render(
            self.config['level_name'],
            True,
            self.config['level_color']
        )
        text_rect = level_text.get_rect(center=(
            int(self.base_width // 2 * self.scale_x),
            int(30 * self.scale_y)
        ))

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
        stars_text = self.font.render(
            f"Звезды: {self.stars_collected}/{self.config['total_stars']}",
            True,
            WHITE
        )
        screen.blit(stars_text, (int(20 * self.scale_x), int(20 * self.scale_y)))

    def _render_transitions(self, screen, current_size):
        if self.transition_surface.get_size() != current_size:
            self.transition_surface = pygame.Surface(current_size, pygame.SRCALPHA)

        if self.showing_completion:
            self.transition_surface.fill((0, 0, 0, self.transition_alpha))
            screen.blit(self.transition_surface, (0, 0))

        if self.game_over:
            self.transition_surface.fill((0, 0, 0, self.game_over_alpha))
            screen.blit(self.transition_surface, (0, 0))