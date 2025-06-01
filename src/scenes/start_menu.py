import pygame
import os
from scene_manager import *
from settings import * 
import sys

class Button:
    def __init__(self, text, x, y, width, height, font, bg_color, text_color, scale_factor=1.0):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.rendered_text = self.font.render(self.text, True, self.text_color)
        self.hovered = False
        self.border_color = WHITE
        self.border_width = 3
        self.scale_factor = scale_factor  # Добавляем scale_factor как атрибут

    def draw(self, surface):
        color = self.bg_color
        if self.hovered:
            color = tuple(min(c + 30, 255) for c in self.bg_color)
        pygame.draw.rect(surface, color, self.rect, border_radius=int(10 * self.scale_factor))
        text_rect = self.rendered_text.get_rect(center=self.rect.center)
        surface.blit(self.rendered_text, text_rect)
        
        if self.hovered:
            pygame.draw.rect(surface, self.border_color, self.rect, int(self.border_width * self.scale_factor), border_radius=int(10 * self.scale_factor))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.is_hovered(mouse_pos)

class StartMenu:
    def __init__(self):
        self.base_width = WIDTH
        self.base_height = HEIGHT
        
        # Базовые размеры шрифтов
        self.base_title_font_size = 80
        self.base_menu_font_size = 40
        
        # Инициализация шрифтов с базовыми размерами
        self.title_font = pygame.font.Font(font_path, self.base_title_font_size)
        self.menu_font = pygame.font.Font(font_path, self.base_menu_font_size)
        
        # Масштабируемые атрибуты
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_factor = 1.0
        
        self.title_text = self.title_font.render("Sky Witch", True, PURPLE_NEON)
        self.title_rect = self.title_text.get_rect(center=(self.base_width // 2, self.base_height // 4))
        self.buttons = []
        
        self._create_buttons()
        self.update_layout((self.base_width, self.base_height))

    def _create_buttons(self):
        button_width = 250
        button_height = 60
        self.buttons.clear()
        for text in ["Старт", "Настройки", "Выход"]:
            button = Button(
                text,
                0,
                0,
                button_width,
                button_height,
                self.menu_font,
                PURPLE_MID,
                WHITE,
                self.scale_factor  # Передаем текущий scale_factor
            )
            self.buttons.append(button)

    def update_layout(self, window_size):
        width, height = window_size
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        # Масштабирование шрифтов
        self.title_font = pygame.font.Font(font_path, int(self.base_title_font_size * self.scale_factor))
        self.menu_font = pygame.font.Font(font_path, int(self.base_menu_font_size * self.scale_factor))
        
        # Обновление заголовка
        self.title_text = self.title_font.render("Sky Witch", True, PURPLE_NEON)
        self.title_rect = self.title_text.get_rect(center=(width // 2, int(height // 4)))
        
        # Масштабирование кнопок
        start_y = height // 2
        spacing = int(20 * self.scale_factor)
        
        for idx, btn in enumerate(self.buttons):
            btn.scale_factor = self.scale_factor  # Обновляем scale_factor для каждой кнопки
            btn.rect.width = int(250 * self.scale_factor)
            btn.rect.height = int(60 * self.scale_factor)
            btn.rect.center = (width // 2, start_y + idx * (btn.rect.height + spacing))
            
            # Обновление шрифта и текста кнопки
            btn.font = self.menu_font
            btn.rendered_text = btn.font.render(btn.text, True, btn.text_color)
            btn.border_width = int(3 * self.scale_factor)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                if btn.check_click(mouse_pos):
                    if btn.text == "Старт":
                        scene_manager = SceneManager.get_instance()
                        scene_manager.set('level1')
                    elif btn.text == "Настройки":
                        scene_manager = SceneManager.get_instance()
                        scene_manager.set('settings')
                    elif btn.text == "Выход":
                        pygame.quit()
                        sys.exit()

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.hovered = btn.is_hovered(mouse_pos)

    def render(self, screen):
        screen.fill(PURPLE_DARK)
        screen.blit(self.title_text, self.title_rect)
        for btn in self.buttons:
            btn.draw(screen)