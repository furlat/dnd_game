import pygame
import pygame_gui
from pygame.locals import *
import os

from neurodragon.ui.battlemap_window import create_battlemap_window, create_details_window
from neurodragon.ui.music import create_music_manager
from neurodragon.ui.active_entity_window import ActiveEntityWindow
from neurodragon.ui.target_window import TargetWindow


def resize_image(original_path, resized_path, size):
    if not os.path.exists(resized_path):
        original_image = pygame.image.load(original_path)
        resized_image = pygame.transform.scale(original_image, size)
        pygame.image.save(resized_image, resized_path)

def ensure_resized_images():
    base_path = 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites'
    image_files = {
        'toggle_fov.png': (50, 50),
        'color_fov.png': (50, 50),
        'ray_to_target.png': (50, 50),
        'toggle_paths.png': (50, 50),
        'path_to_target.png': (50, 50)
    }

    for image_name, size in image_files.items():
        original_path = os.path.join(base_path, image_name)
        resized_path = os.path.join(base_path, f'resized_{size[0]}x{size[1]}_{image_name}')
        resize_image(original_path, resized_path, size)

ensure_resized_images()

pygame.init()
width = 800
height = 600
factor = 1.7
width *= factor
height *= factor

window_surface = pygame.display.set_mode((int(width), int(height)))
pygame.display.set_caption('NeuroDragonV0')

background_path = os.path.join('assets', 'backgrounds', 'glitched_neurodragon.png')
background = pygame.image.load(background_path)

theme_path = os.path.join('assets', 'themes', 'theme.json')
manager = pygame_gui.UIManager((int(width), int(height)), theme_path)

clock = pygame.time.Clock()
is_running = True

# Create the details window
details_window = create_details_window(manager)

# Create the music manager
music_manager = create_music_manager(manager, width, height)

# Create the active entity window
active_entity_window_rect = pygame.Rect(0, int(height) - 150, 300, 150)
active_entity_window = ActiveEntityWindow(active_entity_window_rect, manager)

# Create the target window
target_window_rect = pygame.Rect(int(width) - 310, int(height) - 150, 300, 150)
target_window = TargetWindow(target_window_rect, manager)

# Create the battlemap window
battlemap_window = create_battlemap_window(manager, details_window, active_entity_window, target_window)

while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False

        manager.process_events(event)
        battlemap_window.process_event(event)
        music_manager.handle_event(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()
