import cProfile
import os
import pstats
import pygame
import pygame_gui
from src.utils import hex_utils
from src.board.board import HexBoard
from src.camera.camera import Camera
from src.game_core.game_core import Player, GameManager
from src.ui.hud.ui import HUDManager
from src.ui.windows.main_menu import MainMenu
from src.utils.deserialization import load_game_from_file
from src.utils.factories import GameEntityFactory

all_sprites = pygame.sprite.Group()
all_units = pygame.sprite.Group()
player_1_units = pygame.sprite.Group()
player_2_units = pygame.sprite.Group()
military_objects = pygame.sprite.Group()
game_manager = None
hud_manager = None
camera = None
board = None
player1 = None
player2 = None


def place_units_for_testing(board, player1, player2, player1_units_data, player2_units_data):
    global all_sprites, all_units, player_1_units, player_2_units, military_objects
    city_tile = board.get_tile_by_hex(hex_utils.Hex(-1, 3, -2))
    print(city_tile)
    GameEntityFactory.create_city('city', city_tile, player1, game_manager)

    for unit_id, hex_coords in player1_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = GameEntityFactory.create_unit(unit_id, tile, player1,
                                                 game_manager)
            player1.units.add(unit)
        else:
            print(f"Could not place unit {unit_id} at {hex_coords} for Player 1.")

    for unit_id, hex_coords in player2_units_data:
        tile = board.get_tile_by_hex(hex_utils.Hex(*hex_coords))
        if tile and tile.unit is None:
            unit = GameEntityFactory.create_unit(unit_id, tile, player2,
                                                 game_manager)
            player2.units.add(unit)
        else:
            print(f"Could not place unit {unit_id} at {hex_coords} for Player 2.")


def restart_game():
    global game_manager, hud_manager, camera, board, player1, player2, all_sprites, \
        all_units, player_1_units, player_2_units, military_objects

    all_sprites.empty()
    all_units.empty()
    player_1_units.empty()
    player_2_units.empty()
    military_objects.empty()

    camera.x = 0
    camera.y = 0

    board = HexBoard(20, 20, 50)
    player1 = Player(1)
    player2 = Player(2)
    players = [player1, player2]
    game_manager = GameManager(players, board, camera, hud_manager)
    board.game_manager = game_manager

    all_sprites = game_manager.all_sprites
    all_units = game_manager.all_units
    player_1_units = game_manager.player_1_units
    player_2_units = game_manager.player_2_units
    military_objects = game_manager.military

    player1_data = [
        ("cavalry", (0, 0, 0)),
        ("cavalry", (-1, 3, -2)),
        ("archer", (-1, 1, 0)),
        ("crossbowman", (-1, 2, -1)),
    ]
    player2_data = [
        ("warrior", (3, 0, -3)),
        ("warrior", (3, 1, -4)),
        ("warrior", (2, 2, -4)),
    ]
    place_units_for_testing(board, player1, player2, player1_data, player2_data)

    print("Game restarted!")


def main_gamer(screen, width, height, new_game=False, new_game_options=None, load_game=False, load_game_file=None):
    global game_manager, hud_manager, camera, board, player1, player2, all_sprites, \
        all_units, player_1_units, player_2_units, military_objects

    FPS = 60
    pygame.display.set_caption("Hex Game")

    camera = Camera(width, height, 20)
    font = pygame.font.Font(None, 20)
    hud_manager = HUDManager(width, height, font, restart_game)
    clock = pygame.time.Clock()

    if load_game and load_game_file:
        loaded_game = load_game_from_file(filepath=os.path.join('data', 'saves', load_game_file),
                                          hud_manager=hud_manager, camera=camera)
        game_manager = loaded_game
        board = game_manager.board
        camera = game_manager.camera
        hud_manager = game_manager.hud_manager
        hud_manager.set_game_manager(game_manager)
        players = game_manager.players
        player1 = players[0] if players else None
        player2 = players[1] if len(players) > 1 else None

        all_sprites = game_manager.all_sprites
        all_units = game_manager.all_units
        player_1_units = game_manager.player_1_units
        player_2_units = game_manager.player_2_units
        military_objects = game_manager.military

        print(f"Game loaded from {load_game_file}!")

    elif new_game:
        board = HexBoard(20, 20, 50)
        players = []
        num_players = new_game_options.get('player_count', 2)
        for i in range(num_players):
            players.append(Player(i + 1))
        player1 = players[0] if players else None
        player2 = players[1] if len(players) > 1 else None

        game_manager = GameManager(players, board, camera, hud_manager)
        board.game_manager = game_manager
        board.camera = camera
        hud_manager.set_game_manager(game_manager)

        all_sprites = game_manager.all_sprites
        all_units = game_manager.all_units
        player_1_units = game_manager.player_1_units
        player_2_units = game_manager.player_2_units
        military_objects = game_manager.military

        player1_data = [
            ("cavalry", (0, 0, 0)),
            ("cavalry", (-1, 3, -2)),
            ("archer", (-1, 1, 0)),
            ("crossbowman", (-1, 2, -1)),
        ]
        player2_data = [
            ("warrior", (3, 0, -3)),
            ("warrior", (3, 1, -4)),
        ]
        place_units_for_testing(board, player1, player2, player1_data, player2_data)
        print("Starting a new game with options:", new_game_options)

    else:
        board = HexBoard(20, 20, 50)
        player1 = Player(1)
        player2 = Player(2)
        players = [player1, player2]
        game_manager = GameManager(players, board, camera, hud_manager)
        board.game_manager = game_manager
        board.camera = camera
        hud_manager.set_game_manager(game_manager)

        all_sprites = game_manager.all_sprites
        all_units = game_manager.all_units
        player_1_units = game_manager.player_1_units
        player_2_units = game_manager.player_2_units
        military_objects = game_manager.military

        player1_data = [
            ("cavalry", (0, 0, 0)),
            ("cavalry", (-1, 3, -2)),
            ("archer", (-1, 1, 0)),
            ("crossbowman", (-1, 2, -1)),
        ]
        player2_data = [
            ("warrior", (3, 0, -3)),
            ("warrior", (3, 1, -4)),
        ]
        place_units_for_testing(board, player1, player2, player1_data, player2_data)
        print("Starting a new default game as no save found and 'Continue' pressed.")

    profiler = cProfile.Profile()
    profiler.enable()

    running = True
    print(f"It's {game_manager.get_current_player()}'s turn.")

    while running:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            hud_manager.process_event(event)
            if hud_manager.is_paused or hud_manager.splash_screen.is_visible:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_manager.next_player()
                if event.key == pygame.K_ESCAPE:
                    game_manager.deselect_unit()
                    game_manager.deselect_building()
                else:
                    game_manager.process_key_press(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game_manager.process_mouse_click(event.pos)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            camera.x -= camera.speed
        if keys[pygame.K_d]:
            camera.x += camera.speed
        if keys[pygame.K_w]:
            camera.y -= camera.speed
        if keys[pygame.K_s]:
            camera.y += camera.speed

        if not hud_manager.is_paused:
            for sprite in all_sprites:
                sprite.update()
            hud_manager.update(time_delta)
        else:
            hud_manager.update(time_delta)

        screen.fill(board.colors['background'])
        board.render(screen, camera)

        for sprite in all_sprites:
            sprite.render(screen, camera)

        hud_manager.draw(screen)

        if game_manager.game_over:
            hud_manager.show_game_over_menu(game_manager.game_over_message, game_manager.player_scores)

        pygame.display.flip()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('tottime').print_stats(20)
    return False


def main():
    pygame.init()
    width, height = 1000, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Hex Game")

    manager = pygame_gui.UIManager((width, height), os.path.join('data', 'theme', 'game_theme.json'))
    main_menu = MainMenu(screen, manager)
    running = True

    while running:
        menu_action, menu_data = main_menu.run()
        if menu_action == "start_game":
            manager.clear_and_reset()
            running = main_gamer(screen, width, height)
        elif menu_action == "new_game":
            manager.clear_and_reset()
            new_game_options = menu_data
            print("New Game Options:", new_game_options)
            running = main_gamer(screen, width, height, new_game=True,
                                 new_game_options=new_game_options)
        elif menu_action == "load_game":
            manager.clear_and_reset()
            load_game_data = menu_data
            print("Load Game Data:", load_game_data)
            running = main_gamer(screen, width, height, load_game=True,
                                 load_game_file=load_game_data.get('save_file'))
        elif menu_action == "quit":
            running = False
        else:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
