from src.entities.game.level_objects import City


class GameState:
    def __init__(self, game_manager, board, camera, hud_manager):
        self.game_manager = game_manager
        self.board = board
        self.camera = camera
        self.unit_info_text = hud_manager.elements['unit_info_text']

    def _reset_selection(self):
        self.game_manager.selected_unit = None
        self.game_manager.selected_building = None
        self.board.selected_tile = None
        self.board.path_to_target = []
        self.unit_info_text.html_text = "Select a unit or building to see information."
        self.unit_info_text.rebuild()
        self.board.reachable_enemy_hexes = []
        self.board.attackable_enemy_hexes = []
        self.board.highlighted_hexes = []


class SelectingUnitState(GameState):
    def handle_mouse_click(self, pos):
        clicked_tile = self.board.get_click(pos, self.camera)
        if not clicked_tile:
            print("Clicked outside the grid.")
            return

        if clicked_tile.unit:
            if self.game_manager.is_current_player(clicked_tile.unit.player):
                print(f"Clicked unit: {clicked_tile.unit}")
                self.game_manager.selected_unit = clicked_tile.unit
                self.game_manager.current_state = self.game_manager.unit_selected_state
                self.game_manager.update_ui_for_selected_unit()
                self.board.selected_tile = clicked_tile
                self.board.highlighted_hexes = self.board.get_reachable_tiles(clicked_tile.unit)
            else:
                self.game_manager.selected_unit = None
                self.game_manager.selected_building = None
                self.board.selected_tile = clicked_tile
                self.board.path_to_target = []
                self.unit_info_text.html_text = clicked_tile.unit.get_enemy_unit_info_text()
                self.unit_info_text.rebuild()
                self.board.reachable_enemy_hexes = []
                self.board.attackable_enemy_hexes = []
                self.board.highlighted_hexes = []
        elif clicked_tile.building:
            if self.game_manager.is_current_player(clicked_tile.building.player):
                print(f"Clicked building: {clicked_tile.building}")
                self.game_manager.selected_building = clicked_tile.building
                self.game_manager.current_state = self.game_manager.building_selected_state
                self.game_manager.update_ui_for_selected_building()
                self.board.selected_tile = clicked_tile
                self.board.highlighted_hexes = self.board.get_hexes_in_radius(clicked_tile,
                                                                              clicked_tile.building.attack_range)
            else:
                self.game_manager.selected_unit = None
                self.game_manager.selected_building = None
                self.board.selected_tile = clicked_tile
                self.board.path_to_target = []
                self.unit_info_text.html_text = clicked_tile.building.get_enemy_unit_info_text()
                self.unit_info_text.rebuild()
                self.board.reachable_enemy_hexes = []
                self.board.attackable_enemy_hexes = []
                self.board.highlighted_hexes = []
        else:
            self._reset_selection()


class UnitSelectedState(GameState):
    def handle_mouse_click(self, pos):
        clicked_tile = self.board.get_click(pos, self.camera)
        if not clicked_tile:
            print("Clicked outside the grid.")
            return

        selected_unit = self.game_manager.selected_unit

        if clicked_tile == selected_unit.hex_tile:
            self._reset_selection()
            self.game_manager.current_state = self.game_manager.selecting_unit_state
        elif clicked_tile.unit and clicked_tile.unit != selected_unit:
            if selected_unit.player_id != clicked_tile.unit.player_id:
                if selected_unit.attack(clicked_tile.unit, pos):
                    self._reset_selection()
                    self.game_manager.current_state = self.game_manager.selecting_unit_state
            else:
                print(f"Clicked unit: {clicked_tile.unit}")
                self.game_manager.selected_unit = clicked_tile.unit
                self.game_manager.update_ui_for_selected_unit()
                self.board.selected_tile = clicked_tile
                self.board.highlighted_hexes = self.board.get_reachable_tiles(clicked_tile.unit)
        elif clicked_tile.building and not self.game_manager.is_current_player(clicked_tile.building.player):
            if selected_unit.attack(clicked_tile.building, pos):
                self._reset_selection()
                self.game_manager.current_state = self.game_manager.selecting_unit_state
        elif not clicked_tile.unit and not clicked_tile.building:
            if selected_unit.move_to(clicked_tile, self.board, pos):
                self._reset_selection()
                self.game_manager.current_state = self.game_manager.selecting_unit_state
            else:
                self.board.path_to_target = self.board.find_path(selected_unit.hex_tile,
                                                                 clicked_tile)[0] if clicked_tile else []


class BuildingSelectedState(GameState):
    def handle_mouse_click(self, pos):
        clicked_tile = self.board.get_click(pos, self.camera)
        if not clicked_tile:
            print("Clicked outside the grid.")
            return

        selected_building = self.game_manager.selected_building

        if clicked_tile == selected_building.hex_tile:
            self._reset_selection()
            self.game_manager.current_state = self.game_manager.selecting_unit_state
        elif clicked_tile.unit and not self.game_manager.is_current_player(clicked_tile.unit.player):
            if selected_building.attack_unit(clicked_tile.unit, pos):
                self._reset_selection()
                self.game_manager.current_state = self.game_manager.selecting_unit_state
        elif clicked_tile.building and not self.game_manager.is_current_player(clicked_tile.building.player):
            if selected_building.attack_unit(clicked_tile.building, pos):
                self._reset_selection()
                self.game_manager.current_state = self.game_manager.selecting_unit_state
        else:
            self._reset_selection()
            self.game_manager.current_state = self.game_manager.selecting_unit_state
