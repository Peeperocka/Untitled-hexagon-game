import pygame

import hex_utils


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
        self.enemy_reachable_hexes = []
        self.enemy_attackable_hexes = []
        self.path_to_target = []

    def _create_grid(self):
        grid = []
        for r in range(self.rows):
            min_q = -r // 2
            max_q = self.cols - r // 2
            row = []

            for q in range(min_q, max_q):
                row.append(hex_utils.Hex(q, r, -q - r))
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
                pygame.draw.polygon(surface, self.colors['tile'], [(c.x, c.y) for c in corners], 0)
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
            return None

        open_set = {start_tile}
        came_from = {}
        g_score = {start_tile: 0}
        f_score = {start_tile: self.heuristic(start_tile, goal_tile)}

        while open_set:
            current = min(open_set, key=lambda tile: f_score.get(tile, float('inf')))

            if current == goal_tile:
                return self._reconstruct_path(came_from, current)

            open_set.remove(current)

            for neighbor_coords in current.get_neighbors():
                neighbor = self.get_tile_by_hex(neighbor_coords)
                if neighbor:
                    temp_g_score = g_score[current] + 1

                    if neighbor.unit is None or neighbor == goal_tile:
                        if temp_g_score < g_score.get(neighbor, float('inf')):
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score[neighbor] = temp_g_score + self.heuristic(neighbor, goal_tile)
                            if neighbor not in open_set:
                                open_set.add(neighbor)

        return None

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def render(self, screen, camera):
        screen.blit(self.map_surface, (-camera.x, -camera.y))

        if self.highlighted_hexes:
            for hex in self.highlighted_hexes:
                corners = hex_utils.polygon_corners(self.layout, hex)
                pygame.draw.polygon(screen, self.colors['highlight'],
                                    [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

        for enemy_unit in self.enemy_attackable_hexes:
            corners = hex_utils.polygon_corners(self.layout, enemy_unit.hex_tile)
            pygame.draw.polygon(screen, self.colors['enemy_attackable'],
                                [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

        for enemy_unit in self.enemy_reachable_hexes:
            if enemy_unit not in self.enemy_attackable_hexes:
                corners = hex_utils.polygon_corners(self.layout, enemy_unit.hex_tile)
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

    def get_reachable_tiles(self, unit):
        reachable = set()
        queue = [(unit.hex_tile, unit.current_movement_range)]
        visited = {unit.hex_tile}

        while queue:
            current_tile, remaining_movement = queue.pop(0)
            reachable.add(current_tile)

            if remaining_movement > 0:
                for neighbor_coords in current_tile.get_neighbors():
                    neighbor_tile = self.get_tile_by_hex(neighbor_coords)
                    if neighbor_tile and neighbor_tile not in visited and neighbor_tile.unit is None:
                        visited.add(neighbor_tile)
                        queue.append((neighbor_tile, remaining_movement - 1))

        return reachable
