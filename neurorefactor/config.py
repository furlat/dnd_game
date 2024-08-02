from pydantic import BaseModel, Field
from typing import Dict, Tuple, List, Optional
import os

class WindowConfig(BaseModel):
    width: int = 1700
    height: int = 1020
    title: str = "NeuroDragon"

class UIConfig(BaseModel):
    battlemap_window: Dict[str, int] = Field(default_factory=lambda: {"left": 10, "top": 10, "width": 1052, "height": 800})
    details_window: Dict[str, int] = Field(default_factory=lambda: {"left": 1072, "top": 10, "width": 400, "height": 400})
    actions_window: Dict[str, int] = Field(default_factory=lambda: {"left": 1072, "top": 420, "width": 400, "height": 590})
    logger_window: Dict[str, int] = Field(default_factory=lambda: {"left": 10, "top": 820, "width": 1052, "height": 190})
    active_entity_window: Dict[str, int] = Field(default_factory=lambda: {"left": 1482, "top": 10, "width": 208, "height": 500})
    target_window: Dict[str, int] = Field(default_factory=lambda: {"left": 1482, "top": 520, "width": 208, "height": 490})
    
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
            'path_to_target': os.path.join(base_path, 'path_to_target.png')
        }
        return cls(base_path=base_path, paths=paths)

class TileConfig(BaseModel):
    ascii: Dict[str, str] = Field(default_factory=lambda: {'WALL': '#', 'FLOOR': '.'})

class EntityConfig(BaseModel):
    ascii: Dict[str, str] = Field(default_factory=lambda: {'Goblin': 'g', 'Skeleton': 's'})

class BattlemapConfig(BaseModel):
    width: int = 20
    height: int = 9
    default_map: str = '''
####################
#........#.........#
#...###..#....#....#
#...###..#....#....#
#...###..#....#....#
#........#....#....#
#.............#....#
#........#....#....#
####################
'''.strip()

    @classmethod
    def default_factory(cls) -> 'BattlemapConfig':
        return cls()

class GameRulesConfig(BaseModel):
    movement_cost: int = 5
    visibility_range: int = 8

class Config(BaseModel):
    window: WindowConfig = WindowConfig()
    ui: UIConfig = UIConfig()
    theme: ThemeConfig = ThemeConfig()
    sprites: SpriteConfig = Field(default_factory=SpriteConfig.default_factory)
    tiles: TileConfig = TileConfig()
    entities: EntityConfig = EntityConfig()
    battlemap: BattlemapConfig = Field(default_factory=BattlemapConfig.default_factory)
    game_rules: GameRulesConfig = GameRulesConfig()
    debug: bool = False

    @classmethod
    def default_factory(cls) -> 'Config':
        return cls()

# Global configuration object
config = Config.default_factory()

def load_config(file_path: str) -> Config:
    # TODO: Implement loading from a JSON or YAML file
    return config