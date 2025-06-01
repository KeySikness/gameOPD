import pygame
import sys
from scene_manager import SceneManager
from src.scenes.start_menu import StartMenu
from src.scenes.settings_scene import SettingsScene
from settings import *
import os
pygame.init()

screen_size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
pygame.display.set_caption("Sky Witch")

clock = pygame.time.Clock()
music_path = os.path.join('assets', 'audio', 'sound_for_menu.mp3')
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  
scene_manager = SceneManager.get_instance()

start_scene = StartMenu()
settings_scene = SettingsScene()

scene_manager.add('start', start_scene)
scene_manager.add('settings', settings_scene)


scene_manager = SceneManager.get_instance()
scene_manager.set('start')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            screen_size = event.size
            screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

        scene_manager.handle_event(event)

    scene_manager.update()

    if hasattr(scene_manager.current_scene, 'update_layout'):
        scene_manager.current_scene.update_layout(screen_size)

    scene_manager.render(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()