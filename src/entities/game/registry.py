from src.entities.base.blueprints import UnitBlueprint, TileBuildingBlueprint, CityBlueprint, CityImprovementBlueprint
from src.entities.game.units import Warrior, Cavalry, Archer, Crossbowman
from src.game_core.states.states import SelectingUnitState, UnitSelectedState, BuildingSelectedState
from src.terrains.game.terrains import GrassTerrain, SandTerrain, MountainTerrain

TERRAIN_NAME_MAPPING = {
    GrassTerrain: "grass",
    SandTerrain: "sand",
    MountainTerrain: "mountain",
}

TERRAIN_NAME_REVERSE_MAPPING = {v: k for k, v in TERRAIN_NAME_MAPPING.items()}

STATE_NAME_MAPPING = {
    SelectingUnitState: "selecting_unit_state",
    UnitSelectedState: "unit_selected_state",
    BuildingSelectedState: "building_selected_state",
}

STATE_NAME_REVERSE_MAPPING = {v: k for k, v in STATE_NAME_MAPPING.items()}

UNIT_BLUEPRINTS = {
    "warrior": UnitBlueprint(
        name="Воин",
        description="Базовый пехотный юнит ближнего боя, крепкий и надежный.",
        base_health=120,
        base_attack=25,
        attack_spread=5,
        attack_range=1,
        movement_range=3,
        cost_gold=50,
        cost_food=10,
        cost_metal=0,
        requirements=[],
        implementation_class=Warrior
    ),
    "cavalry": UnitBlueprint(
        name="Кавалерия",
        description="Быстрый и маневренный кавалерийский юнит, хорош для фланговых атак.",
        base_health=80,
        base_attack=35,
        attack_spread=7,
        attack_range=1,
        movement_range=5,
        cost_gold=80,
        cost_food=30,
        cost_metal=15,
        requirements=[],
        implementation_class=Cavalry
    ),
    "archer": UnitBlueprint(
        name="Лучник",
        description="Дальнобойный юнит, эффективен на расстоянии, но уязвим в ближнем бою.",
        base_health=60,
        base_attack=20,
        attack_spread=8,
        attack_range=4,
        movement_range=2,
        cost_gold=60,
        cost_food=15,
        cost_metal=0,
        requirements=[],
        implementation_class=Archer
    ),
    "crossbowman": UnitBlueprint(
        name="Арбалетчик",
        description="Дальнобойный юнит с повышенной точностью и пробивной силой.",
        base_health=70,
        base_attack=30,
        attack_spread=4,
        attack_range=5,
        movement_range=2,
        cost_gold=70,
        cost_food=18,
        cost_metal=10,
        requirements=["barracks"],
        implementation_class=Crossbowman
    ),
}

CITY_BLUEPRINTS = {
    "city": CityBlueprint(
        name="Город",
        description="Главный город...",
        build_time=0,
        cost_gold=0,
        cost_wood=0,
        cost_stone=0,
        requirements=[],
        provides={},
        implementation_class="City",
        base_health=200,
        base_attack=15,
        min_damage=8,
        max_damage=40,
        defense=8,
        attack_range=4,
    ),
}

TILE_BUILDING_BLUEPRINTS = {
    "tower": TileBuildingBlueprint(
        name="Башня",
        description="Оборонительная башня.",
        build_time=5,
        cost_gold=150,
        cost_wood=80,
        cost_stone=50,
        cost_metal=0,
        requirements=["barracks"],
        provides={"defense_bonus": 2},
        implementation_class="Tower",
        base_health=100,
        base_attack=20,
        min_damage=10,
        max_damage=30,
        defense=3,
        attack_range=5,
    ),
}

CITY_IMPROVEMENT_BLUEPRINTS = {
    "farm": CityImprovementBlueprint(
        name="Ферма",
        description="Увеличивает производство еды...",
        build_time=3,
        cost_gold=100,
        cost_wood=50,
        cost_stone=20,
        requirements=[],
        provides={"food_production": 10},
    ),
    "mine": CityImprovementBlueprint(
        name="Шахта",
        description="Добывает ценные ресурсы...",
        build_time=4,
        cost_gold=120,
        cost_wood=30,
        cost_stone=80,
        requirements=[],
        provides={"gold_income": 20, "stone_income": 5},
    ),
    "barracks": CityImprovementBlueprint(
        name="Казармы",
        description="Позволяет нанимать пехотные юниты...",
        build_time=5,
        cost_gold=150,
        cost_wood=70,
        cost_stone=0,
        requirements=[],
        provides={},
    ),
}
