import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UITextBox, UIImage

# Define a dictionary to map tiles and entities to sprite file paths
SPRITE_PATHS = {
    'WALL': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\wall.png',
    'FLOOR': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\floor.png',
    'Goblin': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\goblin.png',
    'Skeleton': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\skeleton.png'
}

class ActiveEntityWindow(UIWindow):
    def __init__(self, rect, manager):
        super().__init__(rect, manager, window_display_title='Active Entity')

        text_width = rect.width - 120
        text_height = 80
        text_rect = pygame.Rect(10, 10, text_width, text_height + 10)
        image_rect = pygame.Rect(rect.width - 100, ((text_height + 10) // 2) - 10, 120, 120)

        self.text_element = UITextBox(
            html_text="No active entity.",
            relative_rect=text_rect,
            manager=manager,
            container=self
        )

        self.default_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.image_element = UIImage(
            relative_rect=image_rect,
            image_surface=self.default_surface,
            manager=manager,
            container=self
        )

    def update_details(self, entity):
        if entity:
            details = f"Name: {entity.name}<br>ID: {entity.id}<br>Hit Points: {entity.current_hit_points}/{entity.max_hit_points}"
            self.text_element.set_text(details)

            # Update with the entity's sprite if available
            combined_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            entity_sprite_path = SPRITE_PATHS.get(entity.name)

            if entity_sprite_path:
                entity_sprite_surface = pygame.image.load(entity_sprite_path).convert_alpha()
                combined_surface.blit(entity_sprite_surface, (0, 0))

            self.image_element.set_image(combined_surface)
        else:
            self.text_element.set_text("No active entity.")
            self.image_element.set_image(self.default_surface)
