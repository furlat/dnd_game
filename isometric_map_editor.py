import pygame
import pygame_gui
import math
import json
import os
from pygame_gui.windows import UIFileDialog
from pydantic import BaseModel
from typing import Tuple, Dict, Union, Optional

class GridConfig(BaseModel):
    tile_size: int
    grid_size_x: int
    grid_size_y: int
    grid_origin_x: int
    grid_origin_y: int
    isometric_angle: float
    rotation: float
    image_path: Optional[str] = None
    image_scale: int = 100
    tile_tags: Dict[Union[Tuple[int, int], str], str] = {}

    def save(self, file_path: str):
        data = self.model_dump()
        # Convert all keys to strings for JSON serialization
        data['tile_tags'] = {f"{k[0]},{k[1]}" if isinstance(k, tuple) else k: v 
                             for k, v in self.tile_tags.items()}
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Convert string keys to tuples
        if 'tile_tags' in data:
            tile_tags = {}
            for k, v in data['tile_tags'].items():
                try:
                    key_parts = k.split(',')
                    if len(key_parts) >= 2:
                        x, y = int(key_parts[0]), int(key_parts[1])
                        tile_tags[(x, y)] = v
                    else:
                        print(f"Skipping malformed tile tag key: {k}")
                except ValueError:
                    print(f"Skipping invalid tile tag key: {k}")
            data['tile_tags'] = tile_tags
        return cls(**data)

class IsometricGrid:
    def __init__(self, width, height, tile_size, window_size, origin=(0, 0), isometric_angle=30, rotation=0):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.window_size = window_size
        self.origin = origin
        self.isometric_angle = math.radians(isometric_angle)
        self.rotation = math.radians(rotation)
        self.highlighted_cell = None

    def grid_to_screen(self, grid_x, grid_y):
        iso_x = (grid_x - grid_y) * math.cos(self.isometric_angle)
        iso_y = (grid_x + grid_y) * math.sin(self.isometric_angle)
        
        rotated_x = iso_x * math.cos(self.rotation) - iso_y * math.sin(self.rotation)
        rotated_y = iso_x * math.sin(self.rotation) + iso_y * math.cos(self.rotation)
        
        screen_x = rotated_x * self.tile_size + self.origin[0] + self.window_size[0] // 2
        screen_y = rotated_y * self.tile_size + self.origin[1] + self.window_size[1] // 2
        return int(screen_x), int(screen_y)

    def screen_to_grid(self, screen_x, screen_y):
        # Translate to origin
        translated_x = screen_x - self.origin[0] - self.window_size[0] // 2
        translated_y = screen_y - self.origin[1] - self.window_size[1] // 2
        
        # Unrotate
        unrotated_x = translated_x * math.cos(-self.rotation) - translated_y * math.sin(-self.rotation)
        unrotated_y = translated_x * math.sin(-self.rotation) + translated_y * math.cos(-self.rotation)
        
        # Scale down
        scaled_x = unrotated_x / self.tile_size
        scaled_y = unrotated_y / self.tile_size
        
        # Convert from isometric to grid coordinates
        grid_y = (scaled_y / math.sin(self.isometric_angle) - scaled_x / math.cos(self.isometric_angle)) / 2
        grid_x = scaled_y / math.sin(self.isometric_angle) - grid_y
        
        return round(grid_x), round(grid_y)

    def is_in_grid(self, screen_x, screen_y):
        grid_x, grid_y = self.screen_to_grid(screen_x, screen_y)
        return 0 <= grid_x < self.width and 0 <= grid_y < self.height

    def draw(self, surface):
        for x in range(self.width + 1):
            start = self.grid_to_screen(x, 0)
            end = self.grid_to_screen(x, self.height)
            pygame.draw.line(surface, (0, 0, 0), start, end, 2)

        for y in range(self.height + 1):
            start = self.grid_to_screen(0, y)
            end = self.grid_to_screen(self.width, y)
            pygame.draw.line(surface, (0, 0, 0), start, end, 2)

        if self.highlighted_cell:
            self.highlight_cell(surface, *self.highlighted_cell, (255, 255, 0, 100))

    def highlight_cell(self, surface, grid_x, grid_y, color):
        points = [
            self.grid_to_screen(grid_x, grid_y),
            self.grid_to_screen(grid_x + 1, grid_y),
            self.grid_to_screen(grid_x + 1, grid_y + 1),
            self.grid_to_screen(grid_x, grid_y + 1)
        ]
        pygame.draw.polygon(surface, color, points)

class BattlemapGridApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('DnD Isometric Grid App')
        self.window_size = (2520, 1080)  # Increased width for the new side window
        self.window_surface = pygame.display.set_mode(self.window_size)
        self.ui_manager = pygame_gui.UIManager(self.window_size)

        self.background = pygame.Surface(self.window_size)
        self.background.fill(self.ui_manager.ui_theme.get_colour('dark_bg'))
        self.is_dragging = False
        self.grid = None
        self.grid_surface = None
        self.battlemap = None
        self.resized_battlemap = None
        self.image_path = None
        self.load_battlemap_dialog = None
        self.save_session_dialog = None
        self.load_session_dialog = None

        self.tile_tags = {}
        self.active_tag = "floor"
        self.static_highlight = False

        self.show_labels = False
        self.label_colors = {
            "void": (128, 0, 128, 100),  # Purple
            "wall": (255, 0, 0, 100),    # Red
            "floor": (0, 255, 0, 100),   # Green
            "water": (0, 0, 255, 100)    # Blue
        }

        self.setup_ui()
        self.initialize_grid()
        self.starting_config = self.get_current_config()

        self.clock = pygame.time.Clock()
        self.is_running = True

    def setup_ui(self):
        panel_width = 600  # Increased panel width by 300 pixels
        slider_width = 180  # Reduced slider width
        label_width = 90  # Increased label width

        y_offset = 10
        self.load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset, (panel_width - 30) // 2, 30),
            text='Load Battlemap',
            manager=self.ui_manager
        )
        self.load_session_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20 + (panel_width - 30) // 2, y_offset, (panel_width - 30) // 2, 30),
            text='Load Session',
            manager=self.ui_manager
        )
        y_offset += 40
        self.save_session_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 30),
            text='Save Session',
            manager=self.ui_manager
        )
        y_offset += 40

        self.create_labeled_slider('Image Scale', 'image_scale', y_offset, slider_width, label_width, (10, 200), 100)
        y_offset += 70

        self.create_labeled_slider('Tile Size', 'tile_size', y_offset, slider_width, label_width, (1, 50), 10)
        y_offset += 70

        self.grid_size_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 20),
                                       text='Grid Size:',
                                       manager=self.ui_manager)
        y_offset += 30
        self.create_labeled_slider('Width', 'grid_size_x', y_offset, slider_width, label_width, (10, 200), 100)
        y_offset += 40
        self.create_labeled_slider('Height', 'grid_size_y', y_offset, slider_width, label_width, (10, 200), 100)
        y_offset += 70

        self.grid_origin_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 20),
                                         text='Grid Origin:',
                                         manager=self.ui_manager)
        y_offset += 30
        self.create_labeled_slider('X', 'grid_origin_x', y_offset, slider_width, label_width, (-1000, 1000), 0)
        y_offset += 40
        self.create_labeled_slider('Y', 'grid_origin_y', y_offset, slider_width, label_width, (-1000, 1000), 0)
        y_offset += 70

        self.create_labeled_slider('Iso Angle', 'isometric_angle', y_offset, slider_width, label_width, (1, 89), 30)
        y_offset += 70
        self.create_labeled_slider('Rotation', 'rotation', y_offset, slider_width, label_width, (-359, 359), 0)

        self.map_window = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(panel_width, 0, 
                                                                   self.window_size[0] - panel_width, 
                                                                   self.window_size[1]),
                                         image_surface=pygame.Surface((self.window_size[0] - panel_width, 
                                                                       self.window_size[1])),
                                         manager=self.ui_manager)
        # Add new side window for tile tagging
        tag_window_width = 300
        self.tag_window = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.window_size[0] - tag_window_width, 0, tag_window_width, self.window_size[1]),
            manager=self.ui_manager
        )

        # Add tile tag buttons
        button_height = 50
        y_offset = 10
        self.tag_buttons = {}
        for tag in ["floor", "water", "wall", "void", "None"]:
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10, y_offset, tag_window_width - 20, button_height),
                text=tag.capitalize(),
                manager=self.ui_manager,
                container=self.tag_window
            )
            self.tag_buttons[tag] = button
            y_offset += button_height + 10

        # Add reset dictionary button
        y_offset += 20  # Extra spacing
        self.reset_dict_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset, tag_window_width - 20, button_height),
            text='Reset All Labels',
            manager=self.ui_manager,
            container=self.tag_window
        )

        # Add remove image and reset battlemap buttons
        button_width = 200
        button_height = 40
        x_offset = 10
        y_offset = self.window_size[1] - 50  # 50 pixels from bottom

        self.remove_image_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x_offset, y_offset, button_width, button_height),
            text='Remove Image',
            manager=self.ui_manager
        )

        x_offset += button_width + 10
        self.reset_battlemap_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x_offset, y_offset, button_width, button_height),
            text='Reset Battlemap',
            manager=self.ui_manager
        )
        #
         # Add toggle button for label visualization
        self.toggle_labels_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, self.window_size[1] - 100, 280, 40),
            text='Toggle Label Visualization',
            manager=self.ui_manager,
            container=self.tag_window
        )

    def create_labeled_slider(self, label, attr_name, y_offset, slider_width, label_width, value_range, start_value):
        setattr(self, f'{attr_name}_label', pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, label_width, 20),
            text=f'{label}:',
            manager=self.ui_manager
        ))
        setattr(self, f'{attr_name}_slider', pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(10 + label_width, y_offset, slider_width, 20),
            start_value=start_value,
            value_range=value_range,
            manager=self.ui_manager
        ))
        setattr(self, f'{attr_name}_input', pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(20 + label_width + slider_width, y_offset, 50, 20),
            manager=self.ui_manager
        ))
        getattr(self, f'{attr_name}_input').set_text(str(start_value))

    def initialize_grid(self):
        map_rect = self.map_window.get_relative_rect()
        initial_tile_size = max(map_rect.width, map_rect.height) // 100
        self.tile_size_slider.set_current_value(initial_tile_size)
        self.tile_size_input.set_text(str(initial_tile_size))
        grid_width = map_rect.width // initial_tile_size
        grid_height = map_rect.height // initial_tile_size
        self.grid_size_x_slider.set_current_value(grid_width)
        self.grid_size_x_input.set_text(str(grid_width))
        self.grid_size_y_slider.set_current_value(grid_height)
        self.grid_size_y_input.set_text(str(grid_height))
        self.grid = IsometricGrid(grid_width, grid_height, initial_tile_size, (map_rect.width, map_rect.height))
        self.update_grid_surface()

    def update_grid_surface(self):
        if self.grid:
            self.grid_surface = pygame.Surface(self.map_window.get_relative_rect().size, pygame.SRCALPHA)
            if self.resized_battlemap:
                self.grid_surface.blit(self.resized_battlemap, (0, 0))
            self.grid.draw(self.grid_surface)

            if self.show_labels:
                self.draw_labeled_cells()

            self.map_window.set_image(self.grid_surface)

    def draw_labeled_cells(self):
        for (grid_x, grid_y), tag in self.tile_tags.items():
            if tag in self.label_colors:
                color = self.label_colors[tag]
                points = [
                    self.grid.grid_to_screen(grid_x, grid_y),
                    self.grid.grid_to_screen(grid_x + 1, grid_y),
                    self.grid.grid_to_screen(grid_x + 1, grid_y + 1),
                    self.grid.grid_to_screen(grid_x, grid_y + 1)
                ]
                pygame.draw.polygon(self.grid_surface, color, points)
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.load_button:
                    self.load_battlemap()
                elif event.ui_element == self.save_session_button:
                    self.save_session()
                elif event.ui_element == self.load_session_button:
                    self.load_session()
                elif event.ui_element in self.tag_buttons.values():
                    self.active_tag = [tag for tag, button in self.tag_buttons.items() if button == event.ui_element][0]
                elif event.ui_element == self.reset_dict_button:
                    self.reset_tile_tags()
                elif event.ui_element == self.remove_image_button:
                    self.remove_image()
                elif event.ui_element == self.reset_battlemap_button:
                    self.initialize_grid()
                elif event.ui_element == self.toggle_labels_button:
                    self.show_labels = not self.show_labels
                    self.update_grid_surface()

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                self.update_slider_value(event.ui_element)
                self.update_grid()

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                self.update_input_value(event.ui_element)
                self.update_grid()

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                if event.ui_element == self.load_battlemap_dialog:
                    self.battlemap = pygame.image.load(event.text).convert_alpha()
                    self.image_path = event.text
                    self.update_battlemap_image()
                elif event.ui_element == self.save_session_dialog:
                    self.save_session_to_file(event.text)
                elif event.ui_element == self.load_session_dialog:
                    self.load_session_from_file(event.text)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.is_dragging = True
                    self.handle_left_click(event.pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(event.pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.is_dragging = False

            if event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    self.handle_left_click(event.pos)
                elif not self.static_highlight:
                    self.handle_mouse_motion(event.pos)

            self.ui_manager.process_events(event)


    def handle_mouse_motion(self, mouse_pos):
        if self.grid:
            map_rect = self.map_window.get_relative_rect()
            iso_x, iso_y = mouse_pos[0] - map_rect.left, mouse_pos[1] - map_rect.top
            if map_rect.collidepoint(mouse_pos):
                grid_x, grid_y = self.grid.screen_to_grid(iso_x, iso_y)
                if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
                    self.grid.highlighted_cell = (grid_x, grid_y)
                else:
                    self.grid.highlighted_cell = None
            else:
                self.grid.highlighted_cell = None
            self.update_grid_surface()
    
    def handle_left_click(self, mouse_pos):
        if self.grid:
            map_rect = self.map_window.get_relative_rect()
            iso_x, iso_y = mouse_pos[0] - map_rect.left, mouse_pos[1] - map_rect.top
            if map_rect.collidepoint(mouse_pos):
                grid_x, grid_y = self.grid.screen_to_grid(iso_x, iso_y)
                if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
                    if self.active_tag == "None":
                        self.tile_tags.pop((grid_x, grid_y), None)
                    else:
                        self.tile_tags[(grid_x, grid_y)] = self.active_tag
                    self.grid.highlighted_cell = (grid_x, grid_y)
                    self.update_grid_surface()


    def handle_right_click(self, mouse_pos):
        self.static_highlight = not self.static_highlight
        if not self.static_highlight:
            self.handle_mouse_motion(mouse_pos)

    def load_battlemap(self):
        self.load_battlemap_dialog = UIFileDialog(
            rect=pygame.Rect(160, 50, 440, 500),
            manager=self.ui_manager,
            window_title='Load Battlemap...',
            initial_file_path='',
            allow_picking_directories=False,
            allow_existing_files_only=True,
            allowed_suffixes={".png", ".jpg", ".jpeg"}
        )
    def update_slider_value(self, slider):
        for attr in ['image_scale', 'tile_size', 'grid_size_x', 'grid_size_y', 'grid_origin_x', 'grid_origin_y', 'isometric_angle', 'rotation']:
            if slider == getattr(self, f'{attr}_slider'):
                value = int(slider.get_current_value())
                getattr(self, f'{attr}_input').set_text(str(value))
                if attr == 'image_scale' and self.battlemap:
                    self.update_battlemap_image()
                break

    def update_input_value(self, input_box):
        for attr in ['image_scale', 'tile_size', 'grid_size_x', 'grid_size_y', 'grid_origin_x', 'grid_origin_y', 'isometric_angle', 'rotation']:
            if input_box == getattr(self, f'{attr}_input'):
                try:
                    value = int(input_box.get_text())
                    getattr(self, f'{attr}_slider').set_current_value(value)
                    if attr == 'image_scale' and self.battlemap:
                        self.update_battlemap_image()
                except ValueError:
                    input_box.set_text(str(getattr(self, f'{attr}_slider').get_current_value()))
                break

    def update_grid(self):
        if self.grid:
            self.grid_surface = pygame.Surface(self.map_window.get_relative_rect().size, pygame.SRCALPHA)
            if self.resized_battlemap:
                self.grid_surface.blit(self.resized_battlemap, (0, 0))
            self.grid.draw(self.grid_surface)
            self.map_window.set_image(self.grid_surface)
        
        config = self.get_current_config()
        map_rect = self.map_window.get_relative_rect()
        self.grid = IsometricGrid(config.grid_size_x, config.grid_size_y, config.tile_size, 
                                  (map_rect.width, map_rect.height), 
                                  origin=(config.grid_origin_x, config.grid_origin_y),
                                  isometric_angle=config.isometric_angle,
                                  rotation=config.rotation)
        self.update_grid_surface()

    def update_battlemap_image(self):
        if self.battlemap:
            scale = self.image_scale_slider.get_current_value() / 100
            original_size = self.battlemap.get_size()
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            self.resized_battlemap = pygame.transform.smoothscale(self.battlemap, new_size)
            self.update_grid_surface()
            print("Battlemap image updated")  # Debug print

    

    def get_current_config(self) -> GridConfig:
        return GridConfig(
            tile_size=int(self.tile_size_slider.get_current_value()),
            grid_size_x=int(self.grid_size_x_slider.get_current_value()),
            grid_size_y=int(self.grid_size_y_slider.get_current_value()),
            grid_origin_x=int(self.grid_origin_x_slider.get_current_value()),
            grid_origin_y=int(self.grid_origin_y_slider.get_current_value()),
            isometric_angle=self.isometric_angle_slider.get_current_value(),
            rotation=self.rotation_slider.get_current_value(),
            image_path=self.image_path,
            image_scale=int(self.image_scale_slider.get_current_value()),
            tile_tags={f"{k[0]},{k[1]}": v for k, v in self.tile_tags.items()}
        )


    def save_session(self):
        self.save_session_dialog = UIFileDialog(
            rect=pygame.Rect(160, 50, 440, 500),
            manager=self.ui_manager,
            window_title='Save Session...',
            initial_file_path='',
            allow_picking_directories=False,
            allow_existing_files_only=False,
        )

    def load_session(self):
        self.load_session_dialog = UIFileDialog(
            rect=pygame.Rect(160, 50, 440, 500),
            manager=self.ui_manager,
            window_title='Load Session...',
            initial_file_path='',
            allow_picking_directories=False,
            allow_existing_files_only=True,
        )

    def save_session_to_file(self, file_path):
        config = self.get_current_config()
        try:
            config.save(file_path)
            print(f"Session saved to {file_path}")
        except Exception as e:
            print(f"Error saving session: {str(e)}")

    def load_session_from_file(self, file_path):
        try:
            config = GridConfig.load(file_path)
            self.apply_config(config)
            print(f"Session loaded from {file_path}")
            print(f"Loaded tile tags: {config.tile_tags}")  # Debug print
            print(f"Loaded image path: {config.image_path}")  # Debug print
        except Exception as e:
            print(f"Error loading session: {str(e)}")

    def reset_tile_tags(self):
        self.tile_tags.clear()
        self.update_grid_surface()

    def remove_image(self):
        self.battlemap = None
        self.resized_battlemap = None
        self.image_path = None
        self.update_grid_surface()

    def reset_battlemap(self):
        map_rect = self.map_window.get_relative_rect()
        self.grid_origin_x_slider.set_current_value(0)
        self.grid_origin_y_slider.set_current_value(0)
        self.isometric_angle_slider.set_current_value(30)
        self.rotation_slider.set_current_value(0)
        self.grid = IsometricGrid(self.grid.width, self.grid.height, self.grid.tile_size,
                                  (map_rect.width, map_rect.height),
                                  origin=(0, 0), isometric_angle=30, rotation=0)
        self.update_grid_surface()
    
    def apply_config(self, config):
        self.tile_size_slider.set_current_value(config.tile_size)
        self.tile_size_input.set_text(str(config.tile_size))
        self.grid_size_x_slider.set_current_value(config.grid_size_x)
        self.grid_size_x_input.set_text(str(config.grid_size_x))
        self.grid_size_y_slider.set_current_value(config.grid_size_y)
        self.grid_size_y_input.set_text(str(config.grid_size_y))
        self.grid_origin_x_slider.set_current_value(config.grid_origin_x)
        self.grid_origin_x_input.set_text(str(config.grid_origin_x))
        self.grid_origin_y_slider.set_current_value(config.grid_origin_y)
        self.grid_origin_y_input.set_text(str(config.grid_origin_y))
        self.isometric_angle_slider.set_current_value(config.isometric_angle)
        self.isometric_angle_input.set_text(str(config.isometric_angle))
        self.rotation_slider.set_current_value(config.rotation)
        self.rotation_input.set_text(str(config.rotation))
        self.image_scale_slider.set_current_value(config.image_scale)
        self.image_scale_input.set_text(str(config.image_scale))

        self.tile_tags = config.tile_tags
        print(f"Applied tile tags: {self.tile_tags}")  # Debug print

        if config.image_path and os.path.exists(config.image_path):
            self.battlemap = pygame.image.load(config.image_path).convert_alpha()
            self.image_path = config.image_path
            self.update_battlemap_image()
        else:
            print(f"Image not found or path is empty: {config.image_path}")  # Debug print

        self.update_grid()

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.ui_manager.update(time_delta)

            self.window_surface.blit(self.background, (0, 0))
            self.ui_manager.draw_ui(self.window_surface)
            
            if self.grid:
                if self.grid_surface:
                    self.window_surface.blit(self.grid_surface, (600, 0))
                if self.grid.highlighted_cell:
                    font = pygame.font.Font(None, 36)
                    pos_text = font.render(f"Pos: {self.grid.highlighted_cell}", True, (255, 255, 255))
                    tag = self.tile_tags.get(self.grid.highlighted_cell, "None")
                    tag_text = font.render(f"Tag: {tag}", True, (255, 255, 255))
                    self.window_surface.blit(pos_text, (self.window_size[0] - pos_text.get_width() - 310, 10))
                    self.window_surface.blit(tag_text, (self.window_size[0] - tag_text.get_width() - 310, 50))

            pygame.display.update()

if __name__ == "__main__":
    app = BattlemapGridApp()
    app.run()
