import cProfile
import pstats
import pygame
import pygame_gui
from src.utils import hex_utils
from src.board.board import HexBoard
from src.camera.camera import Camera
from src.game_core.game_core import Player, GameManager
from src.entities.game.units import Warrior, Cavalry, Archer, Crossbowman
from src.ui.hud.ui import HUDManager
from src.ui.windows.main_menu import MainMenu

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


def main_gamer(screen, width, height):
    global game_manager, hud_manager, camera, board, player1, player2, all_sprites, all_units, player_1_units, player_2_units, military_objects

    FPS = 60
    pygame.display.set_caption("Hex Game")

    camera = Camera(width, height, 20)
    font = pygame.font.Font(None, 20)
    hud_manager = HUDManager(width, height, font)
    clock = pygame.time.Clock()

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
        (Cavalry, (0, 0, 0)),
        (Archer, (-1, 1, 0)),
        (Crossbowman, (-1, 2, -1)),
    ]
    player2_data = [
        (Warrior, (3, 0, -3)),
        (Warrior, (3, 1, -4)),
        (Warrior, (2, 2, -4)),
    ]
    place_units_for_testing(board, player1, player2, player1_data, player2_data)

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
            if hud_manager.is_paused:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_manager.next_player()
                if event.key == pygame.K_ESCAPE:
                    game_manager.deselect_unit()

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


if __name__ == '__main__':
    main()
