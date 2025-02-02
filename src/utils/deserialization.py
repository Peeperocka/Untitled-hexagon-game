import json
import os.path

from src.board.board import HexBoard
from src.utils import hex_utils
from src.utils.hex_utils import Hex
from src.entities.game.registry import UNIT_BLUEPRINTS, CITY_BLUEPRINTS, TERRAIN_NAME_REVERSE_MAPPING
from src.utils.factories import GameEntityFactory


def deserialize_terrain(terrain_data):
    terrain_class = TERRAIN_NAME_REVERSE_MAPPING[terrain_data]
    return terrain_class()


def deserialize_unit(unit_data, tile, player, game_manager):
    unit_type_name = unit_data["type"].lower()
    unit_blueprint = UNIT_BLUEPRINTS.get(unit_type_name)

    if not unit_blueprint:
        raise ValueError(f"Unknown unit type: {unit_type_name}")

    unit = GameEntityFactory.create_unit(unit_type_name, tile, player, game_manager)
    unit.hp = unit_data["hp"]
    unit.current_movement_range = unit_data["current_movement_range"]
    unit.can_attack = unit_data["can_attack"]
    unit.is_dug_in = unit_data["is_dug_in"]
    return unit


def deserialize_building(building_data, tile, player, game_manager):
    building_type_name = building_data["type"].lower()
    building_blueprint = CITY_BLUEPRINTS.get(building_type_name)

    if not building_blueprint:
        raise ValueError(f"Unknown building type: {building_type_name}")

    building = GameEntityFactory.create_city(building_type_name, tile, player, game_manager)
    building.hp = building_data["hp"]
    return building


def deserialize_tile(tile_data):
    q = tile_data["q"]
    r = tile_data["r"]
    s = tile_data["s"]
    terrain = deserialize_terrain(tile_data["terrain"])
    tile = Hex(q, r, s, terrain)
    return tile


def deserialize_board(board_data, game_manager, players):
    rows = board_data["rows"]
    cols = board_data["cols"]
    tiles_data = board_data["tiles"]
    deserialized_tiles = []
    units_to_create = []
    buildings_to_create = []

    for tile_data in tiles_data:
        tile = deserialize_tile(tile_data)
        deserialized_tiles.append(tile_data)
        if "unit" in tile_data:
            units_to_create.append(tile_data)
        if "building" in tile_data:
            buildings_to_create.append(tile_data)

    board_instance = HexBoard(rows, cols, 50, initial_grid_data=deserialized_tiles)

    return board_instance, units_to_create, buildings_to_create


def deserialize_player(player_data):
    from src.game_core.game_core import Player
    player = Player(player_data["player_id"])
    player.resources = player_data["resources"]
    player.income = player_data["income"]
    player.expense = player_data["expense"]
    player.camera_x = player_data["camera_x"]
    player.camera_y = player_data["camera_y"]
    player.score = player_data["score"]
    player.has_first_city_bonus = player_data["has_first_city_bonus"]
    return player


def deserialize_game_state(game_state_data, hud_manager, camera):
    players_data = game_state_data["players"]
    players = [deserialize_player(player_data) for player_data in players_data]

    board_instance, units_to_create_data, buildings_to_create_data = deserialize_board(
        game_state_data["board"], None, players)
    from src.game_core.game_core import GameManager
    game_manager_instance = GameManager(players, board_instance, camera,
                                        hud_manager)

    board_instance.game_manager = game_manager_instance
    board_instance.camera = camera
    game_manager_instance.camera = camera

    for building_data in buildings_to_create_data:
        q = building_data["q"]
        r = building_data["r"]
        s = building_data["s"]
        tile = board_instance.get_tile_by_hex(hex_utils.Hex(q, r, s))
        if tile:
            player_id = building_data["building"]["player_id"]
            player = next((p for p in players if p.player_id == player_id), None)
            if player:
                building = deserialize_building(building_data["building"], tile, player,
                                                game_manager_instance)
                tile.building = building
                player.buildings.add(building)

    for unit_data in units_to_create_data:
        q = unit_data["q"]
        r = unit_data["r"]
        s = unit_data["s"]
        tile = board_instance.get_tile_by_hex(hex_utils.Hex(q, r, s))
        if tile:
            player_id = unit_data["unit"]["player_id"]
            player = next((p for p in players if p.player_id == player_id), None)
            if player:
                unit = deserialize_unit(unit_data["unit"], tile, player, game_manager_instance)
                tile.unit = unit
                player.units.add(unit)
                player.military.add(unit)
                game_manager_instance.all_units.add(unit)

    game_manager_instance.current_player_index = next(
        (i for i, p in enumerate(game_manager_instance.players) if p.player_id == game_state_data["current_player_id"]),
        0)
    game_manager_instance.current_round = game_state_data["current_round"]
    game_manager_instance.game_over = game_state_data["game_over"]
    game_manager_instance.game_over_message = game_state_data["game_over_message"]
    game_manager_instance.player_scores = game_state_data[
        "player_scores"] if "player_scores" in game_state_data else {}

    return game_manager_instance


def load_game_from_file(filepath=os.path.join("data", "saves", "savegame.json"), hud_manager=None, camera=None):
    try:
        with open(filepath, "r") as f:
            game_state_data = json.load(f)
            game_manager = deserialize_game_state(game_state_data, hud_manager,
                                                  camera)
            return game_manager
    except FileNotFoundError:
        print(f"Save file not found: {filepath}")
        raise
    except Exception as e:
        print(f"Error during game loading: {e}")
        raise
