from dataclasses import dataclass
from typing import List, Type


@dataclass
class UnitBlueprint:
    """Blueprint for units."""
    name: str
    description: str
    base_health: int
    base_attack: int
    attack_spread: int
    attack_range: int
    cost_gold: int
    cost_food: int
    cost_metal: int
    requirements: List[str]
    implementation_class: Type


@dataclass
class TileBuildingBlueprint:
    """Blueprint for buildings that occupy tiles."""
    name: str
    description: str
    build_time: int
    cost_gold: int
    cost_wood: int
    cost_stone: int
    cost_metal: int
    requirements: List[str]
    provides: List[str]
    implementation_class: str
    base_health: int = 100
    base_attack: int = 0
    min_damage: int = 0
    max_damage: int = 0
    defense: int = 0
    attack_range: int = 0


@dataclass
class CityBlueprint:
    """Blueprint specifically for the City tile building."""
    name: str
    description: str
    build_time: int
    cost_gold: int
    cost_wood: int
    cost_stone: int
    requirements: List[str]
    provides: List[str]
    implementation_class: str
    base_health: int = 200
    base_attack: int = 15
    min_damage: int = 5
    max_damage: int = 30
    defense: int = 5
    attack_range: int = 3


@dataclass
class CityImprovementBlueprint:
    """Blueprint for city-level improvements (non-tile city upgrades)."""
    name: str
    description: str
    build_time: int
    requirements: List[str]
    provides: List[str]
    cost_gold: int
    cost_wood: int = 0
    cost_stone: int = 0
    cost_metal: int = 0
