import pygame
import pygame_gui


class UICityWindow(pygame_gui.elements.UIWindow):
    def __init__(self, city, manager, screen_width, screen_height):
        window_width = screen_width * 0.6
        window_height = screen_height * 0.6
        window_x = screen_width * 0.2
        window_y = screen_height * 0.2

        rect = pygame.Rect(window_x, window_y, window_width, window_height)
        super().__init__(rect, manager, window_display_title=f"City Management: {city.hex_tile.q},{city.hex_tile.r}")
        self.city = city
        self.manager = manager
        self.current_category = "info"
        self._create_ui_elements()
        self._update_content()

    def _create_ui_elements(self):
        category_button_height = 30
        category_button_margin = 5
        category_buttons_width_percentage = 0.30
        available_button_width = self.rect.width - 20
        category_button_width = available_button_width * category_buttons_width_percentage - category_button_margin
        start_x = 10
        button_y = 10

        self.info_button = pygame_gui.elements.UIButton(
            pygame.Rect(start_x, button_y, category_button_width, category_button_height),
            "Информация",
            manager=self.manager,
            container=self,
            object_id="#category_button",
        )
        start_x += category_button_width + category_button_margin

        self.city_build_button = pygame_gui.elements.UIButton(
            pygame.Rect(start_x, button_y, category_button_width, category_button_height),
            "Строительство города",
            manager=self.manager,
            container=self,
            object_id="#category_button",
        )
        start_x += category_button_width + category_button_margin

        self.unit_build_button = pygame_gui.elements.UIButton(
            pygame.Rect(start_x, button_y, category_button_width, category_button_height),
            "Строительство юнитов",
            manager=self.manager,
            container=self,
            object_id="#category_button",
        )

        self.info_panel = pygame_gui.elements.UIPanel(
            pygame.Rect(10, button_y + category_button_height + 10, self.rect.width - 20,
                        self.rect.height - (button_y + category_button_height + 20)),
            0,
            manager=self.manager,
            container=self,
            visible=False,
            object_id="#info_panel"
        )
        self.info_text_box = pygame_gui.elements.UITextBox(
            "",
            pygame.Rect(0, 0, self.info_panel.relative_rect.width, self.info_panel.relative_rect.height),
            manager=self.manager,
            container=self.info_panel,
            object_id="#info_text_box"
        )

        self.build_options_panel = pygame_gui.elements.UIScrollingContainer(
            pygame.Rect(10, button_y + category_button_height + 10, self.rect.width - 20,
                        self.rect.height - (button_y + category_button_height + 20)),
            manager=self.manager,
            container=self,
            visible=False,
            object_id="#build_options_panel"
        )
        self.build_options_container = self.build_options_panel.get_container()

        self.build_option_buttons = {}

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.info_button:
                self.current_category = "info"
                self._update_content()
            elif event.ui_element == self.city_build_button:
                self.current_category = "city_build"
                self._update_content()
            elif event.ui_element == self.unit_build_button:
                self.current_category = "unit_build"
                self._update_content()
            else:
                for option_id, button in self.build_option_buttons.items():
                    if event.ui_element == button:
                        if self.current_category == "city_build":
                            self.city.start_city_build(option_id)
                        elif self.current_category == "unit_build":
                            self.city.start_unit_build(option_id)
                        break

        return super().process_event(event)

    def _update_content(self):
        self.info_panel.hide()
        self.build_options_panel.hide()

        if self.current_category == "info":
            self._show_info_content()
        elif self.current_category == "city_build":
            self._show_city_build_content()
        elif self.current_category == "unit_build":
            self._show_unit_build_content()
        else:
            pass

    def _show_info_content(self):
        self.info_panel.show()
        info_list = self.city.get_info_list()
        self.info_text_box.html_text = self._format_list_to_html(info_list)
        self.info_text_box.rebuild()

    def _show_city_build_content(self):
        self._populate_build_options(self.city.get_city_build_options())
        self.build_options_panel.show()

    def _show_unit_build_content(self):
        self._populate_build_options(self.city.get_unit_build_options())
        self.build_options_panel.show()

    def _populate_build_options(self, build_options):
        for button in self.build_option_buttons.values():
            button.kill()
        self.build_option_buttons = {}

        button_height = 30
        button_width = self.build_options_panel.relative_rect.width - 30
        start_y = 10
        y_offset = 0

        for option_id, option_data in build_options.items():
            button = pygame_gui.elements.UIButton(
                pygame.Rect(5, y_offset + start_y, button_width, button_height),
                option_data["name"],
                manager=self.manager,
                container=self.build_options_container,
                object_id="#build_option_button",
                tool_tip_text=option_data["description"]
            )
            self.build_option_buttons[option_id] = button
            y_offset += button_height + 5
        self.build_options_panel.set_scrollable_area_dimensions(
            (self.build_options_panel.relative_rect.width, y_offset + start_y + 5))

    def _format_list_to_html(self, data_list):
        if not data_list:
            return "Список пуст."
        html_text = ""
        for item in data_list:
            html_text += f"{item}<br>"
        return html_text

    def set_city(self, city):
        self.city = city
        self.window_display_title = f"City Management: {city.hex_tile.q},{city.hex_tile.r}"
        self._update_content()

    def set_text(self):
        self._update_content()

    def show(self):
        self._update_content()
        super().show()

    def hide(self):
        super().hide()

    def update(self, time_delta):
        pass
