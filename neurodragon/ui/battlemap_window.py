import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIImage, UIButton
from dnd.battlemap import Entity, BattleMap
from dnd.monsters.goblin import create_goblin
from dnd.monsters.skeleton import create_skeleton
from typing import Optional, Tuple, Dict
import time

from neurorefactor.config import config
from neurorefactor.event_handler import event_handler, handle_pygame_event, handle_game_event, GameEventType, GameEvent
from neurorefactor.ui.battlemap_renderer import render_battlemap

class BattleMapWindow(UIWindow):
    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager, battle_map: BattleMap):
        super().__init__(rect, manager, window_display_title='Battle Map')

        self.battle_map = battle_map
        self.set_dimensions(rect.size)
        self.initialize_components()
        self.setup_event_handlers()

    def initialize_components(self):
        self.button_size = config.sprites.size
        self.grey_column_width = 1.5*self.button_size[0] + 6

        self.map_surface = pygame.Surface((self.rect.width - self.grey_column_width, self.rect.height))
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

        self.create_buttons()
        self.render_battlemap()

    def create_buttons(self):
        button_definitions = [
            ('toggle_fov', 'Toggle FOV'),
            ('color_fov', 'Color FOV'),
            ('ray_to_target', 'Ray to Target'),
            ('toggle_paths', 'Toggle Paths'),
            ('path_to_target', 'Path to Target')
        ]

        button_x = self.rect.width - self.grey_column_width
        button_y = 0

        self.buttons = []

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
            self.buttons.append(button)
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
            if event.ui_element in self.buttons:
                self.handle_button_press(event.ui_element)




    def render_battlemap(self):
        self.map_surface = render_battlemap(
            self.map_surface,
            self.battle_map,
            self.selected_entity,
            self.target_position,
            self.offset,
            self.fov_mode,
            self.color_fov_mode,
            self.paths_mode,
            self.ray_mode,
            self.path_to_target_mode
        )
        self.image_element.set_image(self.map_surface)
        self.update_grid_positions()

    def update_grid_positions(self):
        tile_size = 32
        self.grid_positions.clear()
        for y in range(self.battle_map.height):
            for x in range(self.battle_map.width):
                draw_x = (x - self.offset[0]) * tile_size
                draw_y = (y - self.offset[1]) * tile_size
                if 0 <= draw_x < self.map_surface.get_width() and 0 <= draw_y < self.map_surface.get_height():
                    self.grid_positions[(x, y)] = (draw_x, draw_y)

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
        entity_ids = self.battle_map.positions.get(grid_pos, None)
        entity_name = None
        sprite_path = None

        if entity_ids:
            entity_ids = list(entity_ids)
            entity = Entity.get_instance(entity_ids[0])
            entity_name = entity.name
            sprite_path = config.sprites.paths.get(entity_name)
        else:
            sprite_path = config.sprites.paths.get(tile_type)

        event_handler.dispatch_game_event(GameEventType.TILE_SELECTED, {
            "position": grid_pos,
            "tile_type": tile_type,
            "entity_name": entity_name,
            "sprite_path": sprite_path,
            "battle_map": self.battle_map
        })

    def handle_double_left_click(self, grid_pos: Tuple[int, int]):
        entity_ids = self.battle_map.positions.get(grid_pos, None)
        if entity_ids:
            entity_id = list(entity_ids)[0]
            entity = Entity.get_instance(entity_id)
            self.selected_entity = entity
            print(f"Selected entity: {entity}")  # Debug print
            event_handler.dispatch_game_event(GameEventType.ENTITY_SELECTED, {"entity": entity})
        else:
            self.selected_entity = None
            print("No entity selected")  # Debug print
            event_handler.dispatch_game_event(GameEventType.ENTITY_SELECTED, {"entity": None})
        self.render_battlemap()

    def handle_right_click(self, grid_pos: Tuple[int, int]):
        entity_ids = self.battle_map.positions.get(grid_pos, None)
        if entity_ids:
            entity_id = list(entity_ids)[0]
            entity = Entity.get_instance(entity_id)
            event_handler.dispatch_game_event(GameEventType.TARGET_SET, {"entity": entity, "position": grid_pos})
        else:
            event_handler.dispatch_game_event(GameEventType.TARGET_SET, {"position": grid_pos})
        self.render_battlemap()

    def get_grid_position(self, click_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        tile_size = 32
        container_rect = self.get_container().get_relative_rect()
        adjusted_click_pos = (
            click_pos[0] - self.rect.left - container_rect.left - 12,
            click_pos[1] - self.rect.top - container_rect.top - 16
        )

        for grid_pos, draw_pos in self.grid_positions.items():
            if (draw_pos[0] <= adjusted_click_pos[0] < draw_pos[0] + tile_size and
                draw_pos[1] <= adjusted_click_pos[1] < draw_pos[1] + tile_size):
                return grid_pos
        return None

    def handle_button_press(self, button: UIButton):
        print(f"Button pressed: {button.tool_tip_text}")
        if button.tool_tip_text == 'Toggle FOV':
            print("Toggling FOV")
            self.fov_mode = not self.fov_mode
        elif button.tool_tip_text == 'Color FOV':
            self.color_fov_mode = not self.color_fov_mode
        elif button.tool_tip_text == 'Ray to Target':
            self.ray_mode = not self.ray_mode
        elif button.tool_tip_text == 'Toggle Paths':
            self.paths_mode = not self.paths_mode
        elif button.tool_tip_text == 'Path to Target':
            self.path_to_target_mode = not self.path_to_target_mode
        self.render_battlemap()

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                current_time = time.time()
                if self.last_left_clicked and current_time - self.last_left_clicked < 0.5:
                    self.handle_click(event.pos, 'double')
                else:
                    self.handle_click(event.pos, 'left')
                self.last_left_clicked = current_time
            elif event.button == 3:  # Right click
                self.handle_click(event.pos, 'right')
        
        super().process_event(event)

def create_battlemap_window(manager: pygame_gui.UIManager) -> BattleMapWindow:
    battle_map, _, _ = create_battlemap_with_entities()
    window_rect = pygame.Rect(
        config.ui.battlemap_window['left'],
        config.ui.battlemap_window['top'],
        config.ui.battlemap_window['width'],
        config.ui.battlemap_window['height']
    )
    return BattleMapWindow(window_rect, manager, battle_map)

def create_battlemap_with_entities() -> Tuple[BattleMap, Entity, Entity]:
    battle_map = BattleMap(width=config.battlemap.width, height=config.battlemap.height)

    map_list = list(config.battlemap.default_map.splitlines())
    for y, row in enumerate(map_list):
        for x, char in enumerate(row):
            if char == '#':
                battle_map.set_tile(x, y, "WALL")
            elif char == '.':
                battle_map.set_tile(x, y, "FLOOR")

    goblin = Entity.from_stats_block(create_goblin())
    skeleton = Entity.from_stats_block(create_skeleton())

    battle_map.add_entity(goblin, (18, 1))
    battle_map.add_entity(skeleton, (18, 7))

    return battle_map, goblin, skeleton