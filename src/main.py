import pygame
import pygame_gui
from pygame.locals import *

pygame.init()
width = 800
height = 600
factor = 1.7
width *= factor
height *= factor

window_surface = pygame.display.set_mode((width, height))
pygame.display.set_caption('DnD Game')

background = pygame.image.load(r'C:\Users\Tommaso\Documents\Dev\dnd_game\assets\backgrounds\glitched_neurodragon.png')

manager = pygame_gui.UIManager((width, height))

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
