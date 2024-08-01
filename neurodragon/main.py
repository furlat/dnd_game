import pygame
import pygame_gui
from pygame.locals import *
import os

from neurodragon.ui.battlemap_window import create_battlemap_window, create_details_window, SPRITE_PATHS
from neurodragon.ui.music import create_music_manager
from neurodragon.ui.active_entity_window import ActiveEntityWindow
from neurodragon.ui.target_window import TargetWindow
from neurodragon.ui.actions_window import create_actions_window, ACTION_COMPLETED


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
width = 1000
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
# Create the actions window
actions_window = create_actions_window(manager, width, height)
while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False
        elif event.type == ACTION_COMPLETED:
            print("Action completed event received in main loop")
            # Update all relevant windows
            battlemap_window.render_battlemap()
            if battlemap_window.selected_entity:
                position = battlemap_window.selected_entity.position
                tile_type = battlemap_window.battle_map.get_tile(*position)
                entity_name = battlemap_window.selected_entity.name
                sprite_path = SPRITE_PATHS.get(entity_name)
                details_window.update_details(position, tile_type, entity_name, sprite_path)
            else:
                details_window.clear_details()
            active_entity_window.update_details(battlemap_window.selected_entity)
            target_window.update_details(battlemap_window.target_window.target_entity)
            actions_window.handle_action_completed()  # Add this line
        else:
            battlemap_window._process_event(event)
            music_manager.handle_event(event)
            actions_window._process_event(event)
            manager.process_events(event)
            

    manager.update(time_delta)

    # Update actions window if active entity or target has changed
    if (actions_window.active_entity != battlemap_window.selected_entity or
        actions_window.target_entity != battlemap_window.target_window.target_entity):
        actions_window.update_actions(battlemap_window.selected_entity, battlemap_window.target_window.target_entity)



    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()
pygame.quit()
