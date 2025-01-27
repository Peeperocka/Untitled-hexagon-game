from src.entities.base.blueprints import CityImprovementBlueprint
from src.entities.game.registry import CITY_BLUEPRINTS, UNIT_BLUEPRINTS, TILE_BUILDING_BLUEPRINTS, \
    CITY_IMPROVEMENT_BLUEPRINTS
from src.entities.base.game_objects import Unit, Building
from src.entities.game.level_objects import City
from src.entities.game.units import Warrior, Cavalry, Archer, Crossbowman


class GameEntityFactory:
    @staticmethod
    def create_unit(unit_id: str, hex_tile, player, game_manager) -> Unit:
        blueprint = UNIT_BLUEPRINTS[unit_id]
        implementation_class = blueprint.implementation_class
        return implementation_class(hex_tile, player, game_manager, blueprint)

    @staticmethod
    def create_city(city_id: str, hex_tile, player, game_manager) -> Building:
        blueprint = CITY_BLUEPRINTS[city_id]
        implementation_class_name = blueprint.implementation_class
        if implementation_class_name == "City":
            implementation_class = City
        else:
            raise ValueError(f"Unknown city implementation class: {implementation_class_name}")
        return implementation_class(hex_tile, player, game_manager, blueprint)

    @staticmethod
    def create_tile_building(building_id: str, hex_tile, player, game_manager) -> Building:
        raise NotImplemented("Not implemented")

    @staticmethod
    def get_city_improvement_blueprint(improvement_id: str) -> CityImprovementBlueprint:
        return CITY_IMPROVEMENT_BLUEPRINTS[improvement_id]
