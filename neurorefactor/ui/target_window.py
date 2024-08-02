import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UITextBox, UIImage
from dnd.battlemap import Entity
from typing import Optional, Tuple, Union
from neurorefactor.config import config
from neurorefactor.event_handler import handle_game_event, GameEventType, GameEvent

class TargetWindow(UIWindow):
    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager):
        super().__init__(rect, manager, window_display_title='Target')

        self.target_pos: Optional[Tuple[int, int]] = None
        self.target_entity: Optional[Entity] = None
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
            html_text="No target selected.",
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
        @handle_game_event(GameEventType.TARGET_SET)
        def on_target_set(event: GameEvent):
            if 'entity' in event.data:
                self.update_details(event.data['entity'])
            elif 'position' in event.data:
                self.update_details(event.data['position'])

    def update_details(self, target: Union[Entity, Tuple[int, int]]):
        if isinstance(target, Entity):
            self.target_entity = target
            self.target_pos = None
            details = f"Name: {target.name}<br>Hit Points: {target.hp}/{target.health.max_hit_points}<br>ID: {target.id}"
            self.text_element.set_text(details)

            combined_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            entity_sprite_path = config.sprites.paths.get(target.name)

            if entity_sprite_path:
                entity_sprite_surface = pygame.image.load(entity_sprite_path).convert_alpha()
                entity_sprite_surface = pygame.transform.scale(entity_sprite_surface, (80, 80))
                combined_surface.blit(entity_sprite_surface, (0, 0))

            self.image_element.set_image(combined_surface)
        elif isinstance(target, tuple):
            self.target_pos = target
            self.target_entity = None
            details = f"Position: {target}"
            self.text_element.set_text(details)
            self.image_element.set_image(self.default_surface)
        else:
            self.text_element.set_text("No target selected.")
            self.image_element.set_image(self.default_surface)
            self.target_pos = None
            self.target_entity = None

def create_target_window(manager: pygame_gui.UIManager) -> TargetWindow:
    window_rect = pygame.Rect(
        config.ui.target_window['left'],
        config.ui.target_window['top'],
        config.ui.target_window['width'],
        config.ui.target_window['height']
    )
    return TargetWindow(window_rect, manager)