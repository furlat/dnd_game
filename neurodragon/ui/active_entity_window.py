import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UITextBox, UIImage
from dnd.battlemap import Entity
from typing import Optional
from neurorefactor.config import config
from neurorefactor.event_handler import handle_game_event, GameEventType, GameEvent

class ActiveEntityWindow(UIWindow):
    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager):
        super().__init__(rect, manager, window_display_title='Active Entity')

        self.set_dimensions(rect.size)
        self.initialize_components()
        self.setup_event_handlers()

    def initialize_components(self):
        padding = 10
        image_size = 80

        text_width = self.rect.width - (3 * padding) - image_size
        text_height = self.rect.height - (2 * padding)

        text_rect = pygame.Rect(padding, padding, text_width, text_height)
        image_rect = pygame.Rect(
            self.rect.width - image_size - padding,
            padding,
            image_size,
            image_size
        )

        self.text_element = UITextBox(
            html_text="No active entity.",
            relative_rect=text_rect,
            manager=self.ui_manager,
            container=self
        )

        self.default_surface = pygame.Surface((image_size, image_size), pygame.SRCALPHA)
        self.image_element = UIImage(
            relative_rect=image_rect,
            image_surface=self.default_surface,
            manager=self.ui_manager,
            container=self
        )

    def setup_event_handlers(self):
        @handle_game_event(GameEventType.ENTITY_SELECTED)
        def on_entity_selected(event: GameEvent):
            self.update_details(event.data['entity'])

    def update_details(self, entity: Optional[Entity]):
        if entity:
            details = f"Name: {entity.name}<br>Hit Points: {entity.hp}/{entity.health.max_hit_points}<br>ID: {entity.id}"
            self.text_element.set_text(details)

            combined_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            entity_sprite_path = config.sprites.paths.get(entity.name)

            if entity_sprite_path:
                entity_sprite_surface = pygame.image.load(entity_sprite_path).convert_alpha()
                entity_sprite_surface = pygame.transform.scale(entity_sprite_surface, (80, 80))
                combined_surface.blit(entity_sprite_surface, (0, 0))

            self.image_element.set_image(combined_surface)
        else:
            self.text_element.set_text("No active entity.")
            self.image_element.set_image(self.default_surface)

def create_active_entity_window(manager: pygame_gui.UIManager) -> ActiveEntityWindow:
    window_rect = pygame.Rect(
        config.ui.active_entity_window['left'],
        config.ui.active_entity_window['top'],
        config.ui.active_entity_window['width'],
        config.ui.active_entity_window['height']
    )
    return ActiveEntityWindow(window_rect, manager)


