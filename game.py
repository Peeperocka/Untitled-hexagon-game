import pstats
import random
import pygame
import pygame_gui
import hex_utils
import cProfile
from utils import load_image


class Camera:
    def __init__(self, width, height, speed):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.speed = speed

    def apply(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def apply_point(self, point):
        return hex_utils.Point(point.x - self.x, point.y - self.y)


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.units = pygame.sprite.Group()

    def __str__(self):
        return f"Player {self.player_id}"


class GameManager:
    def __init__(self, players):
        self.players = players
        self.current_player_index = 0
        self.current_round = 1

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print('=' * 50)
        if self.current_player_index == 0:
            self.end_round()
            return

        print(f"It's {self.get_current_player()}'s turn.")

    def get_current_player(self):
        return self.players[self.current_player_index]

    def is_current_player(self, player):
        return player == self.get_current_player()

    def end_round(self):
        print(f"--- End of Round {self.current_round} ---")
        for player in self.players:
            for unit in player.units:
                unit.on_round_end()
        self.current_round += 1
        print(f"--- Starting Round {self.current_round} ---")
        print(f"It's {self.get_current_player()}'s turn.")


class GameObject(pygame.sprite.Sprite):
    def __init__(self, hex_tile, image_path, size):
        super().__init__(all_sprites)
        self.hex_tile = hex_tile
        self.image = pygame.transform.scale(load_image(image_path), size)
        self.rect = self.image.get_rect()
        self.base_y = 0
        self.update_position(hex_tile)

    def update_position(self, hex_tile):
        self.hex_tile = hex_tile
        self.hex_tile.unit = self
        pixel_coords = self.hex_tile.to_pixel(board.layout).get_coords()
        self.rect.center = pixel_coords
        self.base_y = self.rect.centery

    def render(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))


class Unit(GameObject):
    JUMP_HEIGHT = 10
    JUMP_INTERVAL = 60
    JUMP_SPEED = 1

    def __init__(self, hex_tile, image_path, size, player, damage, damage_spread, hp, movement_range):
        super().__init__(hex_tile, image_path, size)
        self.jump_offset = 0
        self.is_jumping = False
        self.selected = False
        self.frame_count = 0
        self.hex_tile.unit = self

        self.player = player
        self.damage = damage
        self.damage_spread = damage_spread
        self.hp = hp
        self.max_movement_range = movement_range
        self.current_movement_range = movement_range
        self.can_attack = True

    @property
    def player_id(self):
        return self.player.player_id

    def update(self):
        self.frame_count += 1

        if self.selected or self.current_movement_range == 0:
            return

        if not self.is_jumping and self.frame_count % self.JUMP_INTERVAL == 0:
            self.is_jumping = True
            self.jump_offset = 0
            self.jump_direction = -1

        if self.is_jumping:
            if self.jump_direction == -1:
                self.rect.centery -= self.JUMP_SPEED
                self.jump_offset += self.JUMP_SPEED

                if self.jump_offset >= self.JUMP_HEIGHT:
                    self.jump_direction = 1

            elif self.jump_direction == 1:
                self.rect.centery += self.JUMP_SPEED
                self.jump_offset -= self.JUMP_SPEED

                if self.jump_offset <= 0:
                    self.is_jumping = False
                    pixel_coords = self.hex_tile.to_pixel(board.layout).get_coords()
                    self.rect.centery = pixel_coords[1]

    def take_damage(self, amount):
        self.hp -= amount
        print(f"{self} took {amount} damage. Current HP: {self.hp}")
        if self.hp <= 0:
            print(f"{self} killed")
            self.kill()

    def attack(self, target_unit):
        if not self.can_attack:
            print(f"{self} has already attacked this round.")
            return False
        if not isinstance(target_unit, Unit):
            raise ValueError("Target must be an instance of Unit.")

        damage_dealt = max(0, self.damage + random.randint(-self.damage_spread, self.damage_spread))
        target_unit.take_damage(damage_dealt)
        print(f"{self} attacked {target_unit} for {damage_dealt} damage.")
        self.can_attack = False
        self.current_movement_range = 0
        return True

    def kill(self):
        self.hex_tile.unit = None
        self.player.units.remove(self)
        super().kill()

    def move_to(self, target_tile, board):
        if target_tile == self.hex_tile:
            print("Already on this tile.")
            return False

        if target_tile.unit is not None:
            print("Tile is occupied.")
            return False

        path = board.find_path(self.hex_tile, target_tile)
        if path:
            movement_cost = len(path) - 1
            if movement_cost <= self.current_movement_range:
                old_tile = self.hex_tile
                old_tile.unit = None
                self.update_position(target_tile)
                self.current_movement_range -= movement_cost
                print(
                    f"Unit moved to: q={self.hex_tile.q}, r={self.hex_tile.r}, s={self.hex_tile.s}. Remaining movement: {self.current_movement_range}")
                return True
            else:
                print(
                    f"Not enough movement range to reach the target. Remaining: {self.current_movement_range}, needed: {movement_cost}")
                return False
        else:
            print("Target tile is unreachable.")
            return False

    def on_round_end(self):
        self.current_movement_range = self.max_movement_range
        self.can_attack = True

    def get_unit_info_text(self):
        return (
            f"<font color='#FFFFFF'><b>{type(self).__name__}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}</font><br>"
            f"<font color='#AAAAAA'>Damage: {self.damage} (+/- {self.damage_spread})</font><br>"
            f"<font color='#AAAAAA'>Movement: {self.current_movement_range}/{self.max_movement_range}</font>"
        )


class Warrior(Unit):
    def __init__(self, hex_tile, player):
        super().__init__(hex_tile, "warrior.png", (70, 70), player, damage=30, damage_spread=7, hp=100,
                         movement_range=3)


class HexBoard:
    def __init__(self, rows, cols, size):
        self.rows = rows
        self.cols = cols
        self.size = size

        self.grid = self._create_grid()
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.selection_color = (200, 200, 0)
        self.highlight_color = (121, 182, 201)
        self.path_color = (200, 0, 200)
        self.font = pygame.font.Font(None, 18)

        self.layout = hex_utils.Layout(
            hex_utils.layout_pointy,
            hex_utils.Point(size, size),
            hex_utils.Point(0, 0)
        )

        self.map_surface = self._create_map_surface()
        self._render_to_surface(self.map_surface)
        self.selected_tile = None
        self.highlighted_hexes = []
        self.path_to_target = []
        self.game_objects = []

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
                pygame.draw.polygon(surface, (8, 72, 8), [(c.x, c.y) for c in corners], 0)
                pygame.draw.polygon(surface, self.white, [(c.x, c.y) for c in corners], 1)

                text_coords = f"{tile.q}, {tile.r}, {tile.s}"
                text_surface = self.font.render(text_coords, True, self.white)
                text_rect = text_surface.get_rect(center=tile.to_pixel(self.layout).get_coords())
                surface.blit(text_surface, text_rect)

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

    def add_game_object(self, game_object):
        self.game_objects.append(game_object)

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
                pygame.draw.polygon(screen, self.highlight_color, [(c.x - camera.x, c.y - camera.y) for c in corners],
                                    1)

        if self.path_to_target:
            for hex_tile in self.path_to_target:
                corners = hex_utils.polygon_corners(self.layout, hex_tile)
                pygame.draw.polygon(screen, self.path_color, [(c.x - camera.x, c.y - camera.y) for c in corners], 3)

        if self.selected_tile:
            corners = hex_utils.polygon_corners(self.layout, self.selected_tile)
            pygame.draw.polygon(screen, self.selection_color, [(c.x - camera.x, c.y - camera.y) for c in corners], 2)

    def get_visible_entities(self, camera):
        visible_entities = []
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        camera_rect = pygame.Rect(camera.x, camera.y, screen_width, screen_height)

        for entity in self.game_objects:

            entity_rect = entity.rect

            if camera_rect.colliderect(entity_rect):
                visible_entities.append(entity)

        return visible_entities


def place_units_for_testing(board, player1, player2, player1_units_data, player2_units_data):
    global all_sprites

    for unit_type, hex_coords in player1_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = unit_type(tile, player1)
            player1.units.add(unit)
            board.add_game_object(unit)
        else:
            print(f"Could not place unit {unit_type} at {hex_coords} for Player 1.")

    for unit_type, hex_coords in player2_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = unit_type(tile, player2)
            player2.units.add(unit)
            board.add_game_object(unit)
        else:
            print(f"Could not place unit {unit_type} at {hex_coords} for Player 2.")


if __name__ == '__main__':
    pygame.init()

    FPS = 60
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hex Game")

    ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

    unit_info_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((WIDTH - 300, HEIGHT - 200), (280, 180)),
        manager=ui_manager,
        object_id=pygame_gui.core.ObjectID(class_id="@unit_info_panel")
    )

    unit_info_text = pygame_gui.elements.UITextBox(
        relative_rect=pygame.Rect((10, 10), (260, 160)),
        html_text="Select a unit to see information.",
        manager=ui_manager,
        container=unit_info_panel
    )

    font = pygame.font.Font(None, 20)

    clock = pygame.time.Clock()

    running = True
    board = HexBoard(20, 20, 50)

    all_sprites = pygame.sprite.Group()

    player1 = Player(1)
    player2 = Player(2)
    players = [player1, player2]
    game_manager = GameManager(players)

    player1_data = [
        (Warrior, (0, 0, 0)),
        (Warrior, (-1, 1, 0)),
        (Warrior, (-1, 2, -1)),
    ]
    player2_data = [
        (Warrior, (3, 0, -3)),
        (Warrior, (3, 1, -4)),
        (Warrior, (2, 2, -4)),
    ]
    place_units_for_testing(board, player1, player2, player1_data, player2_data)

    camera = Camera(WIDTH, HEIGHT, 20)

    profiler = cProfile.Profile()
    profiler.enable()
    selected_unit = None

    print(f"It's {game_manager.get_current_player()}'s turn.")

    while running:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_manager.next_player()
                    selected_unit = None
                    board.selected_tile = None
                    board.path_to_target = []
                    unit_info_text.html_text = "Select a unit to see information."
                    unit_info_text.rebuild()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    clicked_tile = board.get_click(pos, camera)

                    if not clicked_tile:
                        print("Clicked outside the grid.")
                        continue

                    if selected_unit:
                        if clicked_tile == selected_unit.hex_tile:
                            selected_unit.selected = False
                            selected_unit = None
                            board.selected_tile = None
                            board.path_to_target = []
                            unit_info_text.html_text = "Select a unit to see information."
                            unit_info_text.rebuild()
                        elif clicked_tile.unit and clicked_tile.unit != selected_unit and clicked_tile.unit.player_id != selected_unit.player_id:
                            if selected_unit.attack(clicked_tile.unit):
                                selected_unit.selected = False
                                selected_unit = None
                                board.selected_tile = None
                                board.path_to_target = []
                                unit_info_text.html_text = "Select a unit to see information."
                                unit_info_text.rebuild()
                        elif selected_unit.move_to(clicked_tile, board):
                            selected_unit.selected = False
                            selected_unit = None
                            board.selected_tile = None
                            board.path_to_target = []
                            unit_info_text.html_text = "Select a unit to see information."
                            unit_info_text.rebuild()
                        else:
                            board.path_to_target = board.find_path(selected_unit.hex_tile,
                                                                   clicked_tile) if clicked_tile else []

                    else:
                        if clicked_tile.unit and game_manager.is_current_player(clicked_tile.unit.player):
                            print(f"Clicked unit: {clicked_tile.unit}")

                            if selected_unit == clicked_tile.unit:
                                selected_unit.selected = False
                                selected_unit = None
                                board.path_to_target = []
                                unit_info_text.html_text = "Select a unit to see information."
                                unit_info_text.rebuild()

                            else:
                                if selected_unit:
                                    selected_unit.selected = False
                                selected_unit = clicked_tile.unit
                                selected_unit.selected = True
                                board.path_to_target = []
                                unit_info_text.html_text = selected_unit.get_unit_info_text()
                                unit_info_text.rebuild()

                            board.selected_tile = clicked_tile

                        else:
                            board.selected_tile = clicked_tile
                            board.path_to_target = []
                            unit_info_text.html_text = "Select a unit to see information."
                            unit_info_text.rebuild()

                    board.highlighted_hexes = []
                    if board.selected_tile and board.selected_tile.unit:
                        board.highlighted_hexes = board.selected_tile.get_hexes_in_radius(
                            board.selected_tile.unit.current_movement_range, board)

            ui_manager.process_events(event)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            camera.x -= camera.speed
        if keys[pygame.K_d]:
            camera.x += camera.speed
        if keys[pygame.K_w]:
            camera.y -= camera.speed
        if keys[pygame.K_s]:
            camera.y += camera.speed

        ui_manager.update(time_delta)

        screen.fill(board.black)
        board.render(screen, camera)

        for obj in board.game_objects:
            obj.update()
            obj.render(screen, camera)

        ui_manager.draw_ui(screen)

        pygame.display.flip()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('tottime').print_stats(20)

    pygame.quit()
