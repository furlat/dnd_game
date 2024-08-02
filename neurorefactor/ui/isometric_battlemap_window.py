import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIImage, UIButton, UILabel
from pygame_gui.windows import UIFileDialog
from typing import Optional, Tuple, Dict
import time
import random

from neurorefactor.config import config
from neurorefactor.event_handler import event_handler, handle_pygame_event, handle_game_event, GameEventType, GameEvent
from dnd.battlemap import Entity, BattleMap
from dnd.monsters.goblin import create_goblin
from dnd.monsters.skeleton import create_skeleton
from .isometric_grid import IsometricGrid, GridConfig

class IsometricBattlemapWindow(UIWindow):
    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager):
        super().__init__(rect, manager, window_display_title='Isometric Battle Map')

        self.battle_map = None
        self.isometric_grid = None
        self.background_image = None
        self.show_background = True
        self.show_grid = True
        self.show_labels = True
        
        self.set_dimensions(rect.size)
        self.initialize_components()
        self.setup_event_handlers()

    def initialize_components(self):
        self.button_size = config.sprites.size
        self.grey_column_width = 1.5 * self.button_size[0] + 6

        self.map_surface = pygame.Surface((self.rect.width - self.grey_column_width, self.rect.height), pygame.SRCALPHA)
        self.offset = (0, 0)
        self.grid_positions: Dict[Tuple[int, int], Tuple[int, int]] = {}
        self.fov_mode = False
        self.color_fov_mode = False
        self.selected_entity: Optional[Entity] = None
        self.target_position: Optional[Tuple[int, int]] = None
        self.ray_mode = False
        self.paths_mode = False
        self.path_to_target_mode = False
        self.last_left_clicked = None

        self.image_element = UIImage(
            relative_rect=pygame.Rect((0, 0), (self.rect.width - self.grey_column_width, self.rect.height)),
            image_surface=self.map_surface,
            manager=self.ui_manager,
            container=self
        )

        self.no_battlemap_label = UILabel(
            relative_rect=pygame.Rect((self.rect.width // 4, self.rect.height // 2 - 20, self.rect.width // 2, 40)),
            text="No battlemap loaded. Please load a battlemap.",
            manager=self.ui_manager,
            container=self
        )

        self.create_buttons()

    def create_buttons(self):
        button_definitions = [
            ('load_battlemap', 'Load Battlemap'),
            ('toggle_fov', 'Toggle FOV'),
            ('color_fov', 'Color FOV'),
            ('ray_to_target', 'Ray to Target'),
            ('toggle_paths', 'Toggle Paths'),
            ('path_to_target', 'Path to Target'),
            ('toggle_grid', 'Toggle Grid'),
            ('toggle_labels', 'Toggle Labels'),
            ('toggle_background', 'Toggle Background')
        ]

        button_x = self.rect.width - self.grey_column_width
        button_y = 0

        self.buttons = {}

        for button_id, tooltip in button_definitions:
            button = UIButton(
                relative_rect=pygame.Rect(button_x, button_y, self.button_size[0], self.button_size[1]),
                text='',
                manager=self.ui_manager,
                container=self,
                tool_tip_text=tooltip,
                object_id=pygame_gui.core.ObjectID(class_id=f'@{button_id}_button')
            )
            button_image = pygame.image.load(config.sprites.paths[button_id])
            button_image = pygame.transform.scale(button_image, self.button_size)
            button.set_image(button_image)
            self.buttons[button_id] = button
            button_y += self.button_size[1]

    def setup_event_handlers(self):
        @handle_game_event(GameEventType.ENTITY_SELECTED)
        def on_entity_selected(event: GameEvent):
            self.selected_entity = event.data['entity']
            self.render_battlemap()

        @handle_game_event(GameEventType.TARGET_SET)
        def on_target_set(event: GameEvent):
            self.target_position = event.data['position']
            self.render_battlemap()

        @handle_game_event(GameEventType.RENDER_BATTLEMAP)
        def on_render_battlemap(event: GameEvent):
            self.render_battlemap()
        
        @handle_pygame_event(pygame_gui.UI_BUTTON_PRESSED)
        def on_button_pressed(event: pygame.event.Event):
            if event.ui_element in self.buttons.values():
                button_id = next(key for key, value in self.buttons.items() if value == event.ui_element)
                self.handle_button_press(button_id)

    def render_battlemap(self):
        if not self.battle_map or not self.isometric_grid:
            self.no_battlemap_label.show()
            return
        else:
            self.no_battlemap_label.hide()

        self.map_surface.fill((0, 0, 0, 0))  # Clear the surface with transparency

        if self.show_background and self.background_image:
            self.map_surface.blit(self.background_image, (0, 0))

        if self.show_grid:
            self.draw_grid()

        if self.show_labels:
            self.draw_labels()

        self.draw_entities()

        if self.fov_mode:
            self.draw_fov()

        if self.ray_mode and self.target_position:
            self.draw_ray()

        if self.paths_mode:
            self.draw_paths()

        if self.path_to_target_mode and self.target_position:
            self.draw_path_to_target()

        self.image_element.set_image(self.map_surface)
        self.update_grid_positions()

    def draw_grid(self):
        for x in range(self.isometric_grid.width + 1):
            start = self.isometric_grid.grid_to_screen(x, 0)
            end = self.isometric_grid.grid_to_screen(x, self.isometric_grid.height)
            pygame.draw.line(self.map_surface, (255, 255, 255), start, end, 1)  # Changed color to white and thickness to 1

        for y in range(self.isometric_grid.height + 1):
            start = self.isometric_grid.grid_to_screen(0, y)
            end = self.isometric_grid.grid_to_screen(self.isometric_grid.width, y)
            pygame.draw.line(self.map_surface, (255, 255, 255), start, end, 1)  # Changed color to white and thickness to 1

    def draw_labels(self):
        for x in range(self.isometric_grid.width):
            for y in range(self.isometric_grid.height):
                tile_type = self.battle_map.get_tile(x, y)
                color = self.get_tile_color(tile_type)
                points = [
                    self.isometric_grid.grid_to_screen(x, y),
                    self.isometric_grid.grid_to_screen(x + 1, y),
                    self.isometric_grid.grid_to_screen(x + 1, y + 1),
                    self.isometric_grid.grid_to_screen(x, y + 1)
                ]
                pygame.draw.polygon(self.map_surface, color, points)

    def draw_entities(self):
        for entity in Entity.all_instances():
            if entity.position:
                sprite_path = config.sprites.paths.get(entity.name)
                if sprite_path:
                    sprite = pygame.image.load(sprite_path)
                    sprite = pygame.transform.scale(sprite, (self.isometric_grid.tile_size, self.isometric_grid.tile_size))
                    screen_x, screen_y = self.isometric_grid.grid_to_screen(*entity.position)
                    self.map_surface.blit(sprite, (screen_x - self.isometric_grid.tile_size // 2, 
                                                   screen_y - self.isometric_grid.tile_size))

    def draw_fov(self):
        # Implement FOV drawing logic here
        pass

    def draw_ray(self):
        # Implement ray drawing logic here
        pass

    def draw_paths(self):
        # Implement paths drawing logic here
        pass

    def draw_path_to_target(self):
        # Implement path to target drawing logic here
        pass

    def handle_button_press(self, button_id: str):
        if button_id == 'load_battlemap':
            self.load_battlemap()
        elif self.battle_map and self.isometric_grid:
            if button_id == 'toggle_fov':
                self.fov_mode = not self.fov_mode
            elif button_id == 'color_fov':
                self.color_fov_mode = not self.color_fov_mode
            elif button_id == 'ray_to_target':
                self.ray_mode = not self.ray_mode
            elif button_id == 'toggle_paths':
                self.paths_mode = not self.paths_mode
            elif button_id == 'path_to_target':
                self.path_to_target_mode = not self.path_to_target_mode
            elif button_id == 'toggle_grid':
                self.show_grid = not self.show_grid
            elif button_id == 'toggle_labels':
                self.show_labels = not self.show_labels
            elif button_id == 'toggle_background':
                self.show_background = not self.show_background
            
            self.render_battlemap()

    def load_battlemap(self):
        self.file_dialog = UIFileDialog(
            rect=pygame.Rect(160, 50, 440, 500),
            manager=self.ui_manager,
            window_title='Load Battlemap...',
            initial_file_path='',
            allow_picking_directories=False,
            allow_existing_files_only=True,
            allowed_suffixes={".json"}
        )

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.battle_map and self.isometric_grid:
            if event.button == 1:  # Left click
                current_time = time.time()
                if self.last_left_clicked and current_time - self.last_left_clicked < 0.5:
                    self.handle_click(event.pos, 'double')
                else:
                    self.handle_click(event.pos, 'left')
                self.last_left_clicked = current_time
            elif event.button == 3:  # Right click
                self.handle_click(event.pos, 'right')
        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == self.file_dialog:
                self.load_battlemap_from_file(event.text)
        
        super().process_event(event)

    def load_battlemap_from_file(self, file_path: str):
        grid_config = GridConfig.load(file_path)
        self.battle_map = self.create_battlemap_from_config(grid_config)
        self.isometric_grid = IsometricGrid(
            self.battle_map.width,
            self.battle_map.height,
            config.isometric.tile_size,
            (self.rect.width - self.grey_column_width, self.rect.height),
            isometric_angle=config.isometric.isometric_angle,
            rotation=config.isometric.rotation
        )
        if grid_config.image_path:
            self.background_image = pygame.image.load(grid_config.image_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.rect.width - self.grey_column_width, self.rect.height))
        self.render_battlemap()
        event_handler.dispatch_game_event(GameEventType.BATTLEMAP_LOADED, {"battle_map": self.battle_map})

    def create_battlemap_from_config(self, grid_config: GridConfig) -> BattleMap:
        battle_map = BattleMap(width=grid_config.grid_size_x, height=grid_config.grid_size_y)

        # Set tiles based on the loaded configuration
        for y in range(grid_config.grid_size_y):
            for x in range(grid_config.grid_size_x):
                tile_type = grid_config.tile_tags.get((x, y), "FLOOR").upper()
                battle_map.set_tile(x, y, tile_type)

        # Add entities to random floor tiles
        self.add_entities_to_battlemap(battle_map)

        return battle_map

    def add_entities_to_battlemap(self, battle_map: BattleMap):
        def get_random_floor_tile():
            floor_tiles = [
                (x, y) for x in range(battle_map.width) for y in range(battle_map.height)
                if battle_map.get_tile(x, y) == "FLOOR" and not battle_map.positions.get((x, y))
            ]
            return random.choice(floor_tiles) if floor_tiles else None

        # Add a goblin
        goblin_pos = get_random_floor_tile()
        if goblin_pos:
            goblin = Entity.from_stats_block(create_goblin())
            battle_map.add_entity(goblin, goblin_pos)
            print(f"Added goblin at {goblin_pos}")

        # Add a skeleton
        skeleton_pos = get_random_floor_tile()
        if skeleton_pos:
            skeleton = Entity.from_stats_block(create_skeleton())
            battle_map.add_entity(skeleton, skeleton_pos)
            print(f"Added skeleton at {skeleton_pos}")

    def get_grid_position(self, click_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if not self.isometric_grid:
            return None
        
        container_rect = self.get_container().get_relative_rect()
        adjusted_click_pos = (
            click_pos[0] - self.rect.left - container_rect.left,
            click_pos[1] - self.rect.top - container_rect.top
        )

        return self.isometric_grid.screen_to_grid(*adjusted_click_pos)

    def get_tile_color(self, tile_type: str) -> Tuple[int, int, int, int]:
        # Updated to include void and water labels
        if tile_type == 'WALL':
            return (255, 0, 0, 100)  # Red
        elif tile_type == 'FLOOR':
            return (0, 255, 0, 100)  # Green
        elif tile_type == 'VOID':
            return (0, 0, 0, 50)  # Semi-transparent Black
        elif tile_type == 'WATER':
            return (0, 0, 255, 100)  # Blue
        else:
            return (0, 0, 255, 100)  # Default to Blue

    def handle_click(self, click_pos: Tuple[int, int], click_type: str):
        grid_pos = self.get_grid_position(click_pos)
        if grid_pos:
            if click_type == 'left':
                self.handle_left_click(grid_pos)
            elif click_type == 'double':
                self.handle_double_left_click(grid_pos)
            elif click_type == 'right':
                self.handle_right_click(grid_pos)

    def handle_left_click(self, grid_pos: Tuple[int, int]):
        tile_type = self.battle_map.get_tile(*grid_pos)
        entity_id = self.battle_map.positions[grid_pos]
        entity = Entity.get_instance(entity_id) if entity_id else None
        entity_name = entity.name if entity else None
        sprite_path = config.sprites.paths.get(entity_name) if entity_name else config.sprites.paths.get(tile_type)

        event_handler.dispatch_game_event(GameEventType.TILE_SELECTED, {
            "position": grid_pos,
            "tile_type": tile_type,
            "entity_name": entity_name,
            "sprite_path": sprite_path,
            "battle_map": self.battle_map
        })

    def handle_double_left_click(self, grid_pos: Tuple[int, int]):
        entity_id = self.battle_map.positions[grid_pos]
        entity = Entity.get_instance(entity_id) if entity_id else None
        if entity:
            self.selected_entity = entity
            event_handler.dispatch_game_event(GameEventType.ENTITY_SELECTED, {"entity": entity})
        else:
            self.selected_entity = None
            event_handler.dispatch_game_event(GameEventType.ENTITY_SELECTED, {"entity": None})
        self.render_battlemap()

    def handle_right_click(self, grid_pos: Tuple[int, int]):
        entity_id = self.battle_map.positions[grid_pos]
        entity = Entity.get_instance(entity_id) if entity_id else None
        if entity:
            event_handler.dispatch_game_event(GameEventType.TARGET_SET, {"entity": entity, "position": grid_pos})
        else:
            event_handler.dispatch_game_event(GameEventType.TARGET_SET, {"position": grid_pos})
        self.render_battlemap()

    def update_grid_positions(self):
        self.grid_positions.clear()
        for y in range(self.battle_map.height):
            for x in range(self.battle_map.width):
                screen_x, screen_y = self.isometric_grid.grid_to_screen(x, y)
                if 0 <= screen_x < self.map_surface.get_width() and 0 <= screen_y < self.map_surface.get_height():
                    self.grid_positions[(x, y)] = (screen_x, screen_y)

def create_isometric_battlemap_window(manager: pygame_gui.UIManager) -> IsometricBattlemapWindow:
    window_rect = pygame.Rect(
        config.ui.battlemap_window['left'],
        config.ui.battlemap_window['top'],
        config.ui.battlemap_window['width'],
        config.ui.battlemap_window['height']
    )
    return IsometricBattlemapWindow(window_rect, manager)
