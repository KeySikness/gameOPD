import pygame
import sys
from scene_manager import SceneManager
from src.scenes.start_menu import StartMenu
from src.scenes.settings_scene import SettingsScene
from src.scenes.level_1 import Level1
from settings import *
from src.scenes.level_completed import LevelCompleted
from src.scenes.game_over import GameOver
import os

def main():
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

    # Создаем и добавляем все сцены
    scene_manager.add('start', StartMenu())
    scene_manager.add('settings', SettingsScene())
    scene_manager.add('level1', Level1())
    scene_manager.add('level_completed', LevelCompleted())
    scene_manager.add('game_over', GameOver())

    # Устанавливаем начальную сцену
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
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()