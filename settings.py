import os
WIDTH = 800
HEIGHT = 600

PURPLE_DARK = (43, 0, 69)
PURPLE_MID = (70, 0, 110)
PURPLE_LIGHT = (130, 50, 180)
PURPLE_NEON = (170, 0, 255)
PURPLE_BRIGHT = (200, 80, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FPS = 60
WINDOW_TITLE = "Sky Witch"
font_path = os.path.join('assets', 'fonts', 'Neoneon1.otf')
# Физика
GRAVITY = 0.8
MAX_FALL_SPEED = 15
PLAYER_SPEED = 5
JUMP_STRENGTH = 15
# Конфигурация уровня 1
LEVEL1_CONFIG = {
    'platform_positions': [
        (100, HEIGHT - 50), (300, HEIGHT - 100),
        (500, HEIGHT - 150), (700, HEIGHT - 200),
        (900, HEIGHT - 100), (1100, HEIGHT - 150),
        (1300, HEIGHT - 200), (1500, HEIGHT - 50)
    ],
    'star_indices': [1, 3, 5],
    'cloud_config': [
        {"type": "small", "count": 6, "y_range": (50, HEIGHT // 3)},
        {"type": "medium", "count": 4, "y_range": (HEIGHT // 3, HEIGHT // 2)},
        {"type": "big", "count": 3, "y_range": (HEIGHT // 2, HEIGHT * 2 // 3)}
    ],
    'player_start_pos': (100, HEIGHT - 200),
    'total_stars': 3,
    'background_color': PURPLE_DARK,
    'level_name': "Уровень 1",
    'level_color': (251, 255, 0),
    'ui_colors': {
        'bg': (180, 185, 0),
        'border': (130, 135, 0)
    }
}