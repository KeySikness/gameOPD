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
    
    def update(self, all_clouds):
        self.rect.x -= self.speed
        
        if self.rect.right < 0:
            safe_position_found = False
            attempts = 0
            max_attempts = 10
            
            while not safe_position_found and attempts < max_attempts:
                attempts += 1
                new_x = WIDTH + random.randint(0, WIDTH)
                new_y = random.randint(*self.y_range)
                
                too_close = False
                for cloud in all_clouds:
                    if cloud != self and cloud.type == self.type:
                        distance = abs(new_x - cloud.rect.x)
                        if distance < self.min_distance:
                            too_close = True
                            break
                
                if not too_close:
                    safe_position_found = True
                    self.rect.left = new_x
                    self.rect.y = new_y
                    speed_variation = random.uniform(-0.2, 0.2)
                    self.speed = max(0.3, min(self.speed + speed_variation, 2.5))
            
            if not safe_position_found:
                self.rect.left = WIDTH + random.randint(0, WIDTH)
                self.rect.y = random.randint(*self.y_range)