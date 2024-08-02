import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UITextBox, UIImage
from neurorefactor.config import config
from neurorefactor.event_handler import handle_game_event, GameEventType, GameEvent
from dnd.battlemap import Entity

class DetailsWindow(UIWindow):
    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager):
        super().__init__(rect, manager, window_display_title='Details')

        self.set_dimensions(rect.size)
        self.initialize_components()
        self.setup_event_handlers()

    def initialize_components(self):
        padding = 10
        image_size = 80

        # Calculate sizes based on the window dimensions
        text_width = self.rect.width - (3 * padding) - image_size
        text_height = self.rect.height - (2 * padding)

        # Position text box
        text_rect = pygame.Rect(padding, padding, text_width, text_height)

        # Position image
        image_rect = pygame.Rect(
            self.rect.width - image_size - padding,
            padding,
            image_size,
            image_size
        )

        self.text_element = UITextBox(
            html_text="",
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
        @handle_game_event(GameEventType.TILE_SELECTED)
        def on_tile_selected(event: GameEvent):
            self.update_details(event.data['position'], event.data['battle_map'])

        @handle_game_event(GameEventType.ENTITY_SELECTED)
        def on_entity_selected(event: GameEvent):
            self.update_entity_details(event.data['entity'])

    def update_details(self, position: tuple, battle_map):
        tile_type = battle_map.get_tile(*position)
        entity_ids = battle_map.positions.get(position, None)
        entity_name = None
        sprite_path = None

        if entity_ids:
            entity_ids = list(entity_ids)
            entity = Entity.get_instance(entity_ids[0])
            entity_name = entity.name
            sprite_path = config.sprites.paths.get(entity_name)
        else:
            sprite_path = config.sprites.paths.get(tile_type)

        details = f"Position: {position}<br>Tile Type: {tile_type}<br>Entity: {entity_name}"
        self.text_element.set_text(details)

        self.update_image(tile_type, sprite_path)

    def update_entity_details(self, entity: Entity):
        details = f"Name: {entity.name}<br>HP: {entity.hp}/{entity.health.max_hit_points}<br>ID: {entity.id}"
        self.text_element.set_text(details)

        sprite_path = config.sprites.paths.get(entity.name)
        self.update_image(None, sprite_path)

    def update_image(self, tile_type: str, entity_sprite_path: str):
        image_size = 80
        combined_surface = pygame.Surface((image_size, image_size), pygame.SRCALPHA)
        tile_sprite_path = config.sprites.paths.get(tile_type) if tile_type else None

        if tile_sprite_path:
            tile_sprite_surface = pygame.image.load(tile_sprite_path).convert_alpha()
            tile_sprite_surface = pygame.transform.scale(tile_sprite_surface, (image_size, image_size))
            combined_surface.blit(tile_sprite_surface, (0, 0))

        if entity_sprite_path:
            entity_sprite_surface = pygame.image.load(entity_sprite_path).convert_alpha()
            entity_sprite_surface = pygame.transform.scale(entity_sprite_surface, (image_size, image_size))
            combined_surface.blit(entity_sprite_surface, (0, 0))

        self.image_element.set_image(combined_surface)

    def clear_details(self):
        self.text_element.set_text("No details available")
        self.image_element.set_image(self.default_surface)

def create_details_window(manager: pygame_gui.UIManager) -> DetailsWindow:
    window_rect = pygame.Rect(
        config.ui.details_window['left'],
        config.ui.details_window['top'],
        config.ui.details_window['width'],
        config.ui.details_window['height']
    )
    return DetailsWindow(window_rect, manager)