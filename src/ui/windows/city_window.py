import pygame
import pygame_gui


class UICityWindow(pygame_gui.elements.UIWindow):
    def __init__(self, city, manager):
        rect = pygame.Rect(100, 100, 300, 200)  # Example position and size
        super().__init__(rect, manager, window_display_title=f"City Management: {city.hex_tile.q},{city.hex_tile.r}")
        self.city = city
        self.manager = manager
        self._create_ui_elements()

    def _create_ui_elements(self):
        self.health_label = pygame_gui.elements.UITextBox(
            f"Health: {self.city.hp}/{self.city.max_hp}",
            pygame.Rect(10, 10, 280, 50),
            manager=self.manager,
            container=self
        )

    def set_city(self, city):
        self.city = city
        self.window_display_title = f"City Management: {city.hex_tile.q},{city.hex_tile.r}"
        self.set_text()

    def set_text(self):
        self.health_label.html_text = f"Health: {self.city.hp}/{self.city.max_hp}"
        self.health_label.rebuild()

    def show(self):
        self.set_text()
        super().show()

    def hide(self):
        super().hide()

    def update(self, time_delta):
        pass
