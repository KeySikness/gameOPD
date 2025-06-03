import pygame
import os
import random
from settings import WIDTH, HEIGHT

class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, cloud_type):
        super().__init__()
        self.type = cloud_type
        self.images = self.load_images()
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        if self.type == "small":
            self.speed = random.uniform(0.5, 1.0)
            self.y_range = (50, HEIGHT//3)
            self.min_distance = 300
        elif self.type == "medium":
            self.speed = random.uniform(1.0, 1.5)
            self.y_range = (HEIGHT//3, HEIGHT//2)
            self.min_distance = 400
        else:  # big
            self.speed = random.uniform(1.5, 2.0)
            self.y_range = (HEIGHT//2, HEIGHT*2//3)
            self.min_distance = 500
    
    def load_images(self):
        loaded_images = []
        base_path = os.path.join('assets', 'image', 'clouds')
        
        if self.type == "small":
            filenames = ["cloud_small_1.png", "cloud_small_2.png"]
            default_size = (100, 50)
        elif self.type == "medium":
            filenames = ["cloud_medium_1.png", "cloud_medium_2.png"]
            default_size = (200, 100)
        else:  # big
            filenames = ["cloud_big_1.png", "cloud_big_2.png"]
            default_size = (300, 150)
        
        for filename in filenames:
            try:
                img_path = os.path.join(base_path, filename)
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, default_size)
                loaded_images.append(img)
            except:
                continue
        
        if not loaded_images:
            surf = pygame.Surface(default_size, pygame.SRCALPHA)
            color = (255, 255, 255, 180)
            pygame.draw.ellipse(surf, color, (0, 0, *default_size))
            loaded_images.append(surf)
        
        return loaded_images
    
    def update(self, cloud_group):
        # Движение облака влево
        self.rect.x -= self.speed
        
        # Если облако вышло за левую границу экрана
        if self.rect.right < 0:
            # Перемещаем его вправо за экран
            self.rect.x = random.randint(800, 1200)
            self.rect.y = random.randint(50, 300)
            
            # Проверяем, чтобы новое положение не пересекалось с другими облаками
            while any(abs(self.rect.x - cloud.rect.x) < self.min_distance and 
                     abs(self.rect.y - cloud.rect.y) < 100 for cloud in cloud_group if cloud != self):
                self.rect.x = random.randint(800, 1200)
                self.rect.y = random.randint(50, 300)