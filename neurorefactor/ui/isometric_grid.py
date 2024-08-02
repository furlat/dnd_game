import json
from typing import Tuple, Dict, Union, Optional
from pydantic import BaseModel
import math

import json
from typing import Tuple, Dict, Union, Optional
from pydantic import BaseModel

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
    tile_tags: Dict[Tuple[int, int], str] = {}

    def save(self, file_path: str):
        """
        Save the grid configuration to a file.
        """
        data = self.dict()
        data['tile_tags'] = {f"{k[0]},{k[1]}": v for k, v in self.tile_tags.items()}  # Convert keys to strings
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Configuration saved to {file_path}")

    @classmethod
    def load(cls, file_path: str):
        """
        Load the grid configuration from a file.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        tile_tags = {}
        for k, v in data.get('tile_tags', {}).items():
            try:
                x, y = map(int, k.split(','))
                tile_tags[(x, y)] = v
            except ValueError:
                print(f"Skipping invalid tile tag key: {k}")

        data['tile_tags'] = tile_tags
        print(f"Configuration loaded from {file_path}")
        return cls(**data)


import math
import pygame

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
        """
        Convert grid coordinates to screen coordinates using the tile size from the save file.
        """
        iso_x = (grid_x - grid_y) * self.tile_size * math.cos(self.isometric_angle)
        iso_y = (grid_x + grid_y) * self.tile_size * math.sin(self.isometric_angle)
        
        rotated_x = iso_x * math.cos(self.rotation) - iso_y * math.sin(self.rotation)
        rotated_y = iso_x * math.sin(self.rotation) + iso_y * math.cos(self.rotation)
        
        screen_x = rotated_x + self.origin[0]
        screen_y = rotated_y + self.origin[1]
        return int(screen_x), int(screen_y)

    def screen_to_grid(self, screen_x, screen_y):
        """
        Convert screen coordinates back to grid coordinates.
        """
        translated_x = screen_x - self.origin[0]
        translated_y = screen_y - self.origin[1]
        
        unrotated_x = translated_x * math.cos(-self.rotation) - translated_y * math.sin(-self.rotation)
        unrotated_y = translated_x * math.sin(-self.rotation) + translated_y * math.cos(-self.rotation)
        
        scaled_x = unrotated_x / (self.tile_size * math.cos(self.isometric_angle))
        scaled_y = unrotated_y / (self.tile_size * math.sin(self.isometric_angle))
        
        grid_y = (scaled_y - scaled_x) / 2
        grid_x = scaled_y - grid_y
        
        return round(grid_x), round(grid_y)

    def draw(self, surface):
        """
        Draw the grid on a given surface using the correct tile size.
        """
        for x in range(self.width + 1):
            start = self.grid_to_screen(x, 0)
            end = self.grid_to_screen(x, self.height)
            pygame.draw.line(surface, (255, 255, 255), start, end, 1)

        for y in range(self.height + 1):
            start = self.grid_to_screen(0, y)
            end = self.grid_to_screen(self.width, y)
            pygame.draw.line(surface, (255, 255, 255), start, end, 1)

        if self.highlighted_cell:
            self.highlight_cell(surface, *self.highlighted_cell, (255, 255, 0, 100))

    def highlight_cell(self, surface, grid_x, grid_y, color):
        """
        Highlight a specific grid cell.
        """
        points = [
            self.grid_to_screen(grid_x, grid_y),
            self.grid_to_screen(grid_x + 1, grid_y),
            self.grid_to_screen(grid_x + 1, grid_y + 1),
            self.grid_to_screen(grid_x, grid_y + 1)
        ]
        pygame.draw.polygon(surface, color, points)
