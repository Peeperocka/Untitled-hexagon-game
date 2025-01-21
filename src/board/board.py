import pygame
from src.utils import hex_utils
import random

from src.terrains.game.terrains import (GrassTerrain, SandTerrain, MountainTerrain)


class HexBoard:
    layout = hex_utils.Layout(
        hex_utils.layout_pointy,
        hex_utils.Point(50, 50),
        hex_utils.Point(0, 0)
    )

    def __init__(self, rows, cols, size, game_manager=None):
        self.rows = rows
        self.cols = cols
        self.size = size
        self.game_manager = game_manager

        self.grid = self._create_grid()
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'selection': (200, 200, 0),
            'highlight': (20, 20, 184),
            'enemy_reachable': (255, 165, 0),
            'enemy_attackable': (255, 0, 0),
            'path': (200, 0, 200),
            'tile': (149, 187, 100, 180),
            'background': (96, 96, 96)
        }
        self.font = pygame.font.Font(None, 18)

        self.map_surface = self._create_map_surface()
        self._render_to_surface(self.map_surface)
        self.selected_tile = None
        self.highlighted_hexes = []
        self.reachable_enemy_hexes = []
        self.attackable_enemy_hexes = []
        self.path_to_target = []

    def _create_grid(self):
        grid = []
        for r in range(self.rows):
            min_q = -r // 2
            max_q = self.cols - r // 2
            row = []
            for q in range(min_q, max_q):
                terrain = random.choice((GrassTerrain, SandTerrain, MountainTerrain))()
                hex_tile = hex_utils.Hex(q, r, -q - r, terrain)
                row.append(hex_tile)
            grid.append(row)
        return grid

    def _create_map_surface(self):
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')

        for row in self.grid:
            for tile in row:
                corners = hex_utils.polygon_corners(self.layout, tile)
                for corner in corners:
                    min_x = min(min_x, corner.x)
                    min_y = min(min_y, corner.y)
                    max_x = max(max_x, corner.x)
                    max_y = max(max_y, corner.y)

        total_width = max_x - min_x + 1
        total_height = max_y - min_y

        self.layout = hex_utils.Layout(
            hex_utils.layout_pointy,
            self.layout.size,
            hex_utils.Point(-min_x, -min_y)
        )

        surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

        return surface

    def _render_to_surface(self, surface):
        for row in self.grid:
            for tile in row:
                if tile is None:
                    continue

                corners = hex_utils.polygon_corners(self.layout, tile)
                pygame.draw.polygon(surface, tile.terrain.color, [(c.x, c.y) for c in corners], 0)
                pygame.draw.polygon(surface, self.colors['black'], [(c.x, c.y) for c in corners], 2)

                # text_coords = f"{tile.q}, {tile.r}, {tile.s}"
                # text_surface = self.font.render(text_coords, True, self.colors['white'])
                # text_rect = text_surface.get_rect(center=tile.to_pixel(self.layout).get_coords())
                # surface.blit(text_surface, text_rect)

    def _get_tile_from_pos(self, pos, camera):
        screen_x, screen_y = pos

        world_x = screen_x + camera.x
        world_y = screen_y + camera.y

        hex = hex_utils.pixel_to_hex(self.layout, hex_utils.Point(world_x, world_y)).round()
        return self.get_tile_by_hex(hex)

    def get_tile_by_hex(self, hex):
        if 0 <= hex.r < self.rows:
            min_q = -hex.r // 2
            max_q = self.cols - hex.r // 2
            if min_q <= hex.q < max_q:
                for tile in self.grid[hex.r]:
                    if tile.q == hex.q:
                        return tile

        return None

    def get_click(self, pos, camera):
        return self._get_tile_from_pos(pos, camera)

    def heuristic(self, a, b):
        return hex_utils.cube_distance(a, b)

    def find_path(self, start_tile, goal_tile):
        if not start_tile or not goal_tile:
            return None, None

        open_set = {start_tile}
        came_from = {}
        g_score = {start_tile: 0}
        f_score = {start_tile: self.heuristic(start_tile, goal_tile)}

        while open_set:
            current = min(open_set, key=lambda tile: f_score.get(tile, float('inf')))

            if current == goal_tile:
                path = self._reconstruct_path(came_from, current)
                return path, g_score[goal_tile]

            open_set.remove(current)

            for neighbor_coords in current.get_neighbors():
                neighbor = self.get_tile_by_hex(neighbor_coords)
                if neighbor:
                    temp_g_score = g_score[current] + neighbor.terrain.cost

                    if neighbor.unit is None or neighbor == goal_tile:
                        if temp_g_score < g_score.get(neighbor, float('inf')):
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score[neighbor] = temp_g_score + self.heuristic(neighbor, goal_tile)
                            if neighbor not in open_set:
                                open_set.add(neighbor)

        return None, None

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]

    def render(self, screen, camera):
        screen.blit(self.map_surface, (-camera.x, -camera.y))

        if self.highlighted_hexes:
            for hex in self.highlighted_hexes:
                corners = hex_utils.polygon_corners(self.layout, hex)
                pygame.draw.polygon(screen, self.colors['highlight'],
                                    [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

        for hex_tile in self.attackable_enemy_hexes:
            corners = hex_utils.polygon_corners(self.layout, hex_tile)
            pygame.draw.polygon(screen, self.colors['enemy_attackable'],
                                [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

        for hex_tile in self.reachable_enemy_hexes:
            if hex_tile not in self.attackable_enemy_hexes:
                corners = hex_utils.polygon_corners(self.layout, hex_tile)
                pygame.draw.polygon(screen, self.colors['enemy_reachable'],
                                    [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

        if self.path_to_target:
            for hex_tile in self.path_to_target:
                corners = hex_utils.polygon_corners(self.layout, hex_tile)
                pygame.draw.polygon(screen, self.colors['path'],
                                    [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

        if self.selected_tile:
            corners = hex_utils.polygon_corners(self.layout, self.selected_tile)
            pygame.draw.polygon(screen, self.colors['selection'],
                                [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

    def get_visible_entities(self, screen, camera):
        visible_entities = []
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        camera_rect = pygame.Rect(camera.x, camera.y, screen_width, screen_height)

        for entity in self.game_manager.all_sprites:
            entity_rect = entity.rect
            if camera_rect.colliderect(entity_rect):
                visible_entities.append(entity)

        return visible_entities

    def get_reachable_tiles(self, unit, movement_range=None, include_occupied=False, allowed_extra_steps=0):
        reachable = set()
        initial_movement = movement_range if movement_range is not None else unit.current_movement_range
        queue = [(unit.hex_tile, initial_movement, allowed_extra_steps)]
        visited = {(unit.hex_tile, initial_movement, allowed_extra_steps)}

        while queue:
            current_tile, remaining_movement, remaining_extra_steps = queue.pop(0)
            reachable.add(current_tile)

            for neighbor_coords in current_tile.get_neighbors():
                neighbor_tile = self.get_tile_by_hex(neighbor_coords)
                can_move_to_neighbor = True
                if not include_occupied and neighbor_tile and neighbor_tile.unit is not None:
                    can_move_to_neighbor = False

                if neighbor_tile and can_move_to_neighbor:
                    move_cost = neighbor_tile.terrain.cost

                    if remaining_movement > 0:
                        new_remaining_movement = remaining_movement - move_cost
                        if new_remaining_movement >= 0 and (
                                neighbor_tile, new_remaining_movement, remaining_extra_steps) not in visited:
                            visited.add((neighbor_tile, new_remaining_movement, remaining_extra_steps))
                            queue.append((neighbor_tile, new_remaining_movement, remaining_extra_steps))

                    if remaining_extra_steps > 0:
                        if (neighbor_tile, 0, remaining_extra_steps - 1) not in visited:
                            visited.add((neighbor_tile, 0, remaining_extra_steps - 1))
                            queue.append((neighbor_tile, 0, remaining_extra_steps - 1))

        return reachable

    def get_hexes_in_radius(self, center_hex: hex_utils.Hex, radius: int) -> list[hex_utils.Hex]:
        results = []
        for dq in range(-radius, radius + 1):
            for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                ds = -dq - dr
                neighbor_coords = hex_utils.Hex(center_hex.q + dq, center_hex.r + dr, center_hex.s + ds)
                tile = self.get_tile_by_hex(neighbor_coords)
                if tile:
                    results.append(tile)
        return results

    def clear_selected_tile(self):
        self.highlighted_hexes = []
        self.reachable_enemy_hexes = []
        self.attackable_enemy_hexes = []
        self.path_to_target = []
        self.selected_tile = None
