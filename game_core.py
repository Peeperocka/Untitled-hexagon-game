import cProfile
import pstats

import pygame
import pygame_gui

from board import HexBoard
from camera import Camera
from units import *


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.units = pygame.sprite.Group()
        self.all_objects = pygame.sprite.Group()
        self.military = pygame.sprite.Group()

    def __str__(self):
        return f"Player {self.player_id}"


class GameManager:
    def __init__(self, players, board, camera, ui_manager, unit_info_text):
        self.players = list(players)
        self.current_player_index = 0
        self.current_round = 1
        self.board = board
        self.camera = camera
        self.ui_manager = ui_manager
        self.unit_info_text = unit_info_text
        self.selected_unit = None

        self.all_sprites = pygame.sprite.Group()
        self.all_units = pygame.sprite.Group()
        self.military = pygame.sprite.Group()
        self.player_1_units = pygame.sprite.Group()
        self.player_2_units = pygame.sprite.Group()

        self.selecting_unit_state = SelectingUnitState(self, board, camera, ui_manager, unit_info_text)
        self.unit_selected_state = UnitSelectedState(self, board, camera, ui_manager, unit_info_text)
        self.current_state = self.selecting_unit_state
        self.game_over = False

    def next_player(self):
        if self.game_over:
            return

        self.players_to_remove = []
        for player in self.players:
            if not player.military:
                print(f"{player} has lost the game!")
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
        self.current_round += 1
        print(f"--- Starting Round {self.current_round} ---")
        print(f"It's {self.get_current_player()}'s turn.")

    def process_mouse_click(self, pos):
        if not self.game_over:
            self.current_state.handle_mouse_click(pos)

    def update_ui_for_selected_unit(self):
        if self.selected_unit:
            self.unit_info_text.html_text = self.selected_unit.get_unit_info_text()
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            for other_unit in self.all_units:
                if other_unit.player_id != self.selected_unit.player_id:
                    distance = hex_utils.cube_distance(self.selected_unit.hex_tile, other_unit.hex_tile)
                    if distance <= self.selected_unit.current_movement_range:
                        self.board.enemy_reachable_hexes.append(other_unit)
                    if distance <= self.selected_unit.attack_range:
                        self.board.enemy_attackable_hexes.append(other_unit)
        else:
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []


class GameState:
    def __init__(self, game_manager, board, camera, ui_manager, unit_info_text):
        self.game_manager = game_manager
        self.board = board
        self.camera = camera
        self.ui_manager = ui_manager
        self.unit_info_text = unit_info_text

    def handle_mouse_click(self, pos):
        raise NotImplementedError("Subclasses must implement this method")


class SelectingUnitState(GameState):
    def handle_mouse_click(self, pos):
        clicked_tile = self.board.get_click(pos, self.camera)
        if not clicked_tile:
            print("Clicked outside the grid.")
            return

        if clicked_tile.unit and self.game_manager.is_current_player(clicked_tile.unit.player):
            print(f"Clicked unit: {clicked_tile.unit}")
            self.game_manager.selected_unit = clicked_tile.unit
            self.game_manager.current_state = self.game_manager.unit_selected_state
            self.game_manager.update_ui_for_selected_unit()
            self.board.selected_tile = clicked_tile
            self.board.highlighted_hexes = list(self.board.get_reachable_tiles(clicked_tile.unit))
        elif clicked_tile.unit:
            self.game_manager.selected_unit = None
            self.board.selected_tile = clicked_tile
            self.board.path_to_target = []
            self.unit_info_text.html_text = clicked_tile.unit.get_enemy_unit_info_text()
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
        else:
            self.game_manager.selected_unit = None
            self.board.selected_tile = clicked_tile
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            self.board.highlighted_hexes = []


class UnitSelectedState(GameState):
    def handle_mouse_click(self, pos):
        clicked_tile = self.board.get_click(pos, self.camera)
        if not clicked_tile:
            print("Clicked outside the grid.")
            return

        selected_unit = self.game_manager.selected_unit

        if clicked_tile == selected_unit.hex_tile:
            self.game_manager.selected_unit = None
            self.game_manager.current_state = self.game_manager.selecting_unit_state
            self.board.selected_tile = None
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            self.board.highlighted_hexes = []
        elif clicked_tile.unit and clicked_tile.unit != selected_unit and clicked_tile.unit.player_id != selected_unit.player_id:
            if selected_unit.attack(clicked_tile.unit):
                self.game_manager.selected_unit = None
                self.game_manager.current_state = self.game_manager.selecting_unit_state
                self.board.selected_tile = None
                self.board.path_to_target = []
                self.unit_info_text.html_text = "Select a unit to see information."
                self.unit_info_text.rebuild()
                self.board.enemy_reachable_hexes = []
                self.board.enemy_attackable_hexes = []
                self.board.highlighted_hexes = []
        elif selected_unit.move_to(clicked_tile, self.board):
            self.game_manager.selected_unit = None
            self.game_manager.current_state = self.game_manager.selecting_unit_state
            self.board.selected_tile = None
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.enemy_reachable_hexes = []
            self.board.enemy_attackable_hexes = []
            self.board.highlighted_hexes = []
        else:
            self.board.path_to_target = self.board.find_path(selected_unit.hex_tile,
                                                             clicked_tile) if clicked_tile else []
