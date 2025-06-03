import pygame
from settings import *
from src.scenes.start_menu import Button 

class LevelCompleted:
    def __init__(self):
        self.base_width = WIDTH
        self.base_height = HEIGHT
        self.scale_factor = 1
        self.scale_x = 1
        self.scale_y = 1
        
        self.font_large = None
        self.font_small = None
        self.menu_button = None
        self.next_button = None
        self.retry_button = None
        
        self.alpha = 0
        self.fade_speed = 5
        self.fade_in_complete = False
        self.transition_surface = None
        
        self.current_window_size = (WIDTH, HEIGHT)
        self.fullscreen_content = None
        self.update_layout((WIDTH, HEIGHT))

    def update_layout(self, window_size):
        self.current_window_size = window_size
        width, height = window_size
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        self.font_large = pygame.font.Font(font_path, int(72 * self.scale_factor))
        self.font_small = pygame.font.Font(font_path, int(36 * self.scale_factor))
        
        button_width = int(200 * self.scale_factor)
        button_height = int(50 * self.scale_factor)
        button_spacing = int(20 * self.scale_factor)
        
        # Центральная позиция для группы кнопок
        buttons_start_x = width // 2 - (button_width * 3 + button_spacing * 2) // 2
        
        self.menu_button = Button(
            "В меню",
            buttons_start_x,
            int(height // 2 + 50 * self.scale_y),
            button_width,
            button_height,
            pygame.font.Font(font_path, int(30 * self.scale_factor)),
            PURPLE_MID,
            WHITE
        )
        
        self.next_button = Button(
            "Далее",
            buttons_start_x + button_width + button_spacing,
            int(height // 2 + 50 * self.scale_y),
            button_width,
            button_height,
            pygame.font.Font(font_path, int(30 * self.scale_factor)),
            PURPLE_MID,
            WHITE
        )
        
        self.retry_button = Button(
            "Еще раз",
            buttons_start_x + (button_width + button_spacing) * 2,
            int(height // 2 + 50 * self.scale_y),
            button_width,
            button_height,
            pygame.font.Font(font_path, int(30 * self.scale_factor)),
            PURPLE_MID,
            WHITE
        )
        
        self.fullscreen_content = pygame.Surface((width, height))
        self.transition_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
            
        if event.type == pygame.MOUSEBUTTONDOWN and self.fade_in_complete:
            mouse_pos = pygame.mouse.get_pos()
            if self.menu_button.check_click(mouse_pos):
                from scene_manager import SceneManager
                SceneManager.get_instance().set('start')
            elif self.next_button.check_click(mouse_pos):
                # Заглушка вместо перехода на следующий уровень
                print("Кнопка 'Далее' нажата. Здесь будет переход на следующий уровень.")
                # В будущем можно раскомментировать:
                # from scene_manager import SceneManager
                # SceneManager.get_instance().set('level2')
            elif self.retry_button.check_click(mouse_pos):
                from scene_manager import SceneManager
                level = SceneManager.get_instance().scenes['level1']
                level.reset()
                SceneManager.get_instance().set('level1')

    def update(self):
        if not self.fade_in_complete:
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fade_in_complete = True
        
        mouse_pos = pygame.mouse.get_pos()
        if self.fade_in_complete:
            self.menu_button.hovered = self.menu_button.is_hovered(mouse_pos)
            self.next_button.hovered = self.next_button.is_hovered(mouse_pos)
            self.retry_button.hovered = self.retry_button.is_hovered(mouse_pos)

    def render(self, screen):
        current_width, current_height = self.current_window_size
        
        self.fullscreen_content.fill(PURPLE_DARK)
        
        text = self.font_large.render("УРОВЕНЬ ПРОЙДЕН", True, WHITE)
        text_rect = text.get_rect(
            center=(
                current_width // 2,
                current_height // 2 - 100 * self.scale_y
            )
        )
        self.fullscreen_content.blit(text, text_rect)
        
        if self.fade_in_complete:
            self.menu_button.draw(self.fullscreen_content)
            self.next_button.draw(self.fullscreen_content)
            self.retry_button.draw(self.fullscreen_content)
        
        self.transition_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.transition_surface, (0, 0, 0, 255 - self.alpha), 
                        (0, 0, current_width, current_height))
        
        screen.blit(self.fullscreen_content, (0, 0))
        screen.blit(self.transition_surface, (0, 0))