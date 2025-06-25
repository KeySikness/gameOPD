import pygame
import random
from settings import *
from scene_manager import SceneManager
from src.scenes.start_menu import Button
from Sprites import Platform, Player, Star
from Sprites.clouds import Cloud
from Sprites.monsters import Monster


class Level2:
    def __init__(self):
        self.config = {
            'background_color': PURPLE_DARK,
            'level_name': "Уровень 2",
            'level_color': PURPLE_NEON,
            'ui_colors': {
                'bg': PURPLE_MID,
                'border': PURPLE_LIGHT
            },
            'player_start_pos': (100, HEIGHT - 150),
            'platform_positions': self._generate_platforms(),
            'star_indices': [2, 5, 8],
            'cloud_config': [
                {"type": "small", "count": 6, "y_range": (50, HEIGHT // 3)},
                {"type": "medium", "count": 4, "y_range": (HEIGHT // 3, HEIGHT // 2)},
                {"type": "big", "count": 3, "y_range": (HEIGHT // 2, HEIGHT * 2 // 3)}
            ],
            'total_stars': 3
        }

        self._init_base_variables()
        self.reset()

    def _check_monster_collisions(self):
        if not self.player.is_alive:
            return

        for monster in self.monsters:
            if monster.is_dead:
                continue

            if monster.is_alive and self.player.collision_rect.colliderect(monster.rect):
                if (self.player.velocity_y > 0 and
                        self.player.rect.bottom < monster.rect.centery and
                        self.player.rect.right > monster.rect.left and
                        self.player.rect.left < monster.rect.right):
                    monster.die()
                    self.player.velocity_y = -15
                    self.player.rect.y -= 10
                else:
                    self.game_over = True
                    self.game_over_message = "Уровень не пройден"

    def _player_dies(self):
        self.player.die()
        self.game_over_message = "Уровень не пройден"

    def _generate_platforms(self):
        platform_width = 100
        platform_height = 20
        platform_count = (WIDTH // platform_width) + 1

        platforms = [(0, HEIGHT - platform_height)]

        for i in range(1, platform_count):
            x = i * platform_width
            platforms.append(
                (x if x + platform_width <= WIDTH else WIDTH - platform_width,
                 HEIGHT - platform_height)
            )

        return platforms

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
        self.monsters = pygame.sprite.Group()

    def _init_game_objects(self):
        self.player = Player(*self.config['player_start_pos'])
        self._create_platforms()
        self._create_clouds()
        self._create_stars()
        self._create_monsters()
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

    def _create_platforms(self):
        for x, y in self.config['platform_positions']:
            platform = Platform(x, y)
            self.all_platforms.add(platform)
        self._update_visible_platforms()

    def _create_stars(self):
        platforms = sorted(self.all_platforms.sprites(), key=lambda p: p.rect.x)
        for idx in self.config['star_indices']:
            if idx < len(platforms):
                platform = platforms[idx]
                self.stars.add(Star(platform.rect.centerx, platform.rect.top - 50, self.scale_factor))

    def _create_clouds(self):
        for config in self.config['cloud_config']:
            for _ in range(config["count"]):
                self._attempt_add_cloud(config)

    def _create_monsters(self):
        platforms_sorted = sorted(self.all_platforms.sprites(), key=lambda p: p.rect.x)
        if not platforms_sorted:
            return

        platform = platforms_sorted[-1]
        positions = [
            (platform.rect.right - 400, platform.rect.top - 50),
            (platform.rect.centerx, platform.rect.top - 50)
        ]

        for x, y in positions:
            monster = Monster(x, y, self.all_platforms)
            self.monsters.add(monster)

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
        self.back_button.rendered_text = self.back_button.font.render(
            self.back_button.text,
            True,
            self.back_button.text_color
        )

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

        self.monsters.update()

    def _update_button_state(self):
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.hovered = self.back_button.is_hovered(mouse_pos)

    def _check_game_over(self):
        if (self.player.rect.top > HEIGHT or
            (self.player.is_dying and self.player.is_death_animation_complete())) and not self.game_over:
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
        self._check_monster_collisions()
        self._check_star_collisions()

    def _check_star_collisions(self):
        stars_to_remove = [star for star in self.stars
                           if self.player.collision_rect.colliderect(star.rect) and star.collect()]
        for star in stars_to_remove:
            self.stars.remove(star)
            self.stars_collected += 1

    def _check_level_completion(self):
        if self.stars_collected >= self.config['total_stars'] and not self.showing_completion:
            self.showing_completion = True
            self.transition_alpha = 0
            self.game_over_message = "Уровень пройден!"

            level_completed = SceneManager.get_instance().scenes.get('level_completed')
            if level_completed:
                level_completed.set_current_level('level2')

        if self.showing_completion:
            self.transition_alpha += 5
            if self.transition_alpha >= 255:
                self._transition_to_scene('level_completed')

    def _transition_to_scene(self, scene_name):
        manager = SceneManager.get_instance()
        manager.last_scene_name = 'level2'

        if scene_name == 'game_over':
            game_over_scene = manager.scenes['game_over']
            game_over_scene.set_message(self.game_over_message)

        manager.set(scene_name)

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

        for monster in self.monsters:
            monster.draw(screen, camera_x)

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
            int(30 * self.scale_y))
        )

        bg_width = text_rect.width + int(40 * self.scale_factor)
        bg_height = text_rect.height + int(20 * self.scale_factor)
        bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
        bg_rect.center = (
            int(self.base_width // 2 * self.scale_x),
            int(30 * self.scale_y))

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