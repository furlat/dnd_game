import pygame
from typing import Tuple, List, Set
from neurorefactor.config import config
from dnd.battlemap import Entity

def draw_grid(surface: pygame.Surface, grid_size: Tuple[int, int], tile_size: int, offset: Tuple[int, int]):
    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            draw_x = (x - offset[0]) * tile_size
            draw_y = (y - offset[1]) * tile_size
            pygame.draw.rect(surface, (50, 50, 50), (draw_x, draw_y, tile_size, tile_size), 1)

def draw_ascii_char(surface: pygame.Surface, char: str, x: int, y: int, tile_size: int, font: pygame.font.Font, is_entity: bool = False):
    color = (255, 0, 0) if is_entity else (255, 255, 255)
    text_surface = font.render(char, True, color)
    text_rect = text_surface.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
    surface.blit(text_surface, text_rect)

def draw_fov_overlay(surface: pygame.Surface, visible_positions: Set[Tuple[int, int]], tile_size: int, offset: Tuple[int, int]):
    for x, y in visible_positions:
        draw_x = (x - offset[0]) * tile_size
        draw_y = (y - offset[1]) * tile_size
        color_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        color_surface.fill((255, 255, 0, 64))  # Semi-transparent yellow
        surface.blit(color_surface, (draw_x, draw_y))

def draw_path_overlay(surface: pygame.Surface, reachable_positions: Set[Tuple[int, int]], tile_size: int, offset: Tuple[int, int]):
    for x, y in reachable_positions:
        draw_x = (x - offset[0]) * tile_size
        draw_y = (y - offset[1]) * tile_size
        color_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        color_surface.fill((0, 255, 0, 64))  # Semi-transparent green
        surface.blit(color_surface, (draw_x, draw_y))

def draw_ray(surface: pygame.Surface, source_position: Tuple[int, int], ray: List[Tuple[int, int]], tile_size: int, offset: Tuple[int, int]):
    start_x = (source_position[0] - offset[0]) * tile_size + tile_size // 2
    start_y = (source_position[1] - offset[1]) * tile_size + tile_size // 2

    points = [(start_x, start_y)]
    for x, y in ray[1:]:
        draw_x = (x - offset[0]) * tile_size + tile_size // 2
        draw_y = (y - offset[1]) * tile_size + tile_size // 2
        points.append((draw_x, draw_y))

    if len(points) > 1:
        pygame.draw.lines(surface, (255, 255, 64), False, points, 2)

def draw_path(surface: pygame.Surface, path: List[Tuple[int, int]], movement_budget: int, visible_positions: Set[Tuple[int, int]], tile_size: int, offset: Tuple[int, int], fov_mode: bool):
    points = []
    visible_points = []
    for i, (x, y) in enumerate(path):
        if not fov_mode or (x, y) in visible_positions:
            draw_x = (x - offset[0]) * tile_size + tile_size // 2
            draw_y = (y - offset[1]) * tile_size + tile_size // 2
            points.append((draw_x, draw_y))
            if i <= movement_budget:
                visible_points.append((draw_x, draw_y))

    if len(visible_points) > 1:
        pygame.draw.lines(surface, (0, 0, 255), False, visible_points, 2)
    
    if len(visible_points) < len(points):
        red_points = [visible_points[-1]] + points[len(visible_points):]
        if len(red_points) > 1:
            pygame.draw.lines(surface, (255, 0, 0), False, red_points, 2)

    for i, point in enumerate(points):
        if i < len(visible_points):
            pygame.draw.circle(surface, (0, 0, 255), point, 3)
        else:
            pygame.draw.circle(surface, (255, 0, 0), point, 3)

def render_battlemap(surface: pygame.Surface, battle_map, selected_entity, target_position, offset: Tuple[int, int], 
                     fov_mode: bool, color_fov_mode: bool, paths_mode: bool, ray_mode: bool, path_to_target_mode: bool):
    tile_size = 32
    surface.fill((0, 0, 0, 0))  # Fill with transparent black

    draw_grid(surface, (battle_map.width, battle_map.height), tile_size, offset)

    visible_positions = set()
    reachable_positions = set()
    if selected_entity and selected_entity.sensory:
        if selected_entity.sensory.fov:
            visible_positions = selected_entity.sensory.fov.visible_tiles
        if paths_mode and selected_entity.sensory.paths:
            movement_budget_feet = selected_entity.action_economy.movement.apply(selected_entity).total_bonus
            movement_budget = movement_budget_feet // config.game_rules.movement_cost
            reachable_positions = set(selected_entity.sensory.paths.get_reachable_positions(movement_budget))

    font = pygame.font.Font(None, 32)

    for y in range(battle_map.height):
        for x in range(battle_map.width):
            is_visible = (x, y) in visible_positions or not fov_mode

            if is_visible:
                draw_x = (x - offset[0]) * tile_size
                draw_y = (y - offset[1]) * tile_size

                entity_ids = battle_map.positions.get((x, y), None)
                if entity_ids:
                    entity_ids = list(entity_ids)
                    entity = Entity.get_instance(entity_ids[0])
                    ascii_char = config.entities.ascii.get(entity.name, '?')
                    draw_ascii_char(surface, ascii_char, draw_x, draw_y, tile_size, font, is_entity=True)
                else:
                    tile_type = battle_map.get_tile(x, y)
                    if tile_type:
                        ascii_char = config.tiles.ascii.get(tile_type, ' ')
                        draw_ascii_char(surface, ascii_char, draw_x, draw_y, tile_size, font)

                if color_fov_mode and (x, y) in visible_positions:
                    draw_fov_overlay(surface, {(x, y)}, tile_size, offset)

                if paths_mode and (x, y) in reachable_positions:
                    draw_path_overlay(surface, {(x, y)}, tile_size, offset)

    if ray_mode and selected_entity and target_position:
        source_position = selected_entity.position
        if source_position and selected_entity.sensory and selected_entity.sensory.is_visible(target_position):
            ray = selected_entity.sensory.get_ray_to(target_position)
            if ray:
                draw_ray(surface, source_position, ray, tile_size, offset)

    if path_to_target_mode and selected_entity and target_position and selected_entity.sensory and selected_entity.sensory.paths:
        path = selected_entity.sensory.paths.get_shortest_path_to_position(target_position)
        if path:
            movement_budget_feet = selected_entity.action_economy.movement.apply(selected_entity).total_bonus
            movement_budget = movement_budget_feet // config.game_rules.movement_cost
            draw_path(surface, path, movement_budget, visible_positions, tile_size, offset, fov_mode)

    return surface