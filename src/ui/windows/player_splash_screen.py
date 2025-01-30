import pygame
import pygame_gui


class PlayerTurnSplashScreen:
    def __init__(self, screen_width, screen_height, ui_manager):
        self.ui_manager = ui_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_visible = False
        self.player_name_text = ""

        self.panel_rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.panel_rect,
            manager=self.ui_manager,
            visible=False,
            object_id=pygame_gui.core.ObjectID(class_id="@splash_screen_panel")
        )

        self.text_line_height = 150
        self.text_rect = pygame.Rect(0, 0, screen_width, self.text_line_height)
        self.text_rect.center = (screen_width // 2, screen_height // 2)
        self.player_name_label = pygame_gui.elements.UITextBox(
            relative_rect=self.text_rect,
            html_text="",
            manager=self.ui_manager,
            container=self.panel,
            object_id=pygame_gui.core.ObjectID(class_id="@splash_screen_text")
        )

    def show(self, player_name):
        self.is_visible = True
        self.player_name_text = f"<font color=#FFFFFF>Player Turn:\n<b>{player_name}</b></font>"
        self.player_name_label.html_text = self.player_name_text
        self.player_name_label.rebuild()
        self.panel.show()

    def hide(self):
        self.is_visible = False
        self.panel.hide()

    def process_event(self, event):
        if self.is_visible:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.hide()
                return True
        return False

    def update(self, time_delta):
        if self.is_visible:
            pass

    def draw(self, surface):
        if self.is_visible:
            pass
