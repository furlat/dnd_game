import math
import json
from pydantic import BaseModel, computed_field
from typing import Tuple, Dict, Union, Optional
import pygame


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
    entity_tags: Dict[Union[Tuple[int, int], str], str] = {}
    is_bound: bool = False
    image_offset_x: int = 0
    image_offset_y: int = 0
    show_terrain_labels: bool = False
    show_entity_labels: bool = False

    @computed_field
    def image_offset(self) -> Tuple[int, int]:
        return (self.image_offset_x, self.image_offset_y) if self.is_bound else (0, 0)

    def save(self, file_path: str):
        data = self.model_dump()
        # Convert all keys to strings for JSON serialization
        data['tile_tags'] = {f"{k[0]},{k[1]}" if isinstance(k, tuple) else k: v
                             for k, v in self.tile_tags.items()}
        data['entity_tags'] = {f"{k[0]},{k[1]}" if isinstance(k, tuple) else k: v
                               for k, v in self.entity_tags.items()}
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Convert string keys to tuples for tile_tags
        if 'tile_tags' in data:
            tile_tags = {}
            for k, v in data['tile_tags'].items():
                try:
                    key_parts = k.split(',')
                    if len(key_parts) == 2:
                        x, y = int(key_parts[0]), int(key_parts[1])
                        tile_tags[(x, y)] = v
                    else:
                        tile_tags[k] = v
                except ValueError:
                    tile_tags[k] = v
            data['tile_tags'] = tile_tags

        # Convert string keys to tuples for entity_tags
        if 'entity_tags' in data:
            entity_tags = {}
            for k, v in data['entity_tags'].items():
                try:
                    key_parts = k.split(',')
                    if len(key_parts) == 2:
                        x, y = int(key_parts[0]), int(key_parts[1])
                        entity_tags[(x, y)] = v
                    else:
                        entity_tags[k] = v
                except ValueError:
                    entity_tags[k] = v
            data['entity_tags'] = entity_tags
        else:
            data['entity_tags'] = {}  # Default to empty dict if not present in old saves

        # Set default values for new fields if they're not in the loaded data
        data.setdefault('is_bound', False)
        data.setdefault('image_offset_x', 0)
        data.setdefault('image_offset_y', 0)
        data.setdefault('show_terrain_labels', False)
        data.setdefault('show_entity_labels', False)

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
        # Calculate the total width and height of the grid in isometric space
        self.iso_width = (self.width + self.height) * math.cos(self.isometric_angle) * self.tile_size
        self.iso_height = (self.width + self.height) * math.sin(self.isometric_angle) * self.tile_size

    def grid_to_screen(self, grid_x, grid_y):
        # Apply isometric transformation
        iso_x = (grid_x - grid_y) * math.cos(self.isometric_angle)
        iso_y = (grid_x + grid_y) * math.sin(self.isometric_angle)

        # Apply rotation
        rotated_x = iso_x * math.cos(self.rotation) - iso_y * math.sin(self.rotation)
        rotated_y = iso_x * math.sin(self.rotation) + iso_y * math.cos(self.rotation)

        # Convert to screen position
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

        # Return precise grid coordinates
        return int(grid_x), int(grid_y)

    def is_in_grid(self, screen_x, screen_y):
        grid_x, grid_y = self.screen_to_grid(screen_x, screen_y)
        return 0 <= grid_x < self.width and 0 <= grid_y < self.height

    def draw(self, surface):
        # Draw the vertical lines of the grid
        for x in range(self.width + 1):
            start = self.grid_to_screen(x, 0)
            end = self.grid_to_screen(x, self.height)
            pygame.draw.line(surface, (0, 0, 0), start, end, 2)

        # Draw the horizontal lines of the grid
        for y in range(self.height + 1):
            start = self.grid_to_screen(0, y)
            end = self.grid_to_screen(self.width, y)
            pygame.draw.line(surface, (0, 0, 0), start, end, 2)

        # Highlight the currently selected cell, if any
        if self.highlighted_cell:
            self.highlight_cell(surface, *self.highlighted_cell, (255, 255, 0, 100))

    def highlight_cell(self, surface, grid_x, grid_y, color):
        # Calculate the corners of the cell in screen coordinates
        points = [
            self.grid_to_screen(grid_x, grid_y),
            self.grid_to_screen(grid_x + 1, grid_y),
            self.grid_to_screen(grid_x + 1, grid_y + 1),
            self.grid_to_screen(grid_x, grid_y + 1)
        ]
        # Draw a polygon highlighting the cell
        pygame.draw.polygon(surface, color, points)
