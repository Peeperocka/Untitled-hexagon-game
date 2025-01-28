import random
import pygame

from src.entities.base.game_objects import Building
from src.utils import hex_utils
from src.utils.utils import load_image
from src.entities.base.blueprints import CityBlueprint
from src.entities.game.registry import CITY_IMPROVEMENT_BLUEPRINTS, UNIT_BLUEPRINTS


# noinspection PyTypeChecker
class City(Building):
    """
    A class representing a City as a tile-based building.
    Manages city improvements internally, not as tile objects.
    """

    def __init__(self, hex_tile, player, game_manager, blueprint: CityBlueprint):
        super().__init__(hex_tile, blueprint, game_manager, player)
        self.image = pygame.transform.scale(
            load_image(blueprint.name.lower() + ".png", subdir="level_objects"), (90, 90))
        self.player = player

        self.max_hp = blueprint.base_health
        self.hp = self.max_hp
        self.attack = blueprint.base_attack
        self.min_damage = blueprint.min_damage
        self.max_damage = blueprint.max_damage
        self.defense = blueprint.defense
        self.attack_range = blueprint.attack_range

        self.HEALTH_BAR_WIDTH = 40
        self.HEALTH_BAR_HEIGHT = 8
        self.HEALTH_BAR_OFFSET = 30
        self.selected = False
        self.can_attack = True

        self.city_improvements_in_progress_id = None
        self.unit_recruitment_in_progress_id = None
        self.city_improvements = {}
        self.food_production = 5
        self.food_storage = 20
        self.gold_income = 10
        self.stone_income = 0
        self.available_unit_types = []
        self._initialize_city_improvements_blueprints()

    def _initialize_city_improvements_blueprints(self):
        self.city_improvement_blueprints = CITY_IMPROVEMENT_BLUEPRINTS
        self.unit_recruitment_blueprints_ui = UNIT_BLUEPRINTS

    def take_damage(self, damage):
        effective_damage = max(0, damage - self.defense)
        self.hp -= effective_damage
        print(f"City at {self.hex_tile.q}, {self.hex_tile.r} took {effective_damage} damage. Current HP: {self.hp}")
        if self.hp <= 0:
            self.destroy()

    def attack_unit(self, target_unit, mouse_pos):
        if not target_unit:
            return False
        if not self.can_attack:
            text = 'City has already attacked this round.'
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(f"{self} has already attacked this round.")
            return False
        distance = hex_utils.cube_distance(self.hex_tile, target_unit.hex_tile)
        if distance > self.attack_range:
            text = f"Out of attack range."
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(text)
            return False
        damage = random.randint(self.min_damage, self.max_damage)
        print(
            f"City at {self.hex_tile.q}, {self.hex_tile.r} attacks unit at {target_unit.hex_tile.q}, {target_unit.hex_tile.r} for {damage} damage.")
        target_unit.take_damage(damage)
        self.can_attack = False
        return True

    def destroy(self):
        print(f"City at {self.hex_tile.q}, {self.hex_tile.r} has been destroyed!")
        self.hex_tile.building = None
        self.player.all_objects.remove(self)
        self.game_manager.military.remove(self)
        self.player.military.remove(self)
        self.player.buildings.remove(self)
        self.game_manager.all_sprites.remove(self)

    def render_health_bar(self, surface, camera):
        if self.hp < self.max_hp:
            bar_x = self.rect.centerx - self.HEALTH_BAR_WIDTH // 2 - camera.x
            bar_y = self.rect.top + self.HEALTH_BAR_OFFSET - camera.y
            ratio = self.hp / self.max_hp
            fill_width = int(ratio * self.HEALTH_BAR_WIDTH)
            health_bar_rect = pygame.Rect(bar_x, bar_y, self.HEALTH_BAR_WIDTH, self.HEALTH_BAR_HEIGHT)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, self.HEALTH_BAR_HEIGHT)
            pygame.draw.rect(surface, (40, 40, 40), health_bar_rect)
            pygame.draw.rect(surface, (0, 200, 0), fill_rect)

    def render(self, surface, camera):
        super().render(surface, camera)
        self.render_health_bar(surface, camera)

    def get_unit_info_text(self):
        return (
            f"<font color='#FFFFFF'><b>{self.blueprint.name}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}/{self.max_hp}</font><br>"
            f"<font color='#AAAAAA'>Attack: {self.min_damage}-{self.max_damage}</font><br>"
            f"<font color='#AAAAAA'>Defense: {self.defense}</font><br>"
            f"<font color='#AAAAAA'>Attack Range: {self.attack_range}</font>"
        )

    def get_enemy_unit_info_text(self):
        return (
            f"<font color='#FF0000'><b>[ENEMY] {self.blueprint.name}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}/{self.max_hp}</font><br>"
            f"<font color='#AAAAAA'>Attack: {self.min_damage}-{self.max_damage}</font><br>"
            f"<font color='#AAAAAA'>Defense: {self.defense}</font><br>"
            f"<font color='#AAAAAA'>Attack Range: {self.attack_range}</font>"
        )

    def on_round_end(self):
        self.can_attack = True
        self.hp = min(self.hp + 5, self.max_hp)

        self.apply_city_improvement_effects()
        self._process_city_tasks_on_round_end()

    def apply_city_improvement_effects(self):
        self.food_production = 5
        self.gold_income = 10
        self.stone_income = 0
        self.available_unit_types = []
        provides_food_storage = 0

        player_income = self.player.income

        for improvement_id in self.city_improvements:
            improvement_blueprint = self.city_improvement_blueprints[improvement_id]
            for effect_type, effect_value in improvement_blueprint.provides.items():
                if effect_type == "food_production":
                    self.food_production += int(effect_value)
                    player_income["food"] += int(effect_value)
                elif effect_type == "gold_income":
                    self.gold_income += int(effect_value)
                    player_income["gold"] += int(effect_value)
                elif effect_type == "stone_income":
                    self.stone_income += int(effect_value)
                    player_income["stone"] += int(effect_value)
                elif effect_type == "unit_recruitment":
                    self.available_unit_types.append(effect_value)
                elif effect_type == "food_storage":
                    provides_food_storage += int(effect_value)
        self.food_storage = 20 + provides_food_storage

    def _process_city_tasks_on_round_end(self):
        if self.city_improvements_in_progress_id:
            self.complete_city_improvement_construction()

        if self.unit_recruitment_in_progress_id:
            self.complete_unit_recruitment()

        self.food_storage += self.food_production
        self.food_storage = max(0, self.food_storage - 2)
        self.food_storage = min(self.food_storage, self.max_food_storage)

    @property
    def max_food_storage(self):
        base_storage = 20
        for imp_id in self.city_improvements:
            print(self.city_improvements[imp_id].provides)
        storage_bonus = sum(int(effect.split(':')[1]) for imp_id in self.city_improvements
                            for effect in self.city_improvements[imp_id].provides if
                            effect.startswith('food_storage:'))
        return base_storage + storage_bonus

    def get_city_report(self):
        improvement_name = "не идет"
        if self.city_improvements_in_progress_id:
            improvement_name = self.city_improvement_blueprints[self.city_improvements_in_progress_id].name

        unit_name = "не идет"
        if self.unit_recruitment_in_progress_id:
            unit_name = self.unit_recruitment_blueprints_ui[
                self.unit_recruitment_in_progress_id].name

        improvement_list_str = ", ".join([self.city_improvement_blueprints[imp_id].name for imp_id in
                                          self.city_improvements]) if self.city_improvements else "нет"

        return [
            f"Здоровье: {self.hp}/{self.max_hp}",
            f"Защита: {self.defense}",
            f"Производство еды: {self.food_production}",
            f"Хранилище еды: {self.food_storage}/{self.max_food_storage}",
            f"Доход золота: {self.gold_income}",
            f"Добыча камня: {self.stone_income}",
            f"Строится улучшение: {improvement_name}",
            f"Наем юнита: {unit_name}",
            f"Постройки города: {improvement_list_str}"
        ]

    def get_city_improvement_blueprints(self):
        return self.city_improvement_blueprints

    def get_unit_recruitment_blueprints(self):
        return self.unit_recruitment_blueprints_ui

    def start_city_improvement_construction(self, improvement_id):
        blueprint = self.city_improvement_blueprints[improvement_id]
        player_resources = self.player.resources
        message_text_parts = []

        if self.city_improvements_in_progress_id:
            previous_blueprint_id = self.city_improvements_in_progress_id
            previous_blueprint = self.city_improvement_blueprints[previous_blueprint_id]
            player_resources["gold"] += previous_blueprint.cost_gold
            player_resources["wood"] += previous_blueprint.cost_wood
            player_resources["stone"] += previous_blueprint.cost_stone
            player_resources["metal"] += previous_blueprint.cost_metal
            message_text_parts.append(

    def start_unit_recruitment(self, unit_type):
        print(f"Начат наем юнита: {unit_type}")
        text = f"Начат наем юнита: {unit_type}"
        self.game_manager.hud_manager.dynamic_message_manager.create_message(text)
        self.unit_recruitment_in_progress_id = unit_type
        blueprint = self.unit_recruitment_blueprints_ui[unit_type]
        player_resources = self.player.resources
        message_text_parts = []

        if self.unit_recruitment_in_progress_id:
            previous_blueprint_id = self.unit_recruitment_in_progress_id
            previous_blueprint = self.unit_recruitment_blueprints_ui[previous_blueprint_id]
            player_resources["gold"] += previous_blueprint.cost_gold
            player_resources["metal"] += previous_blueprint.cost_metal
            player_resources["food"] += previous_blueprint.cost_food
            message_text_parts.append(f"Возврат ресурсов за отмену: {previous_blueprint.name}")
            self.unit_recruitment_in_progress_id = None

        if (player_resources["gold"] >= blueprint.cost_gold and
                player_resources["metal"] >= blueprint.cost_metal and
                player_resources["food"] >= blueprint.cost_food):
            player_resources["gold"] -= blueprint.cost_gold
            player_resources["metal"] -= blueprint.cost_metal
            player_resources["food"] -= blueprint.cost_food

            self.game_manager.hud_manager.update_resource_values(
                player_resources, self.player.income, self.player.expense)

            message_text_parts.append(f"Начат наем юнита: {blueprint.name}")

            self.unit_recruitment_in_progress_id = unit_type

        else:
            message_text_parts.append(f"Недостаточно ресурсов для найма юнита: {blueprint.name}")
            self.unit_recruitment_in_progress_id = None

        message_text = "\n".join(message_text_parts)
        self.game_manager.hud_manager.dynamic_message_manager.create_message(message_text)
        print(message_text.replace('\n', ' '))

    def complete_city_improvement_construction(self):
        if self.city_improvements_in_progress_id:
            improvement_id = self.city_improvements_in_progress_id
            self.city_improvements[improvement_id] = self.city_improvement_blueprints[
                improvement_id]
            print(f"Строительство улучшения города {improvement_id} завершено.")
            self.city_improvements_in_progress_id = None
            self.apply_city_improvement_effects()

    def complete_unit_recruitment(self):
        if self.unit_recruitment_in_progress_id:
            from src.utils.factories import GameEntityFactory
            unit_id = self.unit_recruitment_in_progress_id
            print(f"Наем юнита {unit_id} завершен.")
            GameEntityFactory.create_unit(unit_id, self.hex_tile, self.player, self.game_manager)
            self.unit_recruitment_in_progress_id = None
