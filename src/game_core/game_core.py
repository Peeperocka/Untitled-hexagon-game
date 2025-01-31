import pygame

from src.entities.game.level_objects import City
from src.game_core.states.states import SelectingUnitState, UnitSelectedState, BuildingSelectedState


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.units = pygame.sprite.Group()
        self.all_objects = pygame.sprite.Group()
        self.military = pygame.sprite.Group()
        self.buildings = pygame.sprite.Group()

        self.resources = {
            "gold": 2000,
            "wood": 2000,
            "stone": 2000,
            "metal": 0,
            "food": 20,
        }

        self.income = {
            "gold": 0,
            "wood": 0,
            "stone": 0,
            "metal": 0,
            "food": 0,
        }

        self.expense = {
            "gold": 0,
            "wood": 0,
            "stone": 0,
            "metal": 0,
            "food": 0,
        }

        self.money = 0

        self.camera_x = 0
        self.camera_y = 0
        self.score = 0

        self.has_first_city_bonus = False

    def __str__(self):
        return f"Player {self.player_id}"

    def calculate_score(self):
        self.score = 0

        city_count = 0
        for building in self.buildings:
            if isinstance(building, City):
                city_count += 1
        self.score += city_count * 100

        self.score += len(self.units) * 5

        total_resources_collected = sum(
            self.resources.values())
        self.score += total_resources_collected // 10

        improvement_count = 0
        for building in self.buildings:
            if isinstance(building, City):
                improvement_count += len(building.city_improvements)
        self.score += improvement_count * 50

        if city_count > 0 and not self.has_first_city_bonus:
            self.score += 200
            self.has_first_city_bonus = True

        return self.score


class GameManager:
    def __init__(self, players, board, camera, hud_manager):
        self.selected_building = None
        self.players = list(players)
        self.current_player_index = 0
        self.current_round = 1
        self.board = board
        self.camera = camera
        self.hud_manager = hud_manager
        self.ui_manager = self.hud_manager.ui_manager
        self.selected_unit = None
        self.city_window = None

        self.all_sprites = pygame.sprite.Group()
        self.all_units = pygame.sprite.Group()
        self.military = pygame.sprite.Group()
        self.player_1_units = pygame.sprite.Group()
        self.player_2_units = pygame.sprite.Group()

        self.players_to_remove = []

        self.selecting_unit_state = SelectingUnitState(self, board, camera, self.hud_manager)
        self.unit_selected_state = UnitSelectedState(self, board, camera, self.hud_manager)
        self.building_selected_state = BuildingSelectedState(self, board, camera, self.hud_manager)

        self.current_state = self.selecting_unit_state
        self.game_over = False
        self.game_over_message = ""

        self.update_player_resources()
        print(f"It's {self.get_current_player()}'s turn.")

    def next_player(self):
        """Advances the game to the next player's turn and ends round if necessary."""
        if self.game_over:
            return

        current_player = self.get_current_player()
        if current_player:
            current_player.camera_x = self.camera.x
            current_player.camera_y = self.camera.y

        for player in self.players:
            for unit in player.units:
                unit.selected = False
        self.board.highlighted_hexes = []
        self.selected_unit = None
        self.current_state = self.selecting_unit_state

        if (self.current_player_index + 1) % len(self.players) == 0:
            self.end_round()
            if self.game_over:
                return

        if self.players:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if self.current_player_index >= len(self.players):
                self.current_player_index = 0
            next_player = self.get_current_player()
            if next_player:
                self.camera.x = next_player.camera_x
                self.camera.y = next_player.camera_y
        else:
            return

        print('=' * 50)
        if self.players:
            self.hud_manager.show_player_turn_splash_screen(self.get_current_player())
            print(f"It's {self.get_current_player()}'s turn.")
            self.update_player_resources()

    def get_current_player(self):
        if self.players:
            return self.players[self.current_player_index]
        return None

    def is_current_player(self, player):
        current_player = self.get_current_player()
        return current_player is not None and player == current_player

    def end_round(self):
        """Ends the current round and initiates the next round."""
        print(f"--- End of Round {self.current_round} ---")

        self.players_to_remove = []
        for player in self.players:
            if not player.military:
                self.players_to_remove.append(player)
                print(f"{player} has lost the game!")

        for player in self.players_to_remove:
            if self.current_player_index >= len(self.players):
                self.current_player_index = 0
            self.players.remove(player)
            if self.current_player_index >= len(self.players):
                self.current_player_index = 0

        if len(self.players) <= 1:
            self.game_over = True
            if self.players:
                winner = self.players[0]
                self.game_over_message = f"Игра окончена! {winner} - победитель!"
                print(f"Игра окончена! {winner} - победитель!")

                player_scores = {}
                for p in self.players:
                    player_score = p.calculate_score()
                    player_scores[p.player_id] = player_score
                    print(f"Очки игрока {p.player_id}: {player_score}")

                self.player_scores = player_scores
                self.hud_manager.show_game_over_menu(self.game_over_message, player_scores)

            else:
                self.game_over_message = "Игра окончена! Ничья (не осталось игроков)."
                print("Игра окончена! Ничья (не осталось игроков).")
                self.player_scores = {}
                self.hud_manager.show_game_over_menu(self.game_over_message, {})
            return

        for player in self.players:
            for unit in player.units:
                unit.on_round_end()
            for building in player.buildings:
                building.on_round_end()

        self.current_round += 1
        print(f"--- Starting Round {self.current_round} ---")

    def update_player_resources(self):
        current_player = self.get_current_player()
        if not current_player:
            return

        current_player.income = {
            "gold": 0,
            "wood": 0,
            "stone": 0,
            "metal": 0,
            "food": 0,
        }
        current_player.expense = {
            "gold": 0,
            "wood": 0,
            "stone": 0,
            "metal": 0,
            "food": 0,
        }

        player_food_production = 0
        player_gold_income = 0
        player_stone_income = 0

        for building in current_player.buildings:
            player_food_production += building.food_production
            player_gold_income += building.gold_income
            player_stone_income += building.stone_income
            building.apply_city_improvement_effects()

        unit_food_consumption = len(current_player.units)
        current_player.expense["food"] += unit_food_consumption

        for res_type in current_player.resources:
            current_player.resources[res_type] += current_player.income[res_type] - current_player.expense[res_type]
            current_player.resources[res_type] = max(0, current_player.resources[
                res_type])

        print(f"{current_player} resources at the start of turn (Round {self.current_round}):")
        print(
            f"  Food: {current_player.resources['food']} (+{current_player.income['food']} - {current_player.expense['food']})")
        print(
            f"  Gold: {current_player.resources['gold']} (+{current_player.income['gold']} - {current_player.expense['gold']})")
        print(
            f"  Stone: {current_player.resources['stone']} (+{current_player.income['stone']} - {current_player.expense['stone']})")
        print(f"  Wood: {current_player.resources['wood']}")
        print(f"  Metal: {current_player.resources['metal']}")

        self.hud_manager.update_resource_values(current_player.resources, current_player.income, current_player.expense)

    def process_mouse_click(self, pos):
        if not self.game_over:
            self.current_state.handle_mouse_click(pos)

    def update_ui_for_selected_unit(self):
        if self.selected_unit:
            self.hud_manager.elements['unit_info_text'].html_text = self.selected_unit.get_unit_info_text()
            self.hud_manager.elements['unit_info_text'].rebuild()
            self.board.reachable_enemy_hexes = self.board.get_reachable_tiles(
                self.selected_unit,
                self.selected_unit.current_movement_range,
                True, True)
            for hex in self.board.reachable_enemy_hexes.copy():
                if hex.unit and self.is_current_player(hex.unit.player):
                    self.board.reachable_enemy_hexes.remove(hex)
                    continue
                elif hex.building and self.is_current_player(hex.building.player):
                    self.board.reachable_enemy_hexes.remove(hex)
                    continue
                elif not hex.unit and not hex.building:
                    self.board.reachable_enemy_hexes.remove(hex)
                    continue

            self.board.attackable_enemy_hexes = self.board.get_hexes_in_radius(self.selected_unit.hex_tile,
                                                                               self.selected_unit.attack_range)

            for hex in self.board.attackable_enemy_hexes.copy():
                if hex.unit and self.is_current_player(hex.unit.player):
                    self.board.attackable_enemy_hexes.remove(hex)
                    continue
                elif hex.building and self.is_current_player(hex.building.player):
                    self.board.attackable_enemy_hexes.remove(hex)
                    continue
                elif not hex.unit and not hex.building:
                    self.board.attackable_enemy_hexes.remove(hex)
                    continue

        else:
            self.hud_manager.elements['unit_info_text'].html_text = "Select a unit to see information."
            self.hud_manager.elements['unit_info_text'].rebuild()
            self.board.reachable_enemy_hexes = []
            self.board.attackable_enemy_hexes = []

    def update_ui_for_selected_building(self):
        if self.selected_building:
            self.hud_manager.elements['unit_info_text'].html_text = self.selected_building.get_unit_info_text()
            self.hud_manager.elements['unit_info_text'].rebuild()

            self.board.attackable_enemy_hexes = self.board.get_hexes_in_radius(
                self.selected_building.hex_tile,
                self.selected_building.attack_range
            )

            for hex in self.board.attackable_enemy_hexes.copy():
                if hex.unit and self.is_current_player(hex.unit.player):
                    self.board.attackable_enemy_hexes.remove(hex)
                elif hex.building and self.is_current_player(hex.building.player):
                    self.board.attackable_enemy_hexes.remove(hex)
                elif not hex.unit and not hex.building:
                    self.board.attackable_enemy_hexes.remove(hex)

        else:
            self.hud_manager.elements['unit_info_text'].html_text = "Select a unit or building to see information."
            self.hud_manager.elements['unit_info_text'].rebuild()
            self.board.reachable_enemy_hexes = []
            self.board.attackable_enemy_hexes = []

    def deselect_unit(self):
        if self.selected_unit:
            self.selected_unit.selected = False
            self.selected_unit = None
            self.board.clear_selected_tiles()
            self.update_ui_for_selected_unit()
            self.current_state = self.selecting_unit_state

    def deselect_building(self):
        if self.selected_building:
            self.selected_building = None
            self.board.clear_selected_tiles()
            self.update_ui_for_selected_building()
            self.current_state = self.selecting_unit_state

    def process_key_press(self, event):
        if not self.game_over:
            if event.key == pygame.K_q:
                if self.board.selected_tile and self.board.selected_tile.building and isinstance(
                        self.board.selected_tile.building,
                        City) and self.is_current_player(self.board.selected_tile.building.player):
                    city = self.board.selected_tile.building
                    self.hud_manager.open_city_window(city)
                    self.selected_building = city
                    self.current_state = self.building_selected_state
                    self.update_ui_for_selected_building()
                    self.board.highlighted_hexes = self.board.get_hexes_in_radius(
                        city.hex_tile,
                        city.attack_range
                    )
            if event.key == pygame.K_g:
                if self.selected_unit and self.is_current_player(self.selected_unit.player):
                    if self.selected_unit.can_attack and not self.selected_unit.is_dug_in:
                        self.selected_unit.is_dug_in = True
                        self.selected_unit.can_attack = False
                        self.selected_unit.current_movement_range = 0
                        text = f"{self.selected_unit.blueprint.name} окопался!"
                        self.hud_manager.dynamic_message_manager.create_message(text, self.selected_unit.rect.center)
                        self.deselect_unit()
                        print(text)
                        self.update_ui_for_selected_unit()
                    elif self.selected_unit.is_dug_in:
                        text = f"{self.selected_unit.blueprint.name} уже окопался!"
                        self.hud_manager.dynamic_message_manager.create_message(text, self.selected_unit.rect.center)
                        print(text)
                    elif not self.selected_unit.can_attack:
                        text = f"{self.selected_unit.blueprint.name} не может окопаться т/к атаковал!"
                        self.hud_manager.dynamic_message_manager.create_message(text, self.selected_unit.rect.center)
                        print(text)
