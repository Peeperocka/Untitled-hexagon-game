import pygame
import hex_utils


class HexTile(hex_utils.Hex):
    def __init__(self, q, r, s):
        super().__init__(q, r, s)
        self.unit = None
        self.terrain = None
        self.resource = None
        self.corners = []


class Camera:
    def __init__(self, width, height, speed):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.speed = speed

    def update(self):
        pass


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
    def __init__(self, rows, cols, size, offset_x=0, offset_y=0):
        self.rows = rows
        self.cols = cols
        self.size = size
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.grid = self._create_grid()
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.highlight_color = (200, 200, 0)
        self.hover_color = (150, 150, 150)
        self.font = pygame.font.Font(None, 18)

        self.layout = hex_utils.Layout(
            hex_utils.layout_pointy,
            hex_utils.Point(size, size),
            hex_utils.Point(offset_x, offset_y)
        )
        self.highlighted_hex = None
        self.hovered_hex = None

        self.map_surface = self._create_map_surface()
        self._render_to_surface(self.map_surface)

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
                if tile is not None:
                    corners = hex_utils.polygon_corners(self.layout, tile)
                    pygame.draw.polygon(surface, self.white, [(c.x, c.y) for c in corners], 1)

                    if tile is self.highlighted_hex:
                        pygame.draw.polygon(
                            surface, self.highlight_color,
                            [(c.x, c.y) for c in corners], 3)
                    if tile is self.hovered_hex:
                        pygame.draw.polygon(
                            surface, self.hover_color,
                            [(c.x, c.y) for c in corners], 3)

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

    def render(self, screen, camera):
        screen.blit(self.map_surface, (-camera.x, -camera.y))
        pygame.draw.line(screen, 'green', (500, 0), (500, 800))
        pygame.draw.line(screen, 'green', (0, 400), (1000, 400))


if __name__ == '__main__':
    pygame.init()

    FPS = 60
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Гексагональное поле")

    font = pygame.font.Font(None, 20)

    clock = pygame.time.Clock()

    running = True
    board = HexBoard(10, 10, 50, 0, 0)

    camera = Camera(WIDTH, HEIGHT, 20)

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

        pygame.display.flip()
        # print(clock.get_fps())
        clock.tick(FPS)

    pygame.quit()
