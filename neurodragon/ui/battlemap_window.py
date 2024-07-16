import pygame
import pygame_gui
from pygame_gui.elements import UIWindow
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow
from dnd.tests.example_bm import create_battlemap_with_entities
from dnd.battlemap import MapDrawer, Entity

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
    'Skeleton': 'C:\\Users\\Tommaso\\Documents\\Dev\\dnd_game\\assets\\sprites\\skeleton.png'
}
class BattleMapWindow(UIWindow):
    active_window = None  # Class variable to track the active window

    def __init__(self, rect, manager, battle_map, details_window):
        super().__init__(rect, manager, window_display_title='Battle Map')

        self.battle_map = battle_map
        self.map_drawer = MapDrawer(self.battle_map)
        self.details_window = details_window
        
        # Create a surface to display the graphical representation of the battlemap
        self.map_surface = pygame.Surface((rect.width, rect.height))
        self.font = pygame.font.Font(None, 32)  # Define the font and size for ASCII characters
        
        self.offset_x = 0
        self.offset_y = 0

        self.grid_positions = {}

        self.render_battlemap()

        self.image_element = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((0, 0), (rect.width, rect.height)),
            image_surface=self.map_surface,
            manager=manager,
            container=self
        )

    def render_battlemap(self):
        tile_size = 32  # Define the size of each tile

        self.map_surface.fill((0, 0, 0))  # Clear the surface

        self.grid_positions.clear()  # Clear the hashmap

        # Draw the grid lines and store the positions
        for y in range(self.battle_map.height):
            for x in range(self.battle_map.width):
                draw_x = (x - self.offset_x) * tile_size
                draw_y = (y - self.offset_y) * tile_size

                # Skip drawing out-of-bound tiles
                if draw_x < 0 or draw_y < 0 or draw_x >= self.map_surface.get_width() or draw_y >= self.map_surface.get_height():
                    continue

                pygame.draw.rect(self.map_surface, (50, 50, 50), (draw_x, draw_y, tile_size, tile_size), 1)
                self.grid_positions[(x, y)] = (draw_x, draw_y)  # Store grid position as key, draw position as value

                entity_ids = self.battle_map.positions.get((x, y), None)
                if entity_ids:
                    entity_ids = list(entity_ids)
                    # Draw the first entity found at this position
                    entity = Entity.get_instance(entity_ids[0])
                    ascii_char = ENTITY_ASCII.get(entity.name, '?')
                    self.draw_ascii_char(ascii_char, draw_x, draw_y, tile_size, is_entity=True)
                else:
                    # Draw the tile if no entity is found
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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                BattleMapWindow.active_window = self
                container_rect = self.get_container().get_relative_rect()
                relative_click_pos = (
                    event.pos[0] - self.rect.left - container_rect.left - 10,  # Subtract 10 pixels from left
                    event.pos[1] - self.rect.top - container_rect.top - 16  # Subtract 16 pixels from top
                )
                self.handle_click(relative_click_pos)
        
        if BattleMapWindow.active_window == self:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.offset_y = max(self.offset_y - 1, 0)
                elif event.key == pygame.K_s:
                    self.offset_y = min(self.offset_y + 1, self.battle_map.height - self.map_surface.get_height() // 32)
                elif event.key == pygame.K_a:
                    self.offset_x = max(self.offset_x - 1, 0)
                elif event.key == pygame.K_d:
                    self.offset_x = min(self.offset_x + 1, self.battle_map.width - self.map_surface.get_width() // 32)

                self.render_battlemap()
                self.image_element.set_image(self.map_surface)

    def handle_click(self, click_pos):
        tile_size = 32

        clicked_grid_pos = None
        for grid_pos, draw_pos in self.grid_positions.items():
            if (draw_pos[0] <= click_pos[0] < draw_pos[0] + tile_size and
                draw_pos[1] <= click_pos[1] < draw_pos[1] + tile_size):
                clicked_grid_pos = grid_pos
                break

        if clicked_grid_pos:
            grid_x, grid_y = clicked_grid_pos
            print(f"Click position: {click_pos}, Grid position: ({grid_x}, {grid_y})")

            if 0 <= grid_x < self.battle_map.width and 0 <= grid_y < self.battle_map.height:
                tile_type = self.battle_map.get_tile(grid_x, grid_y)
                entity_ids = self.battle_map.positions.get((grid_x, grid_y), None)
                entity_name = None
                sprite_path = None

                if entity_ids:
                    entity_ids = list(entity_ids)
                    entity = Entity.get_instance(entity_ids[0])
                    entity_name = entity.name
                    sprite_path = SPRITE_PATHS.get(entity_name)
                else:
                    sprite_path = SPRITE_PATHS.get(tile_type)

                self.details_window.update_details((grid_x, grid_y), tile_type, entity_name, sprite_path)


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
def create_battlemap_window(manager, details_window):
    battle_map, goblin, skeleton = create_battlemap_with_entities()
    window_rect = pygame.Rect(0, 0, 800, 400)  # Adjusted size for tile rendering (20 tiles * 32px by 9 tiles * 32px)
    return BattleMapWindow(window_rect, manager, battle_map, details_window)

def create_details_window(manager):
    window_rect = pygame.Rect(820, 0, 400, 200)
    return DetailsWindow(window_rect, manager)
