import pygame
import pygame_gui
from isometric_map import IsometricGrid, GridConfig

class BattlemapWindow:
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

    def update_grid_surface(self, tile_tags):
        if self.grid:
            self.grid_surface = pygame.Surface(self.map_window.get_relative_rect().size, pygame.SRCALPHA)
            if self.resized_battlemap:
                self.grid_surface.blit(self.resized_battlemap, (0, 0))
            self.grid.draw(self.grid_surface)

            if self.show_labels:
                self.draw_labeled_cells(tile_tags)

            self.map_window.set_image(self.grid_surface)

    def draw_labeled_cells(self, tile_tags):
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

    def update_battlemap_image(self, scale):
        if self.battlemap:
            original_size = self.battlemap.get_size()
            new_size = (int(original_size[0] * scale / 100), int(original_size[1] * scale / 100))
            self.resized_battlemap = pygame.transform.smoothscale(self.battlemap, new_size)

    def draw(self):
        self.window_surface.blit(self.background, (0, 0))
        self.ui_manager.draw_ui(self.window_surface)
        
        if self.grid:
            if self.grid_surface:
                self.window_surface.blit(self.grid_surface, (600, 0))
            if self.grid.highlighted_cell:
                font = pygame.font.Font(None, 36)
                pos_text = font.render(f"Pos: {self.grid.highlighted_cell}", True, (255, 255, 255))
                self.window_surface.blit(pos_text, (self.window_size[0] - pos_text.get_width() - 310, 10))

        pygame.display.update()