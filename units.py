import random

import pygame

import hex_utils
from utils import load_image


class GameObject(pygame.sprite.Sprite):
    def __init__(self, hex_tile, image_path, size, game_manager):
        super().__init__(game_manager.all_sprites)
        self.game_manager = game_manager
        self.hex_tile = hex_tile
        self.image = pygame.transform.scale(load_image(image_path), size)
        self.rect = self.image.get_rect()
        self.base_y = 0
        self.update_position(hex_tile)

    def update_position(self, hex_tile):
        self.hex_tile = hex_tile
        self.hex_tile.unit = self
        pixel_coords = self.hex_tile.to_pixel(self.game_manager.board.layout).get_coords()
        self.rect.center = pixel_coords
        self.base_y = self.rect.centery

    def render(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))


class Unit(GameObject):
    def __init__(self, hex_tile, image_path, size, player, game_manager, damage, damage_spread, hp, movement_range,
                 attack_range):
        super().__init__(hex_tile, image_path, size, game_manager)
        self.player = player
        game_manager.all_units.add(self)
        game_manager.military.add(self)
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

        self.damage = damage
        self.damage_spread = damage_spread
        self.hp = hp
        self.max_hp = hp
        self.max_movement_range = movement_range
        self.current_movement_range = movement_range
        self.can_attack = True
        self.attack_range = attack_range

    @property
    def player_id(self):
        return self.player.player_id

    def update(self):
        self.frame_count += 1

        if self.selected:
            self._handle_jump()
            return

        if self.game_manager.is_current_player(self.player) and (self.current_movement_range > 0 or self.can_attack):
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
            text = 'Unit has already attacked this round.'
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(f"{self} has already attacked this round.")
            return False
        if not isinstance(target_unit, Unit):
            raise ValueError("Target must be an instance of Unit.")

        distance = hex_utils.cube_distance(self.hex_tile, target_unit.hex_tile)
        if distance > self.attack_range:
            print(f"{target_unit} is out of attack range.")
            return False

        damage_dealt = max(0, self.damage + random.randint(-self.damage_spread, self.damage_spread))
        target_unit.take_damage(damage_dealt)
        print(f"{self} attacked {target_unit} for {damage_dealt} damage.")
        self.can_attack = False
        self.current_movement_range = 0
        return True

    def move_to(self, target_tile, board, mouse_pos):
        if target_tile == self.hex_tile:
            text = "Already on this tile."
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(text)
            return False

        if target_tile.unit is not None:
            text = "Tile is occupied."
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
                return True
            else:
                text = (f"Not enough movement range to reach the target.\n"
                        f"Remaining: {self.current_movement_range}, needed: {movement_cost}")
                self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
                print(text)
                return False
        else:
            text = "Target tile is unreachable."
            self.game_manager.hud_manager.dynamic_message_manager.create_message(text, mouse_pos)
            print(text)
            return False

    def on_round_end(self):
        self.current_movement_range = self.max_movement_range
        self.can_attack = True

    def get_unit_info_text(self):
        return (
            f"<font color='#FFFFFF'><b>{type(self).__name__}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}</font><br>"
            f"<font color='#AAAAAA'>Damage: {self.damage} (+/- {self.damage_spread})</font><br>"
            f"<font color='#AAAAAA'>Movement: {self.current_movement_range}/{self.max_movement_range}</font>"
        )

    def get_enemy_unit_info_text(self):
        return (
            f"<font color='#FF0000'><b>[ENEMY] {type(self).__name__}</b></font><br>"
            f"<font color='#AAAAAA'>HP: {self.hp}</font><br>"
            f"<font color='#AAAAAA'>Damage: {self.damage} (+/- {self.damage_spread})</font><br>"
            f"<font color='#AAAAAA'>Movement: {self.current_movement_range}/{self.max_movement_range}</font>"
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


class Warrior(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "warrior.png", (70, 70), player, game_manager, damage=30, damage_spread=7, hp=100,
                         movement_range=5, attack_range=1)


class Cavalry(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "cavalry.png", (70, 70), player, game_manager, damage=35, damage_spread=6, hp=90,
                         movement_range=4, attack_range=2)


class Archer(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "archer.png", (70, 70), player, game_manager, damage=25, damage_spread=10, hp=70,
                         movement_range=3, attack_range=5)


class Crossbowman(Unit):
    def __init__(self, hex_tile, player, game_manager):
        super().__init__(hex_tile, "crossbowman.png", (70, 70), player, game_manager, damage=30, damage_spread=6, hp=75,
                         movement_range=3, attack_range=6)
