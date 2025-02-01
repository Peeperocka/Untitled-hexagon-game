import json
from src.utils.deserialization import TERRAIN_NAME_MAPPING


def serialize_unit(unit):
    return {
        "type": unit.blueprint.implementation_class.__name__,
        "position": {
            "q": unit.hex_tile.q,
            "r": unit.hex_tile.r,
            "s": unit.hex_tile.s,
        },
        "hp": unit.hp,
        "current_movement_range": unit.current_movement_range,
        "can_attack": unit.can_attack,
        "is_dug_in": unit.is_dug_in,
        "player_id": unit.player.player_id,
    }


def serialize_building(building):
    return {
        "type": building.blueprint.implementation_class,
        "position": {
            "q": building.hex_tile.q,
            "r": building.hex_tile.r,
            "s": building.hex_tile.s,
        },
        "hp": building.hp,
        "player_id": building.player.player_id,
    }


def serialize_player(player):
    return {
        "player_id": player.player_id,
        "resources": player.resources,
        "income": player.income,
        "expense": player.expense,
        "camera_x": player.camera_x,
        "camera_y": player.camera_y,
        "score": player.score,
        "has_first_city_bonus": player.has_first_city_bonus,
    }


def serialize_tile(tile):
    data = {
        "q": tile.q,
        "r": tile.r,
        "s": tile.s,
        "terrain": TERRAIN_NAME_MAPPING[type(tile.terrain)],
    }
    if tile.building:
        data["building"] = serialize_building(tile.building)
    if tile.unit:
        data["unit"] = serialize_unit(tile.unit)
    return data


def serialize_board(board):
    tiles_data = []
    for tile in board.grid.values():
        tiles_data.append(serialize_tile(tile))

    return {
        "rows": board.rows,
        "cols": board.cols,
        "tiles": tiles_data,
    }


def serialize_game_state(game_manager):
    return {
        "board": serialize_board(game_manager.board),
        "players": [serialize_player(player) for player in game_manager.players],
        "current_player_id": game_manager.get_current_player().player_id
        if game_manager.get_current_player()
        else None,
        "current_round": game_manager.current_round,
        "game_over": game_manager.game_over,
        "game_over_message": game_manager.game_over_message,
        "player_scores": game_manager.player_scores if hasattr(game_manager, 'player_scores') else {},
    }


def save_game(game_manager, filename="data/saves/savegame.json"):
    game_state = serialize_game_state(game_manager)
    with open(filename, "w") as f:
        json.dump(game_state, f, indent=4)
