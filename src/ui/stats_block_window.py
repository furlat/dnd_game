import pygame_gui
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
