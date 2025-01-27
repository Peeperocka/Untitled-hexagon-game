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

        self.money = 0

    def __str__(self):
        return f"Player {self.player_id}"


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

    def next_player(self):
        if self.game_over:
            return

        self.players_to_remove = []
        for player in self.players:
            if not player.military:
                print(f"{player} has lost the game_core!")
                self.players_to_remove.append(player)

        if len(self.players) <= 1:
            self.game_over = True
            if self.players:
                print(f"Game Over! {self.players[0]} is the winner!")
            else:
                print("Game Over! It's a draw (no players left).")
            return

        for player in self.players:
            for unit in player.units:
                unit.selected = False
        self.board.highlighted_hexes = []
        self.selected_unit = None
        self.current_state = self.selecting_unit_state

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print('=' * 50)

        print(f"It's {self.get_current_player()}'s turn.")

        if self.current_player_index == 0 and len(
                self.players) > 1:
            self.end_round()
            return

    def get_current_player(self):
        return self.players[self.current_player_index]

    def is_current_player(self, player):
        return player == self.get_current_player()

    def end_round(self):
        print(f"--- End of Round {self.current_round} ---")

        for player in self.players_to_remove:
            self.players.remove(player)

        for player in self.players:
            for unit in player.units:
                unit.on_round_end()
            for building in player.buildings:
                building.on_round_end()

        self.current_round += 1
        print(f"--- Starting Round {self.current_round} ---")
        print(f"It's {self.get_current_player()}'s turn.")

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
                        City) and self.get_current_player() == self.board.selected_tile.building.player:
                    city = self.board.selected_tile.building
                    self.hud_manager.open_city_window(city)
                    self.selected_building = city
                    self.current_state = self.building_selected_state
                    self.update_ui_for_selected_building()
                    self.board.highlighted_hexes = self.board.get_hexes_in_radius(
                        city.hex_tile,
                        city.attack_range
                    )
