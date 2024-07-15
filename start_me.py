import os

def create_dir_structure(base_dir):
    directories = [
        "assets/backgrounds",
        "assets/portraits",
        "assets/icons",
        "assets/themes",
        "data/monsters",
        "src/models",
        "src/ui",
    ]

    for directory in directories:
        path = os.path.join(base_dir, directory)
        os.makedirs(path, exist_ok=True)

def create_files(base_dir):
    files = {
        "requirements.txt": "pygame-ce\npygame_gui\npydantic\ninfinipy\n",
        "README.md": "# DnD Game\n\nA Dungeons and Dragons 5e video game using pygame and pygame_gui.",
        "src/main.py": """import pygame
import pygame_gui
from pygame.locals import *

pygame.init()

window_surface = pygame.display.set_mode((800, 600))
pygame.display.set_caption('DnD Game')

background = pygame.image.load('assets/backgrounds/default_background.png')

manager = pygame_gui.UIManager((800, 600))

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()
""",
        "src/ui/stats_block_window.py": """import pygame_gui
from pygame_gui.elements import UIWindow, UILabel, UIImage
from pydantic import BaseModel
import pygame

class StatsBlockWindow(UIWindow):
    def __init__(self, rect, manager, stats_block):
        super().__init__(rect, manager, window_display_title=stats_block.name)
        UILabel(relative_rect=pygame.Rect((10, 10), (150, 30)), text=f'Name: {stats_block.name}', manager=manager, container=self)
        UILabel(relative_rect=pygame.Rect((10, 50), (150, 30)), text=f'Size: {stats_block.size}', manager=manager, container=self)
        UILabel(relative_rect=pygame.Rect((10, 90), (150, 30)), text=f'Type: {stats_block.type}', manager=manager, container=self)
        portrait_image = pygame.image.load(f'assets/portraits/{stats_block.id}.png')
        UIImage(relative_rect=pygame.Rect((200, 10), (100, 100)), image_surface=portrait_image, manager=manager, container=self)
""",
    }

    for file_path, content in files.items():
        with open(os.path.join(base_dir, file_path), "w") as file:
            file.write(content)

if __name__ == "__main__":
    base_directory = "dnd_game"
    os.makedirs(base_directory, exist_ok=True)
    create_dir_structure(base_directory)
    create_files(base_directory)
    print(f"Project structure created in {base_directory}")
