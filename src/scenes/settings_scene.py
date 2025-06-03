import pygame
import os
from settings import *

class Button:
    def __init__(self, text, x, y, width, height, font, bg_color, text_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.rendered_text = self.font.render(self.text, True, self.text_color)
        self.hovered = False
        self.border_color = WHITE
        self.border_width = 3

    def draw(self, surface):
        color = self.bg_color
        if self.hovered:
            color = tuple(min(c + 30, 255) for c in self.bg_color)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_rect = self.rendered_text.get_rect(center=self.rect.center)
        surface.blit(self.rendered_text, text_rect)
        if self.hovered:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, border_radius=10)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.is_hovered(mouse_pos)

def draw_arrow(surface, position, direction='left', size=20, color=WHITE):
    x, y = position
    if direction == 'left':
        points = [
            (x - size//2, y),
            (x + size//2, y - size//2),
            (x + size//2, y + size//2)
        ]
    else:
        points = [
            (x + size//2, y),
            (x - size//2, y - size//2),
            (x - size//2, y + size//2)
        ]
    pygame.draw.polygon(surface, color, points)

def point_in_triangle(pt, v1, v2, v3):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    b1 = sign(pt, v1, v2) < 0.0
    b2 = sign(pt, v2, v3) < 0.0
    b3 = sign(pt, v3, v1) < 0.0
    return ((b1 == b2) and (b2 == b3))

class SettingsScene:
    def __init__(self):
        self.base_width = WIDTH
        self.base_height = HEIGHT
        self.font_size = 30
        self.font = pygame.font.Font(font_path, self.font_size)
        self.bg_color = PURPLE_DARK
        self.slider_length = 200
        self.slider_height = 8
        self.slider_handle_radius = 12
        self.dragging = False
        self.slider_value = 50
        self.arrow_size = 20

        self.back_button = Button("Назад", 0, 0, 250, 60, self.font, PURPLE_MID, WHITE)
        self.language_options = ["Русский", "English"]
        self.current_language_index = 0

        self.update_layout((self.base_width, self.base_height))

    def update_language_text(self):
        self.lang_name_surface = self.font.render(
            self.language_options[self.current_language_index], 
            True, 
            WHITE
        )
        self.lang_name_rect = self.lang_name_surface.get_rect(center=self.lang_center)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.update_layout(event.size)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            self.back_button.hovered = self.back_button.is_hovered(mouse_pos)

            if self.back_button.check_click(mouse_pos):
                from scene_manager import SceneManager
                scene_manager = SceneManager.get_instance()
                scene_manager.set('start')

            if point_in_triangle(mouse_pos, *self.left_triangle_points):
                self.current_language_index = (self.current_language_index - 1) % len(self.language_options)
                self.update_language_text()
                return
            
            elif point_in_triangle(mouse_pos, *self.right_triangle_points):
                self.current_language_index = (self.current_language_index + 1) % len(self.language_options)
                self.update_language_text()
                return

            if self.slider_handle_rect.collidepoint(mouse_pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.back_button.hovered = self.back_button.is_hovered(mouse_pos)
            if self.dragging:
                mouse_x = mouse_pos[0]
                new_x = max(self.slider_rect.left, min(self.slider_rect.right, mouse_x))
                self.slider_handle_rect.centerx = new_x
                self.slider_value = ((new_x - self.slider_rect.left) / self.slider_length) * 100
                pygame.mixer.music.set_volume(self.slider_value / 100)

    def update(self):
        pass

    def update_layout(self, window_size):
        width, height = window_size
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.scale_factor = min(self.scale_x, self.scale_y)

        self.font_title = pygame.font.Font(font_path, int(50 * self.scale_factor))
        self.font = pygame.font.Font(font_path, int(self.font_size * self.scale_factor))

        self.title_surface = self.font_title.render("Настройки", True, WHITE)
        self.title_rect = self.title_surface.get_rect(center=(width // 2, int(50 * self.scale_y)))

        self.volume_label_surface = self.font.render("Громкость", True, WHITE)
        self.volume_label_rect = self.volume_label_surface.get_rect(
            topleft=(int(133 * self.scale_x), int(150 * self.scale_y))
        )

        self.slider_length_scaled = int(self.slider_length * self.scale_factor)
        self.slider_rect = pygame.Rect(0, 0, self.slider_length_scaled, int(8 * self.scale_factor))
        self.slider_rect.center = (width // 2, int(170 * self.scale_y))

        self.slider_handle_radius_scaled = int(self.slider_handle_radius * self.scale_factor)
        handle_x = self.slider_rect.left + (self.slider_value / 100) * self.slider_length_scaled
        self.slider_handle_rect = pygame.Rect(
            handle_x - self.slider_handle_radius_scaled,
            self.slider_rect.centery - self.slider_handle_radius_scaled,
            self.slider_handle_radius_scaled * 2,
            self.slider_handle_radius_scaled * 2
        )

        self.lang_label_surface = self.font.render("Язык:", True, WHITE)
        self.lang_label_rect = self.lang_label_surface.get_rect(
            topleft=(int(133 * self.scale_x), int(210 * self.scale_y))
        )

        lang_text_width = max(self.font.size(option)[0] for option in self.language_options)
        total_width = lang_text_width + int(self.arrow_size * self.scale_factor) * 2 + int(40 * self.scale_factor)
        
        left_arrow_x = width // 2 - total_width // 2
        right_arrow_x = width // 2 + total_width // 2 - int(self.arrow_size * self.scale_factor)
        
        arrow_y = int(222 * self.scale_y)
        self.arrow_size_scaled = int(self.arrow_size * self.scale_factor)
        
        self.left_arrow_center = (left_arrow_x, arrow_y)
        self.right_arrow_center = (right_arrow_x, arrow_y)
        self.lang_center = (width // 2, arrow_y)
        
        self.update_language_text()

        self.left_triangle_points = [
            (self.left_arrow_center[0] - self.arrow_size_scaled//2, self.left_arrow_center[1]),
            (self.left_arrow_center[0] + self.arrow_size_scaled//2, self.left_arrow_center[1] - self.arrow_size_scaled//2),
            (self.left_arrow_center[0] + self.arrow_size_scaled//2, self.left_arrow_center[1] + self.arrow_size_scaled//2)
        ]
        self.right_triangle_points = [
            (self.right_arrow_center[0] + self.arrow_size_scaled//2, self.right_arrow_center[1]),
            (self.right_arrow_center[0] - self.arrow_size_scaled//2, self.right_arrow_center[1] - self.arrow_size_scaled//2),
            (self.right_arrow_center[0] - self.arrow_size_scaled//2, self.right_arrow_center[1] + self.arrow_size_scaled//2)
        ]

        self.back_button.rect.width = int(250 * self.scale_factor)
        self.back_button.rect.height = int(60 * self.scale_factor)
        self.back_button.rect.centerx = width // 2
        self.back_button.rect.top = height - int(100 * self.scale_y)
        self.back_button.font = pygame.font.Font(font_path, int(30 * self.scale_factor))
        self.back_button.rendered_text = self.back_button.font.render(
            self.back_button.text, True, self.back_button.text_color)

    def render(self, surface):
        surface.fill(self.bg_color)
        surface.blit(self.title_surface, self.title_rect)
        
        surface.blit(self.volume_label_surface, self.volume_label_rect)
        pygame.draw.rect(surface, WHITE, self.slider_rect, border_radius=int(4 * self.scale_factor))
        pygame.draw.rect(surface, PURPLE_DARK, self.slider_rect, width=int(2 * self.scale_factor), border_radius=int(4 * self.scale_factor))
        pygame.draw.circle(surface, WHITE, self.slider_handle_rect.center, self.slider_handle_radius_scaled)
        
        volume_text = self.font.render(f"{int(self.slider_value)}", True, WHITE)
        volume_rect = volume_text.get_rect(midleft=(self.slider_rect.right + int(10 * self.scale_factor), self.slider_rect.centery))
        surface.blit(volume_text, volume_rect)
        
        surface.blit(self.lang_label_surface, self.lang_label_rect)
        draw_arrow(surface, self.left_arrow_center, 'left', size=self.arrow_size_scaled, color=WHITE)
        draw_arrow(surface, self.right_arrow_center, 'right', size=self.arrow_size_scaled, color=WHITE)
        surface.blit(self.lang_name_surface, self.lang_name_rect)
        
        self.back_button.draw(surface)