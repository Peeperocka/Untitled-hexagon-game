import random

import pygame

from src.entities.base.game_objects import Building
from src.utils import hex_utils
from src.utils.utils import load_image


class City(Building):
    """
    A class representing a city in the game, inheriting from Building.

    Attributes:
        hp (int): The city's current health points.
        max_health (int): The city's maximum health points.
        attack (int): The city's attack power.
        min_damage (int): The minimum damage the city can inflict.
        max_damage (int): The maximum damage the city can inflict.
        defense (int): Reduce incoming damage by that amount.
        attack_range (int): The range at which the city can attack.
        image (str): The path to the city's image.
        size (tuple): The size of the city's image.
        player (Player): The player that owns the city.
        game_manager (GameManager): The game manager responsible for managing the whole game.
        city_build_options (dict): Dictionary of city building options.
        unit_build_options (dict): Dictionary of unit building options.
    """

    def __init__(self, hex_tile, player, image="castle.png", size=(90, 90), game_manager=None,
                 hp=100, attack=10, min_damage=5, max_damage=30, defense=5, attack_range=3,
                 image_subdir="level_objects"):
        super().__init__(hex_tile, image, size, game_manager, player, image_subdir=image_subdir)
        self.image = pygame.transform.scale(load_image(image, subdir=image_subdir, colorkey=-1), size)
        self.player = player
        self.max_hp = hp
        self.hp = self.max_hp
        self.attack = attack
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.defense = defense
        self.attack_range = attack_range
        self.HEALTH_BAR_WIDTH = 40
        self.HEALTH_BAR_HEIGHT = 8
        self.HEALTH_BAR_OFFSET = 30
        self.selected = False
        self.can_attack = True

        self.city_building = None
        self.unit_building = None
        self._initialize_build_options()

    def _initialize_build_options(self):
        self.city_build_options = {
            "build_farm": {"name": "Ферма",
                           "description": "Увеличивает производство еды в городе. Необходима для роста населения и предотвращения голода."},
            "build_mine": {"name": "Шахта",
                           "description": "Добывает ценные ресурсы, такие как камень, железо или золото. Увеличивает доход ресурсов для развития города и найма юнитов."},
            "build_barracks": {"name": "Казармы",
                               "description": "Позволяет нанимать базовые пехотные юниты. Основа вашей армии для защиты и нападения."},
            "build_wall": {"name": "Стена",
                           "description": "Улучшает защиту города, делая его более устойчивым к вражеским атакам и осадам."},
            "build_market": {"name": "Рынок",
                             "description": "Усиливает экономику города, увеличивая торговый доход и расширяя доступ к разнообразным товарам."},
            "build_forge": {"name": "Кузница",
                            "description": "Улучшает военную мощь города, позволяя создавать лучшее оружие и броню для ваших юнитов."},
            "build_granary": {"name": "Амбар",
                              "description": "Увеличивает вместимость хранилищ еды, уменьшая потери от порчи и обеспечивая стабильное снабжение продовольствием."},
            "build_stable": {"name": "Конюшня",
                             "description": "Позволяет нанимать кавалерийские юниты. Обеспечивает быстрые и мобильные военные силы."},
            "build_tower": {"name": "Башня",
                            "description": "Оборонительное сооружение, усиливающее защиту города дальнобойными атаками, эффективно против вражеских осад."},
        }
        self.unit_build_options = {
            "build_peasant": {"name": "Крестьянин",
                              "description": "Базовый гражданский юнит, занимается сбором ресурсов и строительством. Основа экономики города."},
            "build_warrior": {"name": "Воин",
                              "description": "Базовый пехотный юнит ближнего боя. Эффективен в ближнем бою и против легкобронированных противников."},
            "build_archer": {"name": "Лучник",
                             "description": "Дальнобойный юнит, атакует на расстоянии. Эффективен против пехоты и для ослабления врага перед ближним боем."},
            "build_knight": {"name": "Рыцарь",
                             "description": "Тяжелая кавалерия, мощная и быстрая. Отлично подходит для фланговых маневров и прорыва вражеских линий. Дорогой в найме."},
            "build_mage": {"name": "Маг",
                           "description": "Юнит, использующий магию. Может наносить магический урон, лечить или применять заклинания поддержки."},
            "build_priest": {"name": "Жрец",
                             "description": "Юнит поддержки, лечит дружественные войска и повышает их боевой дух. Важен для поддержания армии в бою."},
            "build_scout": {"name": "Разведчик",
                            "description": "Быстрый и легкий юнит для разведки местности, обнаружения врагов и ресурсов."},
        }

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
            f"<font color='#FFFFFF'><b>{type(self).__name__}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}/{self.max_hp}</font><br>"
            f"<font color='#AAAAAA'>Attack: {self.min_damage}-{self.max_damage}</font><br>"
            f"<font color='#AAAAAA'>Defense: {self.defense}</font><br>"
            f"<font color='#AAAAAA'>Attack Range: {self.attack_range}</font>"
        )

    def get_enemy_unit_info_text(self):
        return (
            f"<font color='#FF0000'><b>[ENEMY] {type(self).__name__}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}/{self.max_hp}</font><br>"
            f"<font color='#AAAAAA'>Attack: {self.min_damage}-{self.max_damage}</font><br>"
            f"<font color='#AAAAAA'>Defense: {self.defense}</font><br>"
            f"<font color='#AAAAAA'>Attack Range: {self.attack_range}</font>"
        )

    def on_round_end(self):
        self.can_attack = True
        self.hp = min(self.hp + 5, self.max_hp)

    def get_info_list(self):
        return [
            f"Здоровье: {self.hp}/{self.max_hp}",
            f"Защита: {self.defense}",
            f"Улучшение города: {self.city_build_options[self.city_building]['name'] if self.city_building else 'не идет'}",
            f"Производство юнита: {self.unit_build_options[self.unit_building]['name'] if self.unit_building else 'не идет'}"
        ]

    def get_city_build_options(self):
        return self.city_build_options

    def get_unit_build_options(self):
        return self.unit_build_options

    def start_city_build(self, building_type):
        print(f"Начато строительство города: {building_type}")
        self.city_building = building_type

    def start_unit_build(self, unit_type):
        print(f"Начато производство юнита: {unit_type}")
        self.unit_building = unit_type
