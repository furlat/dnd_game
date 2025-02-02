from pydantic import BaseModel, Field
from typing import Dict, Tuple, List, Optional
import os

class WindowConfig(BaseModel):
    width: int = 2520
    height: int = 1080
    title: str = "NeuroDragon Isometric"

class UIConfig(BaseModel):
    battlemap_window: Dict[str, int] = Field(default_factory=lambda: {"left": 0, "top": 0, "width": 1620, "height": 1080})
    details_window: Dict[str, int] = Field(default_factory=lambda: {"left": 1620, "top": 0, "width": 300, "height": 540})
    actions_window: Dict[str, int] = Field(default_factory=lambda: {"left": 1620, "top": 540, "width": 300, "height": 540})
    logger_window: Dict[str, int] = Field(default_factory=lambda: {"left": 1920, "top": 0, "width": 600, "height": 1080})

class ThemeConfig(BaseModel):
    path: str = "assets/themes/theme.json"

class SpriteConfig(BaseModel):
    base_path: str = "assets/sprites"
    paths: Dict[str, str] = Field(default_factory=dict)
    size: Tuple[int, int] = (50, 50)

    @classmethod
    def default_factory(cls) -> 'SpriteConfig':
        base_path = "assets/sprites"
        paths = {
            'WALL': os.path.join(base_path, 'wall.png'),
            'FLOOR': os.path.join(base_path, 'floor.png'),
            'Goblin': os.path.join(base_path, 'goblin.png'),
            'Skeleton': os.path.join(base_path, 'skeleton.png'),
            'toggle_fov': os.path.join(base_path, 'toggle_fov.png'),
            'color_fov': os.path.join(base_path, 'color_fov.png'),
            'ray_to_target': os.path.join(base_path, 'ray_to_target.png'),
            'toggle_paths': os.path.join(base_path, 'toggle_paths.png'),
            'path_to_target': os.path.join(base_path, 'path_to_target.png'),
            'toggle_background': os.path.join(base_path, 'toggle_background.png'),
            'toggle_labels': os.path.join(base_path, 'toggle_labels.png'),
            'toggle_grid': os.path.join(base_path, 'toggle_grid.png'),
            'load_battlemap': os.path.join(base_path, 'load_battlemap.png')
        }
        return cls(base_path=base_path, paths=paths)

class TileConfig(BaseModel):
    ascii: Dict[str, str] = Field(default_factory=lambda: {'WALL': '#', 'FLOOR': '.'})

class EntityConfig(BaseModel):
    ascii: Dict[str, str] = Field(default_factory=lambda: {'Goblin': 'g', 'Skeleton': 's'})

class BattlemapConfig(BaseModel):
    width: int = 20
    height: int = 9

class GameRulesConfig(BaseModel):
    movement_cost: int = 5
    visibility_range: int = 8

class IsometricConfig(BaseModel):
    tile_size: int = 32
    isometric_angle: float = 30.0
    rotation: float = 0.0

class Config(BaseModel):
    window: WindowConfig = WindowConfig()
    ui: UIConfig = UIConfig()
    theme: ThemeConfig = ThemeConfig()
    sprites: SpriteConfig = Field(default_factory=SpriteConfig.default_factory)
    tiles: TileConfig = TileConfig()
    entities: EntityConfig = EntityConfig()
    battlemap: BattlemapConfig = BattlemapConfig()
    game_rules: GameRulesConfig = GameRulesConfig()
    isometric: IsometricConfig = IsometricConfig()
    debug: bool = False

config = Config()

def load_config(file_path: str) -> Config:
    # TODO: Implement loading from a JSON or YAML file
    return config