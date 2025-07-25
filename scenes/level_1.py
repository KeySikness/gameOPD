import pygame
import random
from settings import *
from scene_manager import SceneManager
from src.scenes.start_menu import Button
from Sprites import InfinitePlatform, Cloud, Player

class Level1:
    def __init__(self):
        self.base_width = WIDTH
        self.base_height = HEIGHT

        self.platform = InfinitePlatform(HEIGHT)

        self.player = Player(100, HEIGHT - 200)

        self.back_button = self.create_back_button()
        self.font = pygame.font.Font(font_path, 24)

        self.level_font = pygame.font.Font(font_path, 36)

        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.fill(PURPLE_DARK)
        self.camera_offset = 0

        self.clouds = pygame.sprite.Group()
        self.init_clouds()

    def init_clouds(self):
        cloud_config = [
            {"type": "small", "count": 6},
            {"type": "medium", "count": 4},
            {"type": "big", "count": 3}
        ]
        
        for config in cloud_config:
            for i in range(config["count"]):
                x = WIDTH * (i / config["count"]) + random.randint(-200, 200)
                y = 0
                new_cloud = Cloud(x, y, config["type"])
                
                too_close = any(
                    abs(new_cloud.rect.x - cloud.rect.x) < new_cloud.min_distance and
                    cloud.type == new_cloud.type
                    for cloud in self.clouds
                )
                
                if not too_close:
                    self.clouds.add(new_cloud)
                else:
                    new_cloud.rect.x += new_cloud.min_distance
                    self.clouds.add(new_cloud)

    def create_back_button(self):
        return Button(
            "Назад", 
            WIDTH - 170, 20, 
            150, 50,
            pygame.font.Font(font_path, 30),
            PURPLE_MID,
            WHITE
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.check_click(pygame.mouse.get_pos()):
                SceneManager.get_instance().set('start')

    def update(self):
        if self.player.facing_right and self.player.rect.x > WIDTH // 3:
            self.camera_offset = self.player.rect.x - WIDTH // 3
        else:
            self.camera_offset = max(0, self.player.rect.x - WIDTH // 3)

        self.player.handle_input()
        self.player.update(self.platform.segments)

        self.platform.update(self.camera_offset)

        for cloud in self.clouds:
            cloud.update(self.clouds)

        mouse_pos = pygame.mouse.get_pos()
        self.back_button.hovered = self.back_button.is_hovered(mouse_pos)

    def render(self, screen):
        screen.blit(self.background, (0, 0))

        self.clouds.draw(screen)

        self.platform.draw(screen)

        self.player.draw(screen, self.camera_offset)

        self.back_button.draw(screen)

        level_text = self.level_font.render("Уровень 1", True, (251, 255, 0))
        text_rect = level_text.get_rect(center=(WIDTH // 2, 30))

        bg_color = (180, 185, 0)
        border_color = (130, 135, 0)

        bg_width = text_rect.width + 40
        bg_height = text_rect.height + 20
        bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
        bg_rect.center = (WIDTH // 2, 30)

        pygame.draw.rect(screen, bg_color, bg_rect, border_radius=12)
        pygame.draw.rect(screen, border_color, bg_rect, border_radius=12, width=2)

        screen.blit(level_text, text_rect)