import pygame
import pygame_gui
from pygame_gui.windows import UIFileDialog
import os
from isometric_map import GridConfig, IsometricGrid
from battlemap_drawing import BattlemapDrawing
from grid_config_window import GridConfigWindow
from grid_labels_window import GridLabelsWindow

class BattlemapGridApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('DnD Isometric Grid App')
        self.image_offset = [0, 0]
        self.initial_grid_origin = [0, 0]
        self.window_size = (2520, 1080)
        self.drawing = BattlemapDrawing(self.window_size)
        self.is_dragging = False
        self.image_path = None
        self.load_battlemap_dialog = None
        self.save_session_dialog = None
        self.load_session_dialog = None

        self.tile_tags = {}
        self.entity_tags = {}
        self.entity_sprites = {}
        self.static_highlight = False

        self.setup_ui()
        self.initialize_grid()
        self.starting_config = self.get_current_config()

        self.clock = pygame.time.Clock()
        self.is_running = True

        



    def setup_ui(self):
        # Create a panel for load/save buttons
        top_panel_height = 100
        top_panel_rect = pygame.Rect(0, 0, 600, top_panel_height)
        self.top_panel = pygame_gui.elements.UIPanel(
            relative_rect=top_panel_rect,
            manager=self.drawing.ui_manager
        )

        # Add load/save buttons to the top panel
        button_width = 280
        button_height = 30
        spacing = 10
        self.load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(spacing, spacing, button_width, button_height),
            text='Load Battlemap',
            manager=self.drawing.ui_manager,
            container=self.top_panel
        )
        self.load_session_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_width + spacing * 2, spacing, button_width, button_height),
            text='Load Session',
            manager=self.drawing.ui_manager,
            container=self.top_panel
        )
        self.save_session_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(spacing, button_height + spacing * 2, button_width * 2 + spacing, button_height),
            text='Save Session',
            manager=self.drawing.ui_manager,
            container=self.top_panel
        )

        # Create grid config window below the top panel
        config_window_rect = pygame.Rect(0, top_panel_height, 600, self.window_size[1] - top_panel_height)
        self.config_window = GridConfigWindow(self.drawing.ui_manager, config_window_rect)

        # Create labels window on the right side
        labels_window_rect = pygame.Rect(self.window_size[0] - 300, 0, 300, self.window_size[1])
        self.labels_window = GridLabelsWindow(self.drawing.ui_manager, labels_window_rect)

        # Add remove image and reset battlemap buttons at the bottom of the config window
        button_width = 280
        button_height = 40
        spacing = 10
        bottom_y = self.window_size[1] - button_height - spacing

        self.remove_image_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(spacing, bottom_y, button_width, button_height),
            text='Remove Image',
            manager=self.drawing.ui_manager
        )

        self.reset_battlemap_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_width + spacing * 2, bottom_y, button_width, button_height),
            text='Reset Battlemap',
            manager=self.drawing.ui_manager
        )

    def initialize_grid(self):
        map_rect = self.drawing.map_window.get_relative_rect()
        config = self.config_window.get_config()
        self.drawing.grid = IsometricGrid(config['grid_size_x'], config['grid_size_y'], config['tile_size'],
                                          (map_rect.width, map_rect.height))
        self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                self.handle_button_press(event)

            config_update = self.config_window.handle_event(event)
            if config_update:
                if config_update == 'bind_toggled':
                    self.handle_bind_toggle()
                elif config_update in ['grid_origin_x', 'grid_origin_y']:
                    self.handle_grid_origin_change(config_update)
                self.update_grid()

            label_update = self.labels_window.handle_event(event)
            if label_update:
                self.handle_label_update(label_update)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                self.handle_file_dialog(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.is_dragging = False

            if event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)

            self.drawing.ui_manager.process_events(event)

    def handle_button_press(self, event):
        if event.ui_element == self.load_button:
            self.load_battlemap()
        elif event.ui_element == self.save_session_button:
            self.save_session()
        elif event.ui_element == self.load_session_button:
            self.load_session()
        elif event.ui_element == self.remove_image_button:
            self.remove_image()
        elif event.ui_element == self.reset_battlemap_button:
            self.initialize_grid()

    def handle_bind_toggle(self):
        config = self.config_window.get_config()
        if config['is_bound']:
            self.initial_grid_origin = [config['grid_origin_x'], config['grid_origin_y']]
        else:
            self.initial_grid_origin = [config['grid_origin_x'], config['grid_origin_y']]
        self.update_battlemap_image()

    def handle_grid_origin_change(self, changed_axis):
        config = self.config_window.get_config()
        if config['is_bound']:
            new_x = config['grid_origin_x']
            new_y = config['grid_origin_y']
            if changed_axis == 'grid_origin_x':
                delta = new_x - self.initial_grid_origin[0]
                self.image_offset[0] += delta
                self.initial_grid_origin[0] = new_x
            elif changed_axis == 'grid_origin_y':
                delta = new_y - self.initial_grid_origin[1]
                self.image_offset[1] += delta
                self.initial_grid_origin[1] = new_y
            self.update_battlemap_image()

    def update_grid(self):
        config = self.config_window.get_config()
        map_rect = self.drawing.map_window.get_relative_rect()
        self.drawing.grid = IsometricGrid(config['grid_size_x'], config['grid_size_y'], config['tile_size'], 
                                  (map_rect.width, map_rect.height), 
                                  origin=(config['grid_origin_x'], config['grid_origin_y']),
                                  isometric_angle=config['isometric_angle'],
                                  rotation=config['rotation'])
        self.update_battlemap_image()

    def update_battlemap_image(self):
        config = self.config_window.get_config()
        scale = config['image_scale']
        offset = tuple(self.image_offset) if config['is_bound'] else (0, 0)
        self.drawing.update_battlemap_image(scale, offset)
        self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)



    def handle_label_update(self, update_type):
        if update_type == 'reset_labels':
            self.reset_tile_tags()
        elif update_type == 'toggle_terrain_labels':
            self.drawing.show_terrain_labels = self.labels_window.show_terrain_labels
            self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)
        elif update_type == 'toggle_entity_labels':
            self.drawing.show_entity_labels = self.labels_window.show_entity_labels
            self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)
        elif update_type == 'remove_all_entities':
            self.entity_tags.clear()
            self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)
    def handle_file_dialog(self, event):
        if event.ui_element == self.load_battlemap_dialog:
            self.drawing.battlemap = pygame.image.load(event.text).convert_alpha()
            self.image_path = event.text
            self.update_battlemap_image()
        elif event.ui_element == self.save_session_dialog:
            self.save_session_to_file(event.text)
        elif event.ui_element == self.load_session_dialog:
            self.load_session_from_file(event.text)

    def handle_mouse_down(self, event):
        if event.button == 1:  # Left click
            self.is_dragging = True
            self.handle_left_click(event.pos)
        elif event.button == 3:  # Right click
            self.handle_right_click(event.pos)

    def handle_mouse_motion(self, event):
        if self.is_dragging:
            self.handle_left_click(event.pos)
        elif not self.static_highlight:
            self.handle_mouse_hover(event.pos)

    def handle_left_click(self, mouse_pos):
        if self.drawing.grid:
            map_rect = self.drawing.map_window.get_relative_rect()
            iso_x, iso_y = mouse_pos[0] - map_rect.left, mouse_pos[1] - map_rect.top
            if map_rect.collidepoint(mouse_pos):
                grid_x, grid_y = self.drawing.grid.screen_to_grid(iso_x, iso_y)
                if 0 <= grid_x < self.drawing.grid.width and 0 <= grid_y < self.drawing.grid.height:
                    active_tag = self.labels_window.get_active_tag()
                    active_entity = self.labels_window.get_active_entity()
                    if active_tag != "None":
                        self.tile_tags[(grid_x, grid_y)] = active_tag
                    else:
                        self.tile_tags.pop((grid_x, grid_y), None)
                    
                    if active_entity != "None":
                        self.entity_tags[(grid_x, grid_y)] = active_entity
                        if active_entity not in self.entity_sprites:
                            sprite_path = self.labels_window.entity_dict[active_entity]
                            if sprite_path:
                                self.entity_sprites[active_entity] = pygame.image.load(sprite_path).convert_alpha()
                    else:
                        self.entity_tags.pop((grid_x, grid_y), None)
                    
                    self.drawing.grid.highlighted_cell = (grid_x, grid_y)
                    self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)

    def handle_right_click(self, mouse_pos):
        self.static_highlight = not self.static_highlight
        if not self.static_highlight:
            self.handle_mouse_hover(mouse_pos)

    def handle_mouse_hover(self, mouse_pos):
        if self.drawing.grid:
            map_rect = self.drawing.map_window.get_relative_rect()
            iso_x, iso_y = mouse_pos[0] - map_rect.left, mouse_pos[1] - map_rect.top
            if map_rect.collidepoint(mouse_pos):
                grid_x, grid_y = self.drawing.grid.screen_to_grid(iso_x, iso_y)
                if 0 <= grid_x < self.drawing.grid.width and 0 <= grid_y < self.drawing.grid.height:
                    self.drawing.grid.highlighted_cell = (grid_x, grid_y)
                else:
                    self.drawing.grid.highlighted_cell = None
            else:
                self.drawing.grid.highlighted_cell = None
            self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)

 

 

    def get_current_config(self):
        config = self.config_window.get_config()
        return GridConfig(
            tile_size=config['tile_size'],
            grid_size_x=config['grid_size_x'],
            grid_size_y=config['grid_size_y'],
            grid_origin_x=config['grid_origin_x'],
            grid_origin_y=config['grid_origin_y'],
            isometric_angle=config['isometric_angle'],
            rotation=config['rotation'],
            image_path=self.image_path,
            image_scale=config['image_scale'],
            tile_tags=self.tile_tags,
            entity_tags=self.entity_tags,
            is_bound=config['is_bound'],
            image_offset_x=self.image_offset[0],
            image_offset_y=self.image_offset[1],
            show_terrain_labels=self.drawing.show_terrain_labels,
            show_entity_labels=self.drawing.show_entity_labels
        )

    def apply_config(self, config):
        self.config_window.set_config({
            'tile_size': config.tile_size,
            'grid_size_x': config.grid_size_x,
            'grid_size_y': config.grid_size_y,
            'grid_origin_x': config.grid_origin_x,
            'grid_origin_y': config.grid_origin_y,
            'isometric_angle': config.isometric_angle,
            'rotation': config.rotation,
            'image_scale': config.image_scale,
            'is_bound': config.is_bound
        })

        self.tile_tags = config.tile_tags
        self.entity_tags = config.entity_tags
        self.image_offset = [config.image_offset_x, config.image_offset_y]
        self.initial_grid_origin = [config.grid_origin_x, config.grid_origin_y]
        self.drawing.show_terrain_labels = config.show_terrain_labels
        self.drawing.show_entity_labels = config.show_entity_labels

        if config.image_path and os.path.exists(config.image_path):
            self.drawing.battlemap = pygame.image.load(config.image_path).convert_alpha()
            self.image_path = config.image_path
            self.update_battlemap_image()
        else:
            print(f"Image not found or path is empty: {config.image_path}")

        self.load_entity_sprites()
        self.update_grid()
    
    def load_entity_sprites(self):
        for entity in set(self.entity_tags.values()):
            if entity not in self.entity_sprites:
                sprite_path = self.labels_window.entity_dict.get(entity)
                if sprite_path:
                    self.entity_sprites[entity] = pygame.image.load(sprite_path).convert_alpha()
        self.drawing.set_entity_sprites(self.entity_sprites)  # Add this line


    def load_battlemap(self):
        self.load_battlemap_dialog = UIFileDialog(
            rect=pygame.Rect(160, 50, 440, 500),
            manager=self.drawing.ui_manager,
            window_title='Load Battlemap...',
            initial_file_path='',
            allow_picking_directories=False,
            allow_existing_files_only=True,
            allowed_suffixes={".png", ".jpg", ".jpeg"}
        )

    def save_session(self):
        self.save_session_dialog = UIFileDialog(
            rect=pygame.Rect(160, 50, 440, 500),
            manager=self.drawing.ui_manager,
            window_title='Save Session...',
            initial_file_path='',
            allow_picking_directories=False,
            allow_existing_files_only=False,
        )

    def load_session(self):
        self.load_session_dialog = UIFileDialog(
            rect=pygame.Rect(160, 50, 440, 500),
            manager=self.drawing.ui_manager,
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
        except Exception as e:
            print(f"Error loading session: {str(e)}")

    def reset_tile_tags(self):
        self.tile_tags.clear()
        self.entity_tags.clear()
        self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)


    def remove_image(self):
        self.drawing.battlemap = None
        self.drawing.resized_battlemap = None
        self.image_path = None
        self.drawing.update_grid_surface(self.tile_tags, self.entity_tags)


    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.drawing.ui_manager.update(time_delta)
            self.drawing.draw(self.tile_tags, self.entity_tags)