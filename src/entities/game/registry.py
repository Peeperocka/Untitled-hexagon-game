from src.entities.base.blueprints import UnitBlueprint, TileBuildingBlueprint, CityBlueprint, CityImprovementBlueprint
from src.entities.game.units import Warrior, Cavalry, Archer, Crossbowman

UNIT_BLUEPRINTS = {
    "warrior": UnitBlueprint(
        name="Воин",
        description="Базовый пехотный юнит ближнего боя.",
        base_health=100,
        base_attack=30,
        cost_gold=50,
        cost_food=10,
        requirements=[],
        implementation_class=Warrior
    ),
    "cavalry": UnitBlueprint(
        name="Кавалерия",
        description="Быстрый кавалерийский юнит.",
        base_health=90,
        base_attack=35,
        cost_gold=80,
        cost_food=20,
        requirements=[],
        implementation_class=Cavalry
    ),
    "archer": UnitBlueprint(
        name="Лучник",
        description="Дальнобойный юнит.",
        base_health=70,
        base_attack=25,
        cost_gold=60,
        cost_food=15,
        requirements=[],
        implementation_class=Archer
    ),
    "crossbowman": UnitBlueprint(
        name="Арбалетчик",
        description="Дальнобойный юнит с высокой точностью.",
        base_health=75,
        base_attack=30,
        cost_gold=70,
        cost_food=18,
        requirements=[],
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
        provides=[],
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
        requirements=["barracks"],
        provides=["defense_bonus:+2"],
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
        provides=["food_production:+10"],
    ),
    "mine": CityImprovementBlueprint(
        name="Шахта",
        description="Добывает ценные ресурсы...",
        build_time=4,
        cost_gold=120,
        cost_wood=30,
        cost_stone=80,
        requirements=[],
        provides=["gold_income:+20", "stone_income:+5"],
    ),
    "barracks": CityImprovementBlueprint(
        name="Казармы",
        description="Позволяет нанимать пехотные юниты...",
        build_time=5,
        cost_gold=150,
        cost_wood=70,
        cost_stone=0,
        requirements=[],
        provides=["unit_recruitment:warrior", "unit_recruitment:archer"],
    ),
}
