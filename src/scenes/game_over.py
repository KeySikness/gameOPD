import pygame
from settings import *
from src.scenes.start_menu import Button
from scene_manager import *

class GameOver:
    def __init__(self):
        self.base_width = WIDTH
        self.base_height = HEIGHT
        self.scale_factor = 1
        self.scale_x = 1
        self.scale_y = 1
        
        self.font_large = None
        self.font_small = None
        self.menu_button = None  
        self.retry_button = None
        
        self.alpha = 0
        self.fade_speed = 5
        self.fade_in_complete = False
        self.transition_surface = None
        
        self.current_window_size = (WIDTH, HEIGHT)
        self.fullscreen_content = None
        self.message = "ИГРА ОКОНЧЕНА"
        self.message_color = WHITE
        self._init_buttons()
        self.update_layout((WIDTH, HEIGHT))

    def _init_buttons(self):
        button_width = int(250 * self.scale_factor)
        button_height = int(60 * self.scale_factor)
        
        self.menu_button = Button(
            "В меню",
            0, 0,  
            button_width,
            button_height,
            pygame.font.Font(font_path, int(30 * self.scale_factor)),
            PURPLE_MID,
            WHITE,
            self.scale_factor
        )
        self.menu_button.border_color = WHITE
        self.menu_button.border_width = int(3 * self.scale_factor)
        
        self.retry_button = Button(
            "Еще раз",
            0, 0, 
            button_width,
            button_height,
            pygame.font.Font(font_path, int(30 * self.scale_factor)),
            PURPLE_MID,
            WHITE,
            self.scale_factor
        )
        self.retry_button.border_color = WHITE
        self.retry_button.border_width = int(3 * self.scale_factor)

    def update_layout(self, window_size):
        self.current_window_size = window_size
        width, height = window_size
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        self.font_large = pygame.font.Font(font_path, int(72 * self.scale_factor))
        self.font_small = pygame.font.Font(font_path, int(36 * self.scale_factor))
        
        button_width = int(250 * self.scale_factor)
        button_height = int(60 * self.scale_factor)
        
        if self.menu_button:
            self.menu_button.rect.width = button_width
            self.menu_button.rect.height = button_height
            self.menu_button.rect.center = (
                width // 2,
                height // 2 + 50 * self.scale_y
            )
            self.menu_button.font = pygame.font.Font(font_path, int(30 * self.scale_factor))
            self.menu_button.rendered_text = self.menu_button.font.render(
                self.menu_button.text, True, self.menu_button.text_color)
            self.menu_button.scale_factor = self.scale_factor
            self.menu_button.border_width = int(3 * self.scale_factor)
        
        if self.retry_button:
            self.retry_button.rect.width = button_width
            self.retry_button.rect.height = button_height
            self.retry_button.rect.center = (
                width // 2,
                height // 2 + 120 * self.scale_y
            )
            self.retry_button.font = pygame.font.Font(font_path, int(30 * self.scale_factor))
            self.retry_button.rendered_text = self.retry_button.font.render(
                self.retry_button.text, True, self.retry_button.text_color)
            self.retry_button.scale_factor = self.scale_factor
            self.retry_button.border_width = int(3 * self.scale_factor)
        
        self.fullscreen_content = pygame.Surface((width, height))
        self.transition_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def set_message(self, message, color=None):
        self.message = message
        if color:
            self.message_color = color

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
            
        if event.type == pygame.MOUSEBUTTONDOWN and self.fade_in_complete:
            mouse_pos = pygame.mouse.get_pos()
            if self.menu_button and self.menu_button.check_click(mouse_pos):
                SceneManager.get_instance().set('start')
            elif self.retry_button and self.retry_button.check_click(mouse_pos):
                manager = SceneManager.get_instance()
                failed_level = manager.last_scene_name
                if failed_level and failed_level in manager.scenes:
                    level = manager.scenes[failed_level]
                    if hasattr(level, 'reset'):
                        level.reset()
                    manager.set(failed_level)


    def update(self):
        if not self.fade_in_complete:
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fade_in_complete = True
        
        mouse_pos = pygame.mouse.get_pos()
        if self.fade_in_complete:
            if self.menu_button:
                self.menu_button.hovered = self.menu_button.is_hovered(mouse_pos)
            if self.retry_button:
                self.retry_button.hovered = self.retry_button.is_hovered(mouse_pos)

    def render(self, screen):
        current_width, current_height = self.current_window_size
        
        self.fullscreen_content.fill(PURPLE_DARK)
        
        text = self.font_large.render(self.message, True, self.message_color)
        text_rect = text.get_rect(
            center=(
                current_width // 2,
                current_height // 2 - 100 * self.scale_y
            )
        )
        self.fullscreen_content.blit(text, text_rect)
        
        if self.fade_in_complete:
            if self.menu_button:
                self.menu_button.draw(self.fullscreen_content)
            if self.retry_button:
                self.retry_button.draw(self.fullscreen_content)
        
        self.transition_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.transition_surface, (0, 0, 0, 255 - self.alpha), 
                        (0, 0, current_width, current_height))
        
        screen.blit(self.fullscreen_content, (0, 0))
        screen.blit(self.transition_surface, (0, 0))