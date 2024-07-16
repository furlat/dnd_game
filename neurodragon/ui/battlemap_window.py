import pygame
import pygame_gui
from pygame_gui.elements import UIButton
from pygame_gui.elements import UIWindow, UIImage, UITextBox
from dnd.tests.example_bm import create_battlemap_with_entities
from dnd.battlemap import Entity
import time

# Define a dictionary to map tiles to ASCII characters
TILE_ASCII = {
    'WALL': '#',
    'FLOOR': '.'
}

# Define a dictionary to map entities to ASCII characters
ENTITY_ASCII = {
    'Goblin': 'g',
    'Skeleton': 's'
}

# Define a dictionary to map tiles and entities to sprite file paths
SPRITE_PATHS = {
    'WALL': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\wall.png',
    'FLOOR': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\floor.png',
    'Goblin': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\goblin.png',
    'Skeleton': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\skeleton.png',
    'toggle_fov': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\toggle_fov.png',
    'color_fov': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\color_fov.png',
    'ray_to_target': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\ray_to_target.png',
    'toggle_paths': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\toggle_paths.png',
    'path_to_target': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\path_to_target.png'
}

class BattleMapWindow(UIWindow):
    active_window = None

    def __init__(self, rect, manager, battle_map, details_window, active_entity_window, target_window):
        super().__init__(rect, manager, window_display_title='Battle Map')

        self.battle_map = battle_map
        self.details_window = details_window
        self.active_entity_window = active_entity_window
        self.target_window = target_window

        button_width = 50  # Adjust width for buttons
        button_height = 50
        grey_column_width = button_width + 2  # Match button width

        self.map_surface = pygame.Surface((rect.width - grey_column_width, rect.height))  # Adjust width for buttons
        self.font = pygame.font.Font(None, 32)

        self.offset_x = 0
        self.offset_y = 0

        self.grid_positions = {}

        self.render_battlemap()

        self.last_left_clicked = None

        self.image_element = UIImage(
            relative_rect=pygame.Rect((0, 0), (rect.width - grey_column_width, rect.height)),  # Adjust width for buttons
            image_surface=self.map_surface,
            manager=manager,
            container=self
        )

        # Create buttons
        self.create_buttons(rect, manager, button_width, button_height, grey_column_width)
        self.handled_events = []
        self.handled_events_time = []

    def create_buttons(self, rect, manager, button_width, button_height, grey_column_width):
        button_definitions = [
            ('toggle_fov', 'Toggle FOV'),
            ('color_fov', 'Color FOV'),
            ('ray_to_target', 'Ray to Target'),
            ('toggle_paths', 'Toggle Paths'),
            ('path_to_target', 'Path to Target')
        ]

        button_x = rect.width - grey_column_width  # Align to the right edge
        button_y = 0  # Start at the top

        self.buttons = []

        for button_id, tooltip in button_definitions:
            button = UIButton(
                relative_rect=pygame.Rect(button_x, button_y, button_width, button_height),
                text='',
                manager=manager,
                container=self,
                tool_tip_text=tooltip,
                object_id=pygame_gui.core.ObjectID(class_id=f'@{button_id}_button')
            )
            button_image = pygame.image.load(SPRITE_PATHS[button_id])
            button_image = pygame.transform.scale(button_image, (button_width, button_height))
            button.set_image(button_image)
            self.buttons.append(button)
            button_y += button_height  # Move the next button down without spacing

    def render_battlemap(self):
        tile_size = 32

        self.map_surface.fill((0, 0, 0))

        self.grid_positions.clear()

        for y in range(self.battle_map.height):
            for x in range(self.battle_map.width):
                draw_x = (x - self.offset_x) * tile_size
                draw_y = (y - self.offset_y) * tile_size

                if draw_x < 0 or draw_y < 0 or draw_x >= self.map_surface.get_width() or draw_y >= self.map_surface.get_height():
                    continue

                pygame.draw.rect(self.map_surface, (50, 50, 50), (draw_x, draw_y, tile_size, tile_size), 1)
                self.grid_positions[(x, y)] = (draw_x, draw_y)

                entity_ids = self.battle_map.positions.get((x, y), None)
                if entity_ids:
                    entity_ids = list(entity_ids)
                    entity = Entity.get_instance(entity_ids[0])
                    ascii_char = ENTITY_ASCII.get(entity.name, '?')
                    self.draw_ascii_char(ascii_char, draw_x, draw_y, tile_size, is_entity=True)
                else:
                    tile_type = self.battle_map.get_tile(x, y)
                    if tile_type:
                        ascii_char = TILE_ASCII.get(tile_type, ' ')
                        self.draw_ascii_char(ascii_char, draw_x, draw_y, tile_size)

    def draw_ascii_char(self, char, x, y, tile_size, is_entity=False):
        color = (255, 0, 0) if is_entity else (255, 255, 255)
        text_surface = self.font.render(char, True, color)
        text_rect = text_surface.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
        self.map_surface.blit(text_surface, text_rect)

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if not self.last_left_clicked:
                    self.last_left_clicked = time.time()
                    self.handle_left_click(event.pos)
                elif time.time() - self.last_left_clicked < 0.5:
                    self.handle_double_click(event.pos)
                    self.last_left_clicked = None
                else:
                    self.last_left_clicked = None
                    self.handle_left_click(event.pos)
            elif event.button == 3:
                self.handle_right_click(event.pos)

        # Process button clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED :
            print(event,event.type,time.time())
            if len(self.handled_events)>0 and event == self.handled_events[-1] and time.time() - self.handled_events_time[-1] < 0.5:
                print(f"detected double click for {event}")
            
            elif hasattr(event.ui_element, 'tool_tip_text'):
                print(f"{event.ui_element.tool_tip_text} button clicked")
                self.handled_events.append(event)
                self.handled_events_time.append(time.time())
                return

        super().process_event(event)

    def handle_click(self, click_pos, click_type):
        tile_size = 32
        container_rect = self.get_container().get_relative_rect()
        adjusted_click_pos = (
            click_pos[0] - self.rect.left - container_rect.left - 10,
            click_pos[1] - self.rect.top - container_rect.top - 16
        )

        for grid_pos, draw_pos in self.grid_positions.items():
            if (draw_pos[0] <= adjusted_click_pos[0] < draw_pos[0] + tile_size and
                draw_pos[1] <= adjusted_click_pos[1] < draw_pos[1] + tile_size):
                if click_type == 'left':
                    self.update_details_window(grid_pos)
                elif click_type == 'double':
                    self.update_active_entity_window(grid_pos)
                elif click_type == 'right':
                    self.update_target_window(grid_pos)
                break

    def handle_left_click(self, click_pos):
        self.handle_click(click_pos, 'left')

    def handle_double_click(self, click_pos):
        self.handle_click(click_pos, 'double')

    def handle_right_click(self, click_pos):
        self.handle_click(click_pos, 'right')

    def update_details_window(self, grid_pos):
        tile_type = self.battle_map.get_tile(*grid_pos)
        entity_ids = self.battle_map.positions.get(grid_pos, None)
        entity_name = None
        sprite_path = None

        if entity_ids:
            entity_ids = list(entity_ids)
            entity = Entity.get_instance(entity_ids[0])
            entity_name = entity.name
            sprite_path = SPRITE_PATHS.get(entity_name)
        else:
            sprite_path = SPRITE_PATHS.get(tile_type)

        self.details_window.update_details(grid_pos, tile_type, entity_name, sprite_path)

    def update_active_entity_window(self, grid_pos):
        entity_ids = self.battle_map.positions.get(grid_pos, None)
        if entity_ids:
            entity_id = list(entity_ids)[0]
            entity = Entity.get_instance(entity_id)
            self.active_entity_window.update_details(entity)

    def update_target_window(self, grid_pos):
        entity_ids = self.battle_map.positions.get(grid_pos, None)
        if entity_ids:
            entity_id = list(entity_ids)[0]
            entity = Entity.get_instance(entity_id)
            self.target_window.update_details(entity)
        else:
            self.target_window.update_details(grid_pos)

# This function will be used in the main file to create and display the window
def create_battlemap_window(manager, details_window, active_entity_window, target_window):
    battle_map, goblin, skeleton = create_battlemap_with_entities()
    window_rect = pygame.Rect(0, 0, 850, 400)  # Adjusted width for buttons
    return BattleMapWindow(window_rect, manager, battle_map, details_window, active_entity_window, target_window)


class DetailsWindow(UIWindow):
    def __init__(self, rect, manager):
        super().__init__(rect, manager, window_display_title='Details')

        text_width = rect.width - 120
        text_height = 80  # Adjust the height based on the expected text content
        text_rect = pygame.Rect(10, 10, text_width, text_height+10)
        image_rect = pygame.Rect(rect.width - 100, ((text_height+10) // 2)-10, 120, 120)

        self.text_element = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=text_rect,
            manager=manager,
            container=self
        )

        self.default_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.image_element = pygame_gui.elements.UIImage(
            relative_rect=image_rect,
            image_surface=self.default_surface,
            manager=manager,
            container=self
        )

    def update_details(self, position, tile_type, entity_name, sprite_path):
        details = f"Position: {position}<br>Tile Type: {tile_type}<br>Entity: {entity_name}"
        self.text_element.set_text(details)

        combined_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        tile_sprite_path = SPRITE_PATHS.get(tile_type)
        entity_sprite_path = SPRITE_PATHS.get(entity_name)

        if tile_sprite_path:
            tile_sprite_surface = pygame.image.load(tile_sprite_path).convert_alpha()
            combined_surface.blit(tile_sprite_surface, (0, 0))

        if entity_sprite_path:
            entity_sprite_surface = pygame.image.load(entity_sprite_path).convert_alpha()
            combined_surface.blit(entity_sprite_surface, (0, 0))

        self.image_element.set_image(combined_surface)

# This function will be used in the main file to create and display the window
def create_details_window(manager):
    window_rect = pygame.Rect(820, 0, 400, 200)
    return DetailsWindow(window_rect, manager)
