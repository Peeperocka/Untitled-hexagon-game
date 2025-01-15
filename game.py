import cProfile
import pstats
import pygame
import pygame_gui
import hex_utils
from board import HexBoard
from camera import Camera
from game_core import Player, GameManager
from units import Warrior


def place_units_for_testing(board, player1, player2, player1_units_data, player2_units_data):
    global all_sprites, all_units, player_1_units, player_2_units, military_objects

    for unit_type, hex_coords in player1_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = unit_type(tile, player1, game_manager)
            player1.units.add(unit)
        else:
            print(f"Could not place unit {unit_type} at {hex_coords} for Player 1.")

    for unit_type, hex_coords in player2_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = unit_type(tile, player2, game_manager)
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
    camera = Camera(WIDTH, HEIGHT, 20)

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

    player1 = Player(1)
    player2 = Player(2)
    players = [player1, player2]

    game_manager = GameManager(players, board, camera, ui_manager, unit_info_text)
    board.game_manager = game_manager

    all_sprites = game_manager.all_sprites
    all_units = game_manager.all_units
    player_1_units = game_manager.player_1_units
    player_2_units = game_manager.player_2_units
    military_objects = game_manager.military

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
