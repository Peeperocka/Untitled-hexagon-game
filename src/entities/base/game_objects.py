import random

import pygame

from src.utils import hex_utils
from src.utils.utils import load_image
from src.entities.base.blueprints import UnitBlueprint, TileBuildingBlueprint


class GameObject(pygame.sprite.Sprite):
    def __init__(self, hex_tile, image_name, size, game_manager, player,
                 image_subdir=None):
        super().__init__(game_manager.all_sprites)
        self.game_manager = game_manager
        self.hex_tile = hex_tile
        self.hex_tile.unit = self
        self.image = pygame.transform.scale(load_image(image_name, subdir=image_subdir), size)
        self.rect = self.image.get_rect()
        self.base_y = 0
        self.update_position(hex_tile)
        self.player = player
        self.player.all_objects.add(self)

    def update_position(self, hex_tile):
        self.hex_tile.unit = None
        self.hex_tile = hex_tile
        self.hex_tile.unit = self
        pixel_coords = self.hex_tile.to_pixel(self.game_manager.board.layout).get_coords()
        self.rect.center = pixel_coords
        self.base_y = self.rect.centery

    def render(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))


class Building(GameObject):
    def __init__(self, hex_tile, city_id: str, blueprint: TileBuildingBlueprint, game_manager, player,
                 image_subdir='level_objects'):
        super().__init__(hex_tile, city_id + ".png", (90, 90), game_manager, player,
                         image_subdir)
        self.blueprint = blueprint
        self.hex_tile.unit = None
        self.hex_tile.building = self
        self.player.buildings.add(self)
        self.hp = blueprint.base_health
        self.max_hp = blueprint.base_health
        self.attack_range = blueprint.attack_range
        self.damage = blueprint.base_attack
        self.min_damage = blueprint.min_damage
        self.max_damage = blueprint.max_damage
        self.defense = blueprint.defense
        self.can_attack = False

    def update_position(self, hex_tile):
        self.hex_tile.building = None
        self.hex_tile = hex_tile
        self.hex_tile.building = self
        pixel_coords = self.hex_tile.to_pixel(self.game_manager.board.layout).get_coords()
        self.rect.center = pixel_coords
        self.base_y = self.rect.centery

    def take_damage(self, amount):
        self.hp -= amount
        print(f"{self} (Building) took {amount} damage. Current HP: {self.hp}")
        if self.hp <= 0:
            print(f"{self} (Building) has been destroyed.")
            self.die()

    def die(self):
        self.player.buildings.remove(self)
        if self.hex_tile:
            self.hex_tile.building = None
            self.hex_tile = None
        super().kill()

    def attack_target(self, target_unit):
        if not self.can_attack:
            print(f"{self} (Building) cannot attack yet or has already attacked.")
            return False

        distance = hex_utils.cube_distance(self.hex_tile, target_unit.hex_tile)
        if distance > self.attack_range:
            print(f"{self} (Building) target out of attack range.")
            return False

        damage_dealt = random.randint(self.min_damage, self.max_damage)
        target_unit.take_damage(damage_dealt)
        print(f"{self} (Building) attacked {target_unit} for {damage_dealt} damage.")
        self.can_attack = False


class Unit(GameObject):
    def __init__(self, hex_tile, unit_id: str, blueprint: UnitBlueprint, player, game_manager):
        super().__init__(hex_tile, unit_id + '.png', (70, 70), game_manager, player,
                         image_subdir='units')
        self.blueprint = blueprint
        self.player = player
        game_manager.all_units.add(self)

        if player.player_id == 1:
            game_manager.player_1_units.add(self)
        elif player.player_id == 2:
            game_manager.player_2_units.add(self)
        self.player.units.add(self)
        self.player.military.add(self)

        self.jump_offset = 0
        self.is_jumping = False
        self.selected = False
        self.frame_count = 0
        self.JUMP_HEIGHT = 10
        self.JUMP_INTERVAL = 60
        self.JUMP_SPEED = 1

        self.HEALTH_BAR_WIDTH = 40
        self.HEALTH_BAR_HEIGHT = 8
        self.HEALTH_BAR_OFFSET = 30
        self.hp = blueprint.base_health
        self.max_hp = blueprint.base_health

        self.damage = blueprint.base_attack
        self.damage_spread = blueprint.attack_spread
        self.attack_range = blueprint.attack_range

        self.max_movement_range = blueprint.movement_range
        self.current_movement_range = self.max_movement_range

        self.can_attack = True
        self.is_dug_in = False
        self.dug_in_regen_amount = 10

    @property
    def player_id(self):
        return self.player.player_id

    def update(self):
        self.frame_count += 1

        if self.selected:
            self._handle_jump()
            return

        if self.game_manager.is_current_player(self.player) and (
                self.current_movement_range > 0 or self.can_attack):
            self._handle_jump()
        elif not self.is_jumping:
            pixel_coords = self.hex_tile.to_pixel(self.game_manager.board.layout).get_coords()
            self.rect.centery = pixel_coords[1]

    def _handle_jump(self):
        if not self.is_jumping and self.frame_count % self.JUMP_INTERVAL == 0:
            self.is_jumping = True
            self.jump_offset = 0
            self.jump_direction = -1

        if self.is_jumping:
            if self.jump_direction == -1:
                self.rect.centery -= self.JUMP_SPEED
                self.jump_offset += self.JUMP_SPEED

                if self.jump_offset >= self.JUMP_HEIGHT:
                    self.jump_direction = 1

            elif self.jump_direction == 1:
                self.rect.centery += self.JUMP_SPEED
                self.jump_offset -= self.JUMP_SPEED

                if self.jump_offset <= 0:
                    self.is_jumping = False
                    pixel_coords = self.hex_tile.to_pixel(self.game_manager.board.layout).get_coords()
                    self.rect.centery = pixel_coords[1]

    def take_damage(self, amount):
        self.hp -= amount
        print(f"{self} took {amount} damage. Current HP: {self.hp}")
        if self.hp <= 0:
            print(f"{self} has been killed.")
            self.die()

    def die(self):
        self.game_manager.all_units.remove(self)
        self.game_manager.military.remove(self)
        if self.player.player_id == 1:
            self.game_manager.player_1_units.remove(self)
        elif self.player.player_id == 2:
            self.game_manager.player_2_units.remove(self)
        self.player.units.remove(self)
        self.player.military.remove(self)

        if self.hex_tile:
            self.hex_tile.unit = None
            self.hex_tile = None

        super().kill()

    def attack(self, target_unit, mouse_pos):
        if not self.can_attack:
            text = 'Юнит уже атаковал в этом раунде'
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(f"{self} has already attacked this round.")
            return False

        distance = hex_utils.cube_distance(self.hex_tile, target_unit.hex_tile)
        if distance > self.attack_range:
            text = f"Вне радиуса атаки"
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(text)
            return False

        damage_dealt = max(0, self.damage + random.randint(-self.damage_spread,
                                                           self.damage_spread))
        target_unit.take_damage(damage_dealt)
        print(f"{self} attacked {target_unit} for {damage_dealt} damage.")
        self.can_attack = False
        self.current_movement_range = 0
        self.is_dug_in = False
        return True

    def move_to(self, target_tile, board, mouse_pos):
        if target_tile == self.hex_tile:
            text = "Уже в этом тайле"
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(text)
            return False

        if target_tile.unit is not None:
            text = "Тайл занят"
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(text)
            return False

        path, movement_cost = board.find_path(self.hex_tile, target_tile)
        print(path, movement_cost)
        if path:
            if movement_cost <= self.current_movement_range:
                old_tile = self.hex_tile
                old_tile.unit = None
                self.update_position(target_tile)
                self.current_movement_range -= movement_cost
                print(
                    f"Unit moved to: q={self.hex_tile.q}, r={self.hex_tile.r}, s={self.hex_tile.s}. Remaining movement: {self.current_movement_range}")
                self.is_dug_in = False
                return True
            else:
                text = (f"Для достижения цели не хватает ОД.\n"
                        f"Осталось: {self.current_movement_range}, нужно: {movement_cost}")
                self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
                print(text)
                return False
        else:
            text = "Целевой тайл недостижим"
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(text)
            return False

    def on_round_end(self):
        self.current_movement_range = self.max_movement_range
        self.can_attack = True
        if self.is_dug_in:
            self.hp = min(self.max_hp, self.hp + self.dug_in_regen_amount)

    def get_unit_info_text(self):
        attack_range_str = ""
        if self.attack_range > 1:
            attack_range_str = f"<br><font color='#AAAAAA'>Радиус атаки: {self.attack_range}</font>"

        dug_in_str = ""
        if self.is_dug_in:
            dug_in_str = "<br><font color='#00FF00'>Окопался</font>"

        return (
            f"<font color='#FFFFFF'><b>{self.blueprint.name}</b></font><br>"
            f"<font color='#AAAAAA'>ОЗ: {self.hp}/{self.max_hp}</font><br>"
            f"<font color='#AAAAAA'>Урон: {self.damage} (+/- {self.damage_spread})</font><br>"
            f"<font color='#AAAAAA'>ОД: {self.current_movement_range}/{self.max_movement_range}</font>"
            f"{attack_range_str}"
            f"{dug_in_str}"
        )

    def get_enemy_unit_info_text(self):
        attack_range_str = ""
        if self.attack_range > 1:
            attack_range_str = f"<br><font color='#AAAAAA'>Радиус атаки: {self.attack_range}</font>"

        dug_in_str = ""
        if self.is_dug_in:
            dug_in_str = "<br><font color='#00FF00'>Окопался</font>"

        return (
            f"<font color='#FF0000'><b>[ВРАГ] {self.blueprint.name}</b></font><br>"
            f"<font color='#AAAAAA'>ОЗ: {self.hp}/{self.max_hp}</font><br>"
            f"<font color='#AAAAAA'>Урон: {self.damage} (+/- {self.damage_spread})</font><br>"
            f"<font color='#AAAAAA'>ОД: {self.current_movement_range}/{self.max_movement_range}</font>"
            f"{attack_range_str}"
            f"{dug_in_str}"
        )

    def draw_health_bar(self, surface, camera):
        if self.hp != self.max_hp:
            bar_x = self.rect.centerx - self.HEALTH_BAR_WIDTH // 2 - camera.x
            bar_y = self.rect.centery + self.HEALTH_BAR_OFFSET - camera.y
            ratio = self.hp / self.max_hp
            fill_width = int(ratio * self.HEALTH_BAR_WIDTH)
            health_bar_rect = pygame.Rect(bar_x, bar_y, self.HEALTH_BAR_WIDTH, self.HEALTH_BAR_HEIGHT)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, self.HEALTH_BAR_HEIGHT)
            pygame.draw.rect(surface, (40, 40, 40), health_bar_rect)
            pygame.draw.rect(surface, (0, 200, 0), fill_rect)

    def render(self, surface, camera):
        super().render(surface, camera)
        self.draw_health_bar(surface, camera)
