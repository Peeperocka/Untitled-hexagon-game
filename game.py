import cProfile
import pstats
import pygame
import pygame_gui
from src.entities.game.level_objects import City
from src.entities.game.registry import CITY_BLUEPRINTS, UNIT_BLUEPRINTS
from src.utils import hex_utils
from src.board.board import HexBoard
from src.camera.camera import Camera
from src.game_core.game_core import Player, GameManager
from src.ui.hud.ui import HUDManager
from src.ui.windows.main_menu import MainMenu
from src.utils.deserialization import load_game
from src.utils.factories import GameEntityFactory
from src.utils.serialization import save_game

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


def main_gamer(screen, width, height):
    global game_manager, hud_manager, camera, board, player1, player2, all_sprites, \
        all_units, player_1_units, player_2_units, military_objects

    FPS = 60
    pygame.display.set_caption("Hex Game")

    camera = Camera(width, height, 20)
    font = pygame.font.Font(None, 20)
    hud_manager = HUDManager(width, height, font, restart_game)
    clock = pygame.time.Clock()

    loaded_game = load_game(hud_manager=hud_manager, camera=camera)
    if input('Начать новую?'):
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

        print("Game loaded from save file!")

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
        print("Starting a new game.")

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

    manager = pygame_gui.UIManager((width, height))
    main_menu = MainMenu(screen, manager)
    running = True

    while running:
        if main_menu.run():
            manager.clear_and_reset()
            running = main_gamer(screen, width, height)
        else:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
