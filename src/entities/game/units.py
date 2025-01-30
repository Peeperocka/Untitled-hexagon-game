from src.entities.base.game_objects import Unit
from src.entities.base.blueprints import UnitBlueprint


class Warrior(Unit):
    def __init__(self, hex_tile, player, game_manager, unit_id: str, blueprint: UnitBlueprint):
        super().__init__(hex_tile, unit_id, blueprint, player, game_manager)


class Cavalry(Unit):
    def __init__(self, hex_tile, player, game_manager, unit_id: str, blueprint: UnitBlueprint):
        super().__init__(hex_tile, unit_id, blueprint, player, game_manager)


class Archer(Unit):
    def __init__(self, hex_tile, player, game_manager, unit_id: str, blueprint: UnitBlueprint):
        super().__init__(hex_tile, unit_id, blueprint, player, game_manager)


class Crossbowman(Unit):
    def __init__(self, hex_tile, player, game_manager, unit_id: str, blueprint: UnitBlueprint):
        super().__init__(hex_tile, unit_id, blueprint, player, game_manager)
