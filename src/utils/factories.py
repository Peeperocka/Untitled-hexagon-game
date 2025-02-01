from src.entities.base.blueprints import CityImprovementBlueprint
from src.entities.game.registry import CITY_BLUEPRINTS, UNIT_BLUEPRINTS, CITY_IMPROVEMENT_BLUEPRINTS
from src.entities.base.game_objects import Unit, Building
from src.entities.game.level_objects import City


class GameEntityFactory:
    @staticmethod
    def create_unit(unit_id: str, hex_tile, player, game_manager) -> Unit:
        """
        Creates a new unit instance based on the given unit_id, hex_tile, player and game_manager.
        """
        blueprint = UNIT_BLUEPRINTS[unit_id]
        implementation_class = blueprint.implementation_class
        return implementation_class(hex_tile, player, game_manager, unit_id, blueprint)

    @staticmethod
    def create_city(city_id: str, hex_tile, player, game_manager) -> City:
        """
        Creates a new city instance based on the given city_id, hex_tile, player and game_manager.
        """
        blueprint = CITY_BLUEPRINTS[city_id]
        implementation_class_name = blueprint.implementation_class
        if implementation_class_name == "City":
            implementation_class = City
        else:
            raise ValueError(f"Unknown city implementation class: {implementation_class_name}")
        return implementation_class(hex_tile, city_id, blueprint, game_manager, player)

    @staticmethod
    def create_tile_building(building_id: str, hex_tile, player, game_manager) -> Building:
        """
        Creates a new tile building instance based on the given building_id, hex_tile, player and game_manager.
        """
        raise NotImplemented("Not implemented")

    @staticmethod
    def get_city_improvement_blueprint(improvement_id: str) -> CityImprovementBlueprint:
        """
        Returns the city improvement blueprint for the given improvement_id.
        """
        return CITY_IMPROVEMENT_BLUEPRINTS[improvement_id]
