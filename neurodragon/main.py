import pygame
import pygame_gui
from pygame.locals import *
import os

from neurodragon.ui.battlemap_window import create_battlemap_window, create_details_window

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

manager = pygame_gui.UIManager((int(width), int(height)))

clock = pygame.time.Clock()
is_running = True

# Create the details window
details_window = create_details_window(manager)

# Create the battlemap window
battlemap_window = create_battlemap_window(manager, details_window)

while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False

        manager.process_events(event)
        battlemap_window.process_event(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()