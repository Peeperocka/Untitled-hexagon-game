import pygame
import pygame_gui

from src.utils.serialization import save_game


class PauseMenu:
    def __init__(self, screen_width, screen_height, ui_manager, game_manger, continue_callback, exit_callback):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.is_visible = False
        self.continue_callback = continue_callback
        self.exit_callback = exit_callback
        self.game_manager = game_manger

        button_width = 200
        button_height = 50
        padding = 20

        menu_rect = pygame.Rect(0, 0, button_width * 1.03, ((button_height + padding) * 3))
        menu_rect.center = screen_width // 2, screen_height // 2

        self.container = pygame_gui.elements.UIPanel(
            relative_rect=menu_rect,
            manager=self.ui_manager,
            visible=False
        )

        self.continue_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), (button_width, button_height)),
            text='Продолжить',
            manager=self.ui_manager,
            container=self.container,
            object_id="#continue_button"
        )
        self.continue_button.relative_rect.centerx = self.container.rect.width // 2

        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, button_height + padding), (button_width, button_height)),
            text='Сохранить игру',
            manager=self.ui_manager,
            container=self.container,
            object_id="#save_button"
        )
        self.save_button.relative_rect.centerx = self.container.rect.width // 2

        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 2 * (button_height + padding)), (button_width, button_height)),
            text='Выход',
            manager=self.ui_manager,
            container=self.container,
            object_id="#exit_button"
        )
        self.exit_button.relative_rect.centerx = self.container.rect.width // 2

    def process_event(self, event):
        if self.is_visible:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.continue_button:
                        self.continue_callback()
                    elif event.ui_element == self.save_button:
                        save_game(self.game_manager)
                    elif event.ui_element == self.exit_button:
                        self.exit_callback()

    def show(self):
        self.is_visible = True
        self.container.show()

    def hide(self):
        self.is_visible = False
        self.container.hide()
