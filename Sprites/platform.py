import pygame
import os
from settings import *

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join('assets', 'image', 'result_platform_2.jpg')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (128, 37))
        except:
            self.image = pygame.Surface((128, 37))
            self.image.fill((100, 75, 150))
            pygame.draw.rect(self.image, (150, 100, 200), (0, 30, 128, 7))
        
        self.rect = self.image.get_rect(topleft=(x, y - 37))

class InfinitePlatform:
    def __init__(self, screen_height):
        self.screen_height = screen_height
        self.platform_height = 37
        self.segments = pygame.sprite.Group()
        self.segment_width = 128
        self.camera_offset = 0
        for i in range(-1, WIDTH // self.segment_width + 2):
            segment = Platform(i * self.segment_width, screen_height)
            self.segments.add(segment)
    
    def update(self, camera_offset):
        self.camera_offset = camera_offset
        first_segment = min(self.segments.sprites(), key=lambda s: s.rect.x)
        if first_segment.rect.x > 0:
            offset = first_segment.rect.x
            for segment in self.segments:
                segment.rect.x -= offset
        
        rightmost = max(s.rect.right for s in self.segments)
        while rightmost - camera_offset < WIDTH + self.segment_width * 2:
            new_segment = Platform(rightmost, self.screen_height)
            self.segments.add(new_segment)
            rightmost = new_segment.rect.right
        
        for segment in list(self.segments):
            if segment.rect.right - camera_offset < -self.segment_width * 2:
                segment.kill()
    
    def draw(self, screen):
        for segment in self.segments:
            screen.blit(segment.image, (segment.rect.x - self.camera_offset, segment.rect.y))