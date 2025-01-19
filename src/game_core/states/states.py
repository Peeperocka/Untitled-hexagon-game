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
            self.board.highlighted_hexes = self.board.get_reachable_tiles(clicked_tile.unit)
        elif clicked_tile.unit:
            self.game_manager.selected_unit = None
            self.board.selected_tile = clicked_tile
            self.board.path_to_target = []
            self.unit_info_text.html_text = clicked_tile.unit.get_enemy_unit_info_text()
            self.unit_info_text.rebuild()
            self.board.reachable_enemy_hexes = []
            self.board.attackable_enemy_hexes = []
        else:
            self.game_manager.selected_unit = None
            self.board.selected_tile = clicked_tile
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.reachable_enemy_hexes = []
            self.board.attackable_enemy_hexes = []
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
            self.board.reachable_enemy_hexes = []
            self.board.attackable_enemy_hexes = []
            self.board.highlighted_hexes = []
        elif clicked_tile.unit and clicked_tile.unit != selected_unit and clicked_tile.unit.player_id != selected_unit.player_id:
            if selected_unit.attack(clicked_tile.unit, pos):
                self.game_manager.selected_unit = None
                self.game_manager.current_state = self.game_manager.selecting_unit_state
                self.board.selected_tile = None
                self.board.path_to_target = []
                self.unit_info_text.html_text = "Select a unit to see information."
                self.unit_info_text.rebuild()
                self.board.reachable_enemy_hexes = []
                self.board.attackable_enemy_hexes = []
                self.board.highlighted_hexes = []
        elif selected_unit.move_to(clicked_tile, self.board, pos):
            self.game_manager.selected_unit = None
            self.game_manager.current_state = self.game_manager.selecting_unit_state
            self.board.selected_tile = None
            self.board.path_to_target = []
            self.unit_info_text.html_text = "Select a unit to see information."
            self.unit_info_text.rebuild()
            self.board.reachable_enemy_hexes = []
            self.board.attackable_enemy_hexes = []
            self.board.highlighted_hexes = []
        else:
            self.board.path_to_target = self.board.find_path(selected_unit.hex_tile,
                                                             clicked_tile)[0] if clicked_tile else []
