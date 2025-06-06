import pygame
import random
from settings import *
from scene_manager import SceneManager
from src.scenes.start_menu import Button
from Sprites import Platform, Player, Star
from Sprites.clouds import Cloud
from Sprites.monsters import Monster
from Sprites.boss import Boss

class Level3:
    def __init__(self):
        self.config = {
            'background_color': PURPLE_DARK,
            'level_name': "Уровень 3",
            'level_color': PURPLE_NEON,
            'ui_colors': {
                'bg': PURPLE_MID,
                'border': PURPLE_LIGHT
            },
            'player_start_pos': (100, HEIGHT - 150),
            'platform_positions': self._generate_platforms(),
            'star_indices': [3, 6, 9],  # Индексы платформ, на которых будут звезды
            'cloud_config': [
                {"type": "small", "count": 8, "y_range": (50, HEIGHT // 3)},
                {"type": "medium", "count": 5, "y_range": (HEIGHT // 3, HEIGHT // 2)},
                {"type": "big", "count": 4, "y_range": (HEIGHT // 2, HEIGHT * 2 // 3)}
            ],
            'total_stars': 3  # Всего нужно собрать 3 звезды
        }

        self._init_base_variables()
        self.reset()

    def _generate_platforms(self):
        platform_width = 100
        platform_height = 20
        platform_count = (WIDTH // platform_width) + 15  # Больше платформ, если игрок идет вправо

        y = HEIGHT - platform_height
        platforms = [(i * platform_width, y) for i in range(platform_count)]
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
        self.game_objects.add(self.player)
        
        # Создание босса на последней платформе
        platforms_sorted = sorted(self.all_platforms.sprites(), key=lambda p: p.rect.x)
        if platforms_sorted:
            last_platform = platforms_sorted[10]
            self.boss = Boss(
                last_platform.rect.centerx - 50,
                last_platform.rect.top - 100,
                self.all_platforms
            )
            self.boss.rect.bottom = last_platform.rect.top
            self.game_objects.add(self.boss)

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
            self.config['ui_colors']['bg'],
            WHITE,
            self.scale_factor
        )
        self.back_button.border_color = WHITE
        self.back_button.border_width = 3

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
        self.back_button.rendered_text = self.back_button.font.render(self.back_button.text, True, self.back_button.text_color)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.check_click(pygame.mouse.get_pos()):
                SceneManager.get_instance().set('start')

    def update(self):
        self._update_button_state()
        self._check_boss_collision()
        self._check_game_over()
        
        if not self.game_over:
            self._update_game_objects()
            self._check_level_completion()
            

        if hasattr(self, 'boss'):
            self.boss.platform_group = self.all_platforms
            self.boss.update(self.player)

            
        self.monsters.update()
        # Снимаем временную неуязвимость после 1 секунды
        if getattr(self, 'temporary_invincible', False):
            if pygame.time.get_ticks() - self.invincibility_timer > 1000:
                self.temporary_invincible = False


    def _check_boss_collision(self):
        if hasattr(self, 'boss') and self.player.rect.colliderect(self.boss.rect):
            if (self.player.rect.bottom < self.boss.rect.top + 20 and 
                self.player.velocity_y > 0 and 
                not getattr(self.player, 'just_attacked_boss', False)):  # Атака сверху
                self.boss.take_damage(1)

                boss_x = self.boss.rect.centerx
                boss_y = self.boss.rect.bottom

                left_platform = None
                right_platform = None
                min_left_dist = float('inf')
                min_right_dist = float('inf')

                for platform in self.all_platforms:
                    dy = abs(platform.rect.top - boss_y)
                    if dy < 50:  # Примерно тот же уровень
                        dx = platform.rect.centerx - boss_x
                        if dx < 0 and abs(dx) < min_left_dist:
                            min_left_dist = abs(dx)
                            left_platform = platform
                        elif dx > 0 and dx < min_right_dist:
                            min_right_dist = dx
                            right_platform = platform

                # Отскок от босса
                self.player.velocity_y = -12

                if self.player.rect.centerx < boss_x and left_platform:
                    self.player.velocity_x = -7
                elif self.player.rect.centerx >= boss_x and right_platform:
                    self.player.velocity_x = 7
                else:
                    self.player.velocity_x = -6 if self.player.rect.centerx < boss_x else 6

                # Убираем возможность сразу снова столкнуться
                self.player.rect.bottom = self.boss.rect.top - 10

                # Временная неуязвимость и блокировка повторной атаки
                self.temporary_invincible = True
                self.invincibility_timer = pygame.time.get_ticks()
                self.player.just_attacked_boss = True  # ❗ Блок повторной атаки

                if self.boss.hp <= 0:
                    del self.boss
            else:
                # Боковое столкновение
                if not getattr(self, 'temporary_invincible', False):
                    self.game_over = True
                    self.game_over_message = "Уровень не пройден"

    def _update_button_state(self):
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.hovered = self.back_button.is_hovered(mouse_pos)

    def _check_game_over(self):
        if self.player.rect.top > HEIGHT and not self.game_over:
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
        self.player.update(self.all_platforms)  # Передаём сразу все платформы
        # Сброс флага, если игрок встал на платформу (значит, снова можно атаковать)
        if self.player.on_ground:
            self.player.just_attacked_boss = False


        self._check_star_collisions()

    def _check_star_collisions(self):
        for star in self.stars:
            if self.player.rect.colliderect(star.rect) and star.collect():
                self.stars_collected += 1

    def _check_level_completion(self):
        if self.stars_collected >= self.config['total_stars'] and not self.showing_completion:
            # Проверяем, есть ли еще босс (если нет - уровень пройден)
            if not hasattr(self, 'boss'):
                self.showing_completion = True
                self.transition_alpha = 0
                self.game_over_message = "Уровень пройден!"
                       
                # Устанавливаем текущий уровень
                level_completed_scene = SceneManager.get_instance().scenes['level_completed']
                level_completed_scene.set_current_level('level3')  # <--- ВАЖНО!

                # Переход на сцену завершения
                SceneManager.get_instance().set('level_completed')

    def _transition_to_scene(self, scene_name):
        if scene_name == 'game_over':
            game_over_scene = SceneManager.get_instance().scenes['game_over']
            game_over_scene.set_message(self.game_over_message)
        elif scene_name == 'level_completed':
            SceneManager.get_instance().set_last_completed_level("level3")  # 💾 Сохраняем
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
        
        for platform in self.all_platforms:
            self._render_sprite(screen, platform.image, platform.rect, camera_x)

        
        for star in self.stars:
            self._render_sprite(screen, star.image, star.rect, camera_x)
        
        for monster in self.monsters:
            monster.draw(screen, camera_x)
        
        player_img = (self.player.original_image_right if self.player.facing_right 
                    else self.player.original_image_left)
        self._render_player(screen, player_img)
        
        if hasattr(self, 'boss'):
            self._render_sprite(screen, self.boss.image, self.boss.rect, camera_x)
            self.boss.draw(screen, camera_x)

    def _render_sprite(self, screen, image, rect, camera_x=0):
        x = int((rect.x - camera_x) * self.scale_x)
        y = int(rect.y * self.scale_y)
        scaled_size = (
            int(rect.width * self.scale_factor),
            int(rect.height * self.scale_factor)
        )
        scaled_img = pygame.transform.scale(image, scaled_size)
        screen.blit(scaled_img, (x, y))

    def _render_player(self, screen, image):
        x = int((self.base_width // 2 - self.player.rect.width // 2) * self.scale_x)
        y = int(self.player.rect.y * self.scale_y)
        scaled_size = (
            int(self.player.rect.width * self.scale_x),
            int(self.player.rect.height * self.scale_y)
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