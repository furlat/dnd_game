import pygame
import pygame_gui

class BattlemapDrawing:
    def __init__(self, window_size):
        self.window_size = window_size
        self.window_surface = pygame.display.set_mode(self.window_size)
        self.ui_manager = pygame_gui.UIManager(self.window_size)
        self.background = pygame.Surface(self.window_size)
        self.background.fill(self.ui_manager.ui_theme.get_colour('dark_bg'))
        
        self.grid = None
        self.grid_surface = None
        self.battlemap = None
        self.resized_battlemap = None

        self.show_labels = False
        self.label_colors = {
            "void": (128, 0, 128, 100),  # Purple
            "wall": (255, 0, 0, 100),    # Red
            "floor": (0, 255, 0, 100),   # Green
            "water": (0, 0, 255, 100)    # Blue
        }

        self.map_window = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(600, 0, self.window_size[0] - 600, self.window_size[1]),
            image_surface=pygame.Surface((self.window_size[0] - 600, self.window_size[1])),
            manager=self.ui_manager
        )
        self.image_offset = (0, 0)
        self.show_terrain_labels = False
        self.show_entity_labels = False
        self.entity_sprites = {}  # Add this line to store entity sprites

    def update_battlemap_image(self, scale, offset=(0, 0)):
        if self.battlemap:
            original_size = self.battlemap.get_size()
            new_size = (int(original_size[0] * scale / 100), int(original_size[1] * scale / 100))
            self.resized_battlemap = pygame.transform.smoothscale(self.battlemap, new_size)
            self.image_offset = offset

    def update_grid_surface(self, tile_tags, entity_tags):
        if self.grid:
            self.grid_surface = pygame.Surface(self.map_window.get_relative_rect().size, pygame.SRCALPHA)
            if self.resized_battlemap:
                self.grid_surface.blit(self.resized_battlemap, self.image_offset)
            self.grid.draw(self.grid_surface)

            if self.show_terrain_labels:
                self.draw_terrain_labels(tile_tags)
            if self.show_entity_labels:
                self.draw_entity_labels(entity_tags)

            self.map_window.set_image(self.grid_surface)

    def draw_terrain_labels(self, tile_tags):
        for (grid_x, grid_y), tag in tile_tags.items():
            if tag in self.label_colors:
                color = self.label_colors[tag]
                points = [
                    self.grid.grid_to_screen(grid_x, grid_y),
                    self.grid.grid_to_screen(grid_x + 1, grid_y),
                    self.grid.grid_to_screen(grid_x + 1, grid_y + 1),
                    self.grid.grid_to_screen(grid_x, grid_y + 1)
                ]
                pygame.draw.polygon(self.grid_surface, color, points)
    
    def draw_entity_labels(self, entity_tags):
        for (grid_x, grid_y), entity in entity_tags.items():
            if entity in self.entity_sprites:
                sprite = self.entity_sprites[entity]
                
                # Calculate tile dimensions
                tile_width = self.grid.tile_size

                # Resize sprite to a percentage of the tile size
                entity_height = tile_width*1.6  # 150% of tile height
                aspect_ratio = sprite.get_width() / sprite.get_height()
                entity_width = int(entity_height * aspect_ratio)
                resized_sprite = pygame.transform.smoothscale(sprite, (entity_width, entity_height))
                
                # Calculate position (feet at the center of the tile)
                center_x, center_y = self.grid.grid_to_screen(grid_x+0.9, grid_y + 0.9)
                sprite_rect = resized_sprite.get_rect(midbottom=(center_x, center_y))
                
                self.grid_surface.blit(resized_sprite, sprite_rect)


    def draw(self, tile_tags, entity_tags):
        self.window_surface.blit(self.background, (0, 0))
        self.ui_manager.draw_ui(self.window_surface)
        
        if self.grid:
            if self.grid_surface:
                self.window_surface.blit(self.grid_surface, (600, 0))
            if self.grid.highlighted_cell:
                font = pygame.font.Font(None, 36)
                pos_text = font.render(f"Pos: {self.grid.highlighted_cell}", True, (255, 255, 255))
                terrain_tag = tile_tags.get(self.grid.highlighted_cell, "None")
                entity_tag = entity_tags.get(self.grid.highlighted_cell, "None")
                terrain_text = font.render(f"Terrain: {terrain_tag}", True, (255, 255, 255))
                entity_text = font.render(f"Entity: {entity_tag}", True, (255, 255, 255))
                self.window_surface.blit(pos_text, (self.window_size[0] - pos_text.get_width() - 310, 10))
                self.window_surface.blit(terrain_text, (self.window_size[0] - terrain_text.get_width() - 310, 50))
                self.window_surface.blit(entity_text, (self.window_size[0] - entity_text.get_width() - 310, 90))

        pygame.display.update()

    def set_entity_sprites(self, entity_sprites):
        self.entity_sprites = entity_sprites