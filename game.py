import pstats
import random
import pygame
import pygame_gui
import hex_utils
import cProfile
from utils import load_image

all_sprites = pygame.sprite.Group()
all_units = pygame.sprite.Group()


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
    def __init__(self, players, board, camera, ui_manager, unit_info_text):
        self.players = players
        self.current_player_index = 0
        self.current_round = 1
        self.board = board
        self.camera = camera
        self.ui_manager = ui_manager
        self.unit_info_text = unit_info_text
        self.selected_unit = None

        self.selecting_unit_state = SelectingUnitState(self, board, camera, ui_manager, unit_info_text)
        self.unit_selected_state = UnitSelectedState(self, board, camera, ui_manager, unit_info_text)
        self.current_state = self.selecting_unit_state

    def next_player(self):
        for player in self.players:
            for unit in player.units:
                unit.selected = False
        self.board.highlighted_hexes = []
        self.selected_unit = None
        self.current_state = self.selecting_unit_state

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print('=' * 50)

        print(f"It's {self.get_current_player()}'s turn.")

        if self.current_player_index == 0:
            self.end_round()
            return

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

    def process_mouse_click(self, pos):
        self.current_state.handle_mouse_click(pos)

    def update_ui_for_selected_unit(self):
        if self.selected_unit:
            self.unit_info_text.html_text = self.selected_unit.get_unit_info_text()
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            for other_unit in all_units:
                if other_unit.player_id != self.selected_unit.player_id:
                    distance = hex_utils.cube_distance(self.selected_unit.hex_tile, other_unit.hex_tile)
                    if distance <= self.selected_unit.current_movement_range:
                        self.board.enemy_reachable_hexes.append(other_unit)
                    if distance <= self.selected_unit.attack_range:
                        self.board.enemy_attackable_hexes.append(other_unit)
        else:
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []


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
    def __init__(self, hex_tile, image_path, size, player, damage, damage_spread, hp, movement_range, attack_range):
        super().__init__(hex_tile, image_path, size)
        all_units.add(self)
        self.jump_offset = 0
        self.is_jumping = False
        self.selected = False
        self.frame_count = 0
        self.hex_tile.unit = self
        self.JUMP_HEIGHT = 10
        self.JUMP_INTERVAL = 60
        self.JUMP_SPEED = 1
        self.HEALTH_BAR_WIDTH = 40
        self.HEALTH_BAR_HEIGHT = 8
        self.HEALTH_BAR_OFFSET = 30

        self.player = player
        self.damage = damage
        self.damage_spread = damage_spread
        self.hp = hp
        self.max_hp = hp
        self.max_movement_range = movement_range
        self.current_movement_range = movement_range
        self.can_attack = True
        self.attack_range = attack_range

    @property
    def player_id(self):
        return self.player.player_id

    def update(self):
        self.frame_count += 1

        if self.selected:
            self._handle_jump()
            return

        if game_manager.is_current_player(self.player) and self.current_movement_range > 0:
            self._handle_jump()
        elif not self.is_jumping:
            pixel_coords = self.hex_tile.to_pixel(board.layout).get_coords()
            self.rect.centery = pixel_coords[1]

    def _handle_jump(self):
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

        distance = hex_utils.cube_distance(self.hex_tile, target_unit.hex_tile)
        if distance > self.attack_range:
            print(f"{target_unit} is out of attack range.")
            return False

        damage_dealt = max(0, self.damage + random.randint(-self.damage_spread, self.damage_spread))
        target_unit.take_damage(damage_dealt)
        print(f"{self} attacked {target_unit} for {damage_dealt} damage.")
        self.can_attack = False
        self.current_movement_range = 0
        return True

    def kill(self):
        self.hex_tile.unit = None
        self.player.units.remove(self)
        all_units.remove(self)
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

    def get_enemy_unit_info_text(self):
        return (
            f"<font color='#FF0000'><b>[ENEMY] {type(self).__name__}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}</font><br>"
            f"<font color='#AAAAAA'>Damage: {self.damage} (+/- {self.damage_spread})</font><br>"
            f"<font color='#AAAAAA'>Movement: {self.current_movement_range}/{self.max_movement_range}</font>"
        )

    def draw_health_bar(self, surface, camera):
        if self.hp != self.max_hp:
            bar_x = self.rect.centerx - self.HEALTH_BAR_WIDTH // 2 - camera.x
            bar_y = self.rect.centery + self.HEALTH_BAR_OFFSET - camera.y
            ratio = self.hp / self.max_hp
            fill_width = int(ratio * self.HEALTH_BAR_WIDTH)
            health_bar_rect = pygame.Rect(bar_x, bar_y, self.HEALTH_BAR_WIDTH, self.HEALTH_BAR_HEIGHT)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, self.HEALTH_BAR_HEIGHT)
            pygame.draw.rect(surface, (40, 40, 40), health_bar_rect)
            pygame.draw.rect(surface, (0, 200, 0), fill_rect)

    def render(self, surface, camera):
        super().render(surface, camera)
        self.draw_health_bar(surface, camera)


class Warrior(Unit):
    def __init__(self, hex_tile, player):
        super().__init__(hex_tile, "warrior.png", (70, 70), player, damage=30, damage_spread=7, hp=100,
                         movement_range=3, attack_range=1)


class HexBoard:
    def __init__(self, rows, cols, size):
        self.rows = rows
        self.cols = cols
        self.size = size

        self.grid = self._create_grid()
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'selection': (200, 200, 0),
            'highlight': (20, 20, 184),
            'enemy_reachable': (255, 165, 0),
            'enemy_attackable': (255, 0, 0),
            'path': (200, 0, 200),
            'tile': (149, 187, 100),
            'background': (96, 96, 96)
        }
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

                text_coords = f"{tile.q}, {tile.r}, {tile.s}"
                text_surface = self.font.render(text_coords, True, self.colors['white'])
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

    def get_visible_entities(self, camera):
        visible_entities = []
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        camera_rect = pygame.Rect(camera.x, camera.y, screen_width, screen_height)

        for entity in all_sprites:
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


class GameState:
    def __init__(self, game_manager, board, camera, ui_manager, unit_info_text):
        self.game_manager = game_manager
        self.board = board
        self.camera = camera
        self.ui_manager = ui_manager
        self.unit_info_text = unit_info_text

    def handle_mouse_click(self, pos):
        raise NotImplementedError("Subclasses must implement this method")


class SelectingUnitState(GameState):
    def handle_mouse_click(self, pos):
        clicked_tile = self.board.get_click(pos, self.camera)
        if not clicked_tile:
            print("Clicked outside the grid.")
            return

        if clicked_tile.unit and self.game_manager.is_current_player(clicked_tile.unit.player):
            print(f"Clicked unit: {clicked_tile.unit}")
            self.game_manager.selected_unit = clicked_tile.unit
            self.game_manager.current_state = self.game_manager.unit_selected_state
            self.game_manager.update_ui_for_selected_unit()
            self.board.selected_tile = clicked_tile
            self.board.highlighted_hexes = list(self.board.get_reachable_tiles(clicked_tile.unit))
        elif clicked_tile.unit:
            self.game_manager.selected_unit = None
            self.board.selected_tile = clicked_tile
            self.board.path_to_target = []
            self.unit_info_text.html_text = clicked_tile.unit.get_enemy_unit_info_text()
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
        else:
            self.game_manager.selected_unit = None
            self.board.selected_tile = clicked_tile
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            self.board.highlighted_hexes = []


class UnitSelectedState(GameState):
    def handle_mouse_click(self, pos):
        clicked_tile = self.board.get_click(pos, self.camera)
        if not clicked_tile:
            print("Clicked outside the grid.")
            return

        selected_unit = self.game_manager.selected_unit

        if clicked_tile == selected_unit.hex_tile:
            self.game_manager.selected_unit = None
            self.game_manager.current_state = self.game_manager.selecting_unit_state
            self.board.selected_tile = None
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            self.board.highlighted_hexes = []
        elif clicked_tile.unit and clicked_tile.unit != selected_unit and clicked_tile.unit.player_id != selected_unit.player_id:
            if selected_unit.attack(clicked_tile.unit):
                self.game_manager.selected_unit = None
                self.game_manager.current_state = self.game_manager.selecting_unit_state
                self.board.selected_tile = None
                self.board.path_to_target = []
                self.unit_info_text.html_text = "Select a unit to see information."
                self.unit_info_text.rebuild()
                self.board.enemy_reachable_hexes = []
                self.board.enemy_attackable_hexes = []
                self.board.highlighted_hexes = []
        elif selected_unit.move_to(clicked_tile, self.board):
            self.game_manager.selected_unit = None
            self.game_manager.current_state = self.game_manager.selecting_unit_state
            self.board.selected_tile = None
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            self.board.highlighted_hexes = []
        else:
            self.board.path_to_target = self.board.find_path(selected_unit.hex_tile,
                                                             clicked_tile) if clicked_tile else []


def place_units_for_testing(board, player1, player2, player1_units_data, player2_units_data):
    global all_sprites, all_units

    for unit_type, hex_coords in player1_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = unit_type(tile, player1)
            player1.units.add(unit)
        else:
            print(f"Could not place unit {unit_type} at {hex_coords} for Player 1.")

    for unit_type, hex_coords in player2_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = unit_type(tile, player2)
            player2.units.add(unit)
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
    camera = Camera(WIDTH, HEIGHT, 20)
    game_manager = GameManager(players, board, camera, ui_manager, unit_info_text)

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

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game_manager.process_mouse_click(event.pos)

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

        screen.fill(board.colors['background'])
        board.render(screen, camera)

        for sprite in all_sprites:
            sprite.update()
            sprite.render(screen, camera)

        ui_manager.draw_ui(screen)

        pygame.display.flip()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('tottime').print_stats(20)

    pygame.quit()
