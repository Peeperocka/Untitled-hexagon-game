import pygame
import pygame_gui


class GameOverMenu:
    def __init__(self, screen_width, screen_height, ui_manager, restart_method, exit_method):
        self.ui_manager = ui_manager
        self.restart_method = restart_method
        self.exit_method = exit_method
        self.is_visible = False

        self.window_width = 300
        self.window_height = 300
        self.window_rect = pygame.Rect(
            (screen_width - self.window_width) // 2,
            (screen_height - self.window_height) // 2,
            self.window_width,
            self.window_height
        )

        self.window = pygame_gui.elements.UIWindow(
            rect=self.window_rect,
            manager=self.ui_manager,
            window_display_title='Игра окончена',
            object_id=pygame_gui.core.ObjectID(class_id="@game_over_window")
        )
        self.window.hide()

        self.full_message_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 20), (self.window_width - 20, 100)),
            html_text="",
            manager=self.ui_manager,
            container=self.window,
            object_id=pygame_gui.core.ObjectID(class_id="@game_over_message")
        )

        self.restart_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 150), (self.window_width - 20, 40)),
            text='Заново',
            manager=self.ui_manager,
            container=self.window
        )

        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 200), (self.window_width - 20, 40)),
            text='Выход',
            manager=self.ui_manager,
            container=self.window
        )

    def show(self):
        self.is_visible = True
        self.window.show()

    def hide(self):
        self.is_visible = False
        self.window.hide()

    def process_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.restart_button:
                    self.restart_method()
                elif event.ui_element == self.exit_button:
                    self.exit_method()

    def set_message(self, message):
        self.full_message_label.html_text = message
        self.full_message_label.rebuild()
