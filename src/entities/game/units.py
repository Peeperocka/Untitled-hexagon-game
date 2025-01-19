from src.entities.base.units import Unit


class Warrior(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "warrior.png", (70, 70), player, game_manager, damage=30, damage_spread=7, hp=100,
                         movement_range=5, attack_range=1)


class Cavalry(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "cavalry.png", (70, 90), player, game_manager, damage=35, damage_spread=6, hp=90,
                         movement_range=4, attack_range=2)


class Archer(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "archer.png", (80, 70), player, game_manager, damage=25, damage_spread=10, hp=70,
                         movement_range=3, attack_range=5)


class Crossbowman(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "crossbowman.png", (50, 65), player, game_manager, damage=30, damage_spread=6, hp=75,
                         movement_range=3, attack_range=6)
