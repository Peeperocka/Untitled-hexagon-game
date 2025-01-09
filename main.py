import pstats
import pygame
import hex_utils
import cProfile
from utils import load_image


class HexTile(hex_utils.Hex):
    def __init__(self, q, r, s):
        super().__init__(q, r, s)
        self.terrain = None
        self.resource = None


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


class GameObject(pygame.sprite.Sprite):
    def __init__(self, hex_tile, image_path, size):
        super().__init__()
        self.hex_tile = hex_tile
        self.image = pygame.transform.scale(load_image(image_path), size)
        self.rect = self.image.get_rect()
        self.update_position(hex_tile)

    def update_position(self, hex_tile):
        self.hex_tile = hex_tile
        self.rect.center = self.hex_tile.to_pixel(board.layout).get_coords()

    def render(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))


class Unit(GameObject):
    def __init__(self, hex_tile, image_path, size):
        super().__init__(hex_tile, image_path, size)


class Warrior(Unit):
    def __init__(self, hex_tile):
        super().__init__(hex_tile, "warrior.png", (70, 70))


class HexBoard:
    """
    Продче наш, ежеси на Клауде!
    Да святится Аджайл твой.

    Да придет Кафка твоя.

    Да будет Код Рабочий на Тесте,
    Как и на Релизе.

    Питон насущный дай нам Память.
    И прости нам Баги наши,
    Как и мы прощаем Кьюэев наших.
    И не введи нас в Джаваскушение.
    Но избави нас от Костыльного.

    Ибо Гит есть царство и сила наша.

    Во имя Спринта, Постгреса и времени Старта.

    Деплой.
    """

    def __init__(self, rows, cols, size):
        self.rows = rows
        self.cols = cols
        self.size = size

        self.grid = self._create_grid()
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.highlight_color = (200, 200, 0)
        self.hover_color = (150, 150, 150)
        self.font = pygame.font.Font(None, 18)

        self.layout = hex_utils.Layout(
            hex_utils.layout_pointy,
            hex_utils.Point(size, size),
            hex_utils.Point(0, 0)
        )

        self.map_surface = self._create_map_surface()
        self._render_to_surface(self.map_surface)
        self.hovered_hex = None
        self.game_objects = []

    def _create_grid(self):
        grid = []
        for r in range(self.rows):
            min_q = -r // 2
            max_q = self.cols - r // 2
            row = []

            for q in range(min_q, max_q):
                row.append(HexTile(q, r, -q - r))
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
        return self._get_tile_by_hex(hex)

    def _get_tile_by_hex(self, hex):
        if 0 <= hex.r < self.rows:
            min_q = -hex.r // 2
            max_q = self.cols - hex.r // 2
            if min_q <= hex.q < max_q:
                for tile in self.grid[hex.r]:
                    if tile.q == hex.q:
                        return tile

        return None

    def handle_mouse_movement(self, pos, camera):
        hovered_tile = self._get_tile_from_pos(pos, camera)
        if hovered_tile != self.hovered_hex:
            self.hovered_hex = hovered_tile
            self.map_surface = self._create_map_surface()
            self._render_to_surface(self.map_surface)

    def get_click(self, pos, camera):
        tile = self._get_tile_from_pos(pos, camera)
        if tile:
            self.highlighted_hex = tile
            print(f"Clicked hex: q={self.highlighted_hex.q}, r={self.highlighted_hex.r}, s={self.highlighted_hex.s}")
        else:
            print("Clicked outside the grid.")

    def add_game_object(self, game_object):
        self.game_objects.append(game_object)

    def render(self, screen, camera):
        screen.blit(self.map_surface, (-camera.x, -camera.y))

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


if __name__ == '__main__':
    pygame.init()

    FPS = 60
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    font = pygame.font.Font(None, 20)

    clock = pygame.time.Clock()

    running = True
    board = HexBoard(200, 200, 50)

    for i in range(20):
        for j in range(2):
            initial_tile = board.grid[i][j]
            warrior = Warrior(initial_tile)
            board.add_game_object(warrior)

    camera = Camera(WIDTH, HEIGHT, 20)

    profiler = cProfile.Profile()
    profiler.enable()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    board.get_click(pos, camera)

                if event.button == 4:
                    pass  # прокрутка вниз

                elif event.button == 5:
                    pass  # прокрутка вверх

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            camera.x -= camera.speed
        if keys[pygame.K_d]:
            camera.x += camera.speed
        if keys[pygame.K_w]:
            camera.y -= camera.speed
        if keys[pygame.K_s]:
            camera.y += camera.speed

        camera.update()
        screen.fill(board.black)
        board.render(screen, camera)

        visible_entities = board.get_visible_entities(camera)
        print(visible_entities)

        for entity in visible_entities:
            entity.render(screen, camera)

        pygame.display.flip()
        print(clock.get_fps())
        clock.tick(FPS)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('tottime').print_stats(20)

    pygame.quit()
