import os
import sys

import pygame
import pygame_gui

from src.ui.windows.city_window import UICityWindow
from src.ui.windows.game_over_menu import GameOverMenu
from src.ui.windows.game_pause import PauseMenu
from src.ui.windows.player_splash_screen import PlayerTurnSplashScreen
from src.utils.utils import load_image


class ResourceDisplay:
    def __init__(self, resource_type, initial_amount, position, ui_manager):
        self.resource_type = resource_type
        self.amount = initial_amount
        self.position = position
        self.ui_manager = ui_manager
        self.padding = 5

        image_path = os.path.join('icons', f'{resource_type}.png')
        try:
            self.image_surface = load_image(image_path)
            self.image_surface = pygame.transform.scale(self.image_surface, (30, 30))
        except ValueError:
            self.image_surface = pygame.Surface((20, 20))
            self.image_surface.fill('gray')
        self.image_rect = self.image_surface.get_rect(topleft=position)

        self.text_rect = pygame.Rect(
            self.image_rect.topright,
            (120, self.image_rect.height),
        )
        self.text_rect.x += self.padding
        self.amount_label = pygame_gui.elements.UITextBox(
            relative_rect=self.text_rect,
            html_text=self._format_resource_text(self.amount, 0),
            manager=self.ui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="@resource_amount_label"),
        )

    def _format_resource_text(self, amount, change):
        """Formats the resource text to include amount and change."""
        change_str = ""
        if change > 0:
            change_str = f'<font color=#00FF00> (+{change})</font>'
        elif change < 0:
            change_str = f'<font color=#FF0000> ({change})</font>'
        return f'{amount}{change_str}'

    def update_amount(self, new_amount, income, expense):
        """Updates the displayed amount and resource change."""
        self.amount = new_amount
        change = income - expense
        self.amount_label.html_text = self._format_resource_text(self.amount, change)
        self.amount_label.rebuild()

    def draw(self, surface):
        surface.blit(self.image_surface, self.image_rect)


# noinspection PyTypeChecker
class DynamicMessageManager:
    def __init__(self, font):
        self.messages = pygame.sprite.Group()
        self.font = font
        self.color = pygame.Color('white')

    def create_message(self, text, position=None):
        if not position:
            position = pygame.mouse.get_pos()
        message = FloatingMessage(text, position, self.font, self.color)
        self.messages.add(message)

    def update(self, time_delta):
        self.messages.update(time_delta)

    def draw(self, surface):
        self.messages.draw(surface)


class FloatingMessage(pygame.sprite.Sprite):
    def __init__(self, text, position, font, color, lifespan=3.0, speed=(0, -10)):
        super().__init__()
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(topleft=position)
        self.font = font
        self.color = color
        self.lifespan = lifespan
        self.time_alive = 0
        self.speed = speed

    def update(self, time_delta):
        self.time_alive += time_delta
        self.rect.x += self.speed[0] * time_delta
        self.rect.y += self.speed[1] * time_delta
        self.image.set_alpha(int(255 * (1 - self.time_alive / self.lifespan)))
        if self.time_alive >= self.lifespan:
            self.kill()


class MenuButton:
    def __init__(self, screen_width, screen_height, ui_manager, menu_open_method):
        self.ui_manager = ui_manager
        self.menu_open_method = menu_open_method
        self.button_width = 100
        self.button_height = 50
        self.button_rect = pygame.Rect(screen_width - self.button_width - 10,
                                       10,
                                       self.button_width,
                                       self.button_height)
        self.button = pygame_gui.elements.UIButton(relative_rect=self.button_rect,
                                                   text='Menu',
                                                   manager=self.ui_manager)

    def process_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.button:
                    self.menu_open_method()


class HUDManager:
    def __init__(self, screen_width, screen_height, font, restart_game_method):
        self.font = font
        self.restart_game_method = restart_game_method

        self.ui_manager = pygame_gui.UIManager((screen_width, screen_height),
                                               os.path.join('data', 'theme', 'game_theme.json'))
        self.dynamic_message_manager = DynamicMessageManager(self.font)
        self.elements = {}
        self.city_window = None
        self.is_paused = False
        self.game_over_menu = None
        self.splash_screen = PlayerTurnSplashScreen(
            screen_width, screen_height, self.ui_manager)

        self._create_default_elements(screen_width, screen_height)
        self._create_menu_button(screen_width, screen_height)
        self._create_pause_menu(screen_width, screen_height)
        self._create_resource_displays()
        self._create_game_over_menu(screen_width, screen_height)

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dim_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.dim_surface.fill((0, 0, 0, 128))

    def _create_resource_displays(self):
        """Creates resource icons and counters in the top-left corner."""
        resource_types = ['gold', 'stone', 'wood', 'metal', 'food']
        start_x = 10
        start_y = 10
        offset_x = 160

        self.resource_displays = {}
        for i, res_type in enumerate(resource_types):
            x_pos = start_x + i * offset_x
            res_display = ResourceDisplay(res_type, 100, (x_pos, start_y), self.ui_manager)
            self.resource_displays[res_type] = res_display

    def update_resource_values(self, resources: dict, income: dict, expense: dict):
        """Updates the displayed resource values and changes.

        Args:
            resources (dict): A dictionary where keys are resource types and values are their amounts.
            income (dict): A dictionary of resource income.
            expense (dict): A dictionary of resource expenses.
        """
        for res_type, amount in resources.items():
            if res_type in self.resource_displays:
                self.resource_displays[res_type].update_amount(amount, income.get(res_type, 0),
                                                               expense.get(res_type, 0))

    def _create_default_elements(self, screen_width, screen_height):
        unit_info_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((screen_width - 300,
                                       screen_height - 200), (280, 180)),
            manager=self.ui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="@unit_info_panel")
        )
        self.elements['unit_info_panel'] = unit_info_panel

        unit_info_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 10), (260, 160)),
            html_text="Select a unit to see information.",
            manager=self.ui_manager,
            container=unit_info_panel,
            object_id=pygame_gui.core.ObjectID(class_id="@unit_info_text")
        )
        self.elements['unit_info_text'] = unit_info_text

    def _create_menu_button(self, screen_width, screen_height):
        menu_button = MenuButton(screen_width, screen_height, self.ui_manager, self.toggle_pause_menu)
        self.elements['menu_button'] = menu_button

    def _create_pause_menu(self, screen_width, screen_height):
        self.pause_menu = PauseMenu(screen_width, screen_height, self.ui_manager,
                                    self.unpause_game, self.save_game, self.exit_game)

    def _create_game_over_menu(self, screen_width, screen_height):
        self.game_over_menu = GameOverMenu(screen_width, screen_height, self.ui_manager,
                                           self.restart_game, self.exit_game)

    def toggle_pause_menu(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_menu.show()
        else:
            self.pause_menu.hide()

    def unpause_game(self):
        print("Unpausing the game")
        self.is_paused = False
        self.pause_menu.hide()

    def save_game(self):
        print("Saving the game")

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def restart_game(self):
        self.is_paused = False
        self.game_over_menu.hide()
        self.restart_game_method()

    def process_event(self, event):
        self.ui_manager.process_events(event)
        if 'menu_button' in self.elements:
            self.elements['menu_button'].process_event(event)
        if self.is_paused:
            self.pause_menu.process_event(event)
        if self.game_over_menu.is_visible:
            self.game_over_menu.process_event(event)
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if self.city_window is not None and event.ui_element == self.city_window:
                self.close_city_window_internal()
        if self.splash_screen.is_visible:
            if self.splash_screen.process_event(event):
                return

    def update(self, time_delta):
        self.ui_manager.update(time_delta)
        self.dynamic_message_manager.update(time_delta)
        if self.city_window is not None and self.city_window.visible:
            self.city_window.update(time_delta)
        self.splash_screen.update(time_delta)

    def draw(self, surface):
        if self.is_paused or self.game_over_menu.is_visible or self.splash_screen.is_visible:
            surface.blit(self.dim_surface, (0, 0))
        self.ui_manager.draw_ui(surface)
        self.dynamic_message_manager.draw(surface)
        for res_display in self.resource_displays.values():
            res_display.draw(surface)
        self.splash_screen.draw(surface)

    def set_unit_info_text(self, text):
        if 'unit_info_text' in self.elements:
            self.elements['unit_info_text'].html_text = text
            self.elements['unit_info_text'].rebuild()

    def add_element(self, element_id, element):
        self.elements[element_id] = element

    def get_element(self, element_id):
        return self.elements.get(element_id)

    def remove_element(self, element_id):
        if element_id in self.elements:
            self.elements[element_id].kill()
            del self.elements[element_id]

    def open_city_window(self, city):
        """Opens the city management window."""
        if self.city_window is None:
            self.city_window = UICityWindow(city, self.ui_manager, self.screen_width, self.screen_height)
        else:
            self.city_window.set_city(city)
        self.city_window.show()
        self.is_paused = True

    def close_city_window(self):
        """Closes the city management window."""
        if self.city_window is not None:
            self.city_window.hide()
            self.update_is_paused_from_menus()

    def close_city_window_internal(self):
        """Internal method to close the city window and reset the attribute."""
        self.close_city_window()
        self.city_window = None

    def update_is_paused_from_menus(self):
        """Updates is_paused based on the visibility of both menus."""
        self.is_paused = self.pause_menu.is_visible or (self.city_window is not None and self.city_window.visible)

    def show_game_over_menu(self, message):
        self.is_paused = True
        self.game_over_menu.set_message(message)
        self.game_over_menu.show()

    def show_player_turn_splash_screen(self, player_name):
        """Shows the player turn splash screen."""
        self.splash_screen.show(player_name)

    def hide_player_turn_splash_screen(self):
        """Hides the player turn splash screen."""
        self.splash_screen.hide()
