import pygame
import pygame_gui

from src.entities.game.registry import CITY_IMPROVEMENT_BLUEPRINTS, UNIT_BLUEPRINTS


class UICityWindow(pygame_gui.elements.UIWindow):
    BUTTON_HEIGHT = 30
    BUTTON_VERTICAL_MARGIN = 5
    CATEGORY_BUTTON_WIDTH_PERCENTAGE = 0.30
    PANEL_VERTICAL_OFFSET = 10
    CONTENT_START_X = 10
    BUTTON_WIDTH_OFFSET = 30

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
        self.build_option_buttons = {}
        self._create_ui_elements()
        self._update_content()

    def _calculate_category_button_width(self):
        available_button_width = self.rect.width - 2 * self.CONTENT_START_X
        return available_button_width * self.CATEGORY_BUTTON_WIDTH_PERCENTAGE - self.BUTTON_VERTICAL_MARGIN

    def _create_ui_elements(self):
        button_y = self.CONTENT_START_X
        start_x = self.CONTENT_START_X
        category_button_width = self._calculate_category_button_width()

        self.info_button = pygame_gui.elements.UIButton(
            pygame.Rect(start_x, button_y, category_button_width, self.BUTTON_HEIGHT),
            "Инфо",
            manager=self.manager,
            container=self,
            object_id="#category_button",
        )
        start_x += category_button_width + self.BUTTON_VERTICAL_MARGIN

        self.city_build_button = pygame_gui.elements.UIButton(
            pygame.Rect(start_x, button_y, category_button_width, self.BUTTON_HEIGHT),
            "Улучшения",
            manager=self.manager,
            container=self,
            object_id="#category_button",
        )
        start_x += category_button_width + self.BUTTON_VERTICAL_MARGIN

        self.unit_build_button = pygame_gui.elements.UIButton(
            pygame.Rect(start_x, button_y, category_button_width, self.BUTTON_HEIGHT),
            "Наем юнитов",
            manager=self.manager,
            container=self,
            object_id="#category_button",
        )

        panel_y = button_y + self.BUTTON_HEIGHT + self.PANEL_VERTICAL_OFFSET
        panel_height = self.rect.height - (panel_y + self.PANEL_VERTICAL_OFFSET)

        self.info_panel = pygame_gui.elements.UIPanel(
            pygame.Rect(self.CONTENT_START_X, panel_y, self.rect.width - 2 * self.CONTENT_START_X, panel_height),
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
            pygame.Rect(self.CONTENT_START_X, panel_y, self.rect.width - 2 * self.CONTENT_START_X, panel_height),
            manager=self.manager,
            container=self,
            visible=False,
            object_id="#build_options_panel"
        )
        self.build_options_container = self.build_options_panel.get_container()

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
                self._handle_build_option_click(event.ui_element)
        return super().process_event(event)

    def _handle_build_option_click(self, clicked_element):
        for option_id, button in self.build_option_buttons.items():
            if clicked_element != button:
                continue

            if self.current_category == "city_build":
                if not self._check_requirements(option_id, CITY_IMPROVEMENT_BLUEPRINTS):
                    msg = f"Не выполнены требования для {CITY_IMPROVEMENT_BLUEPRINTS[option_id].name}"
                    print(msg)
                    self.city.game_manager.hud_manager.dynamic_message_manager.create_message(msg)
                    return
                self.city.start_city_improvement_construction(option_id)
                return

            elif self.current_category == "unit_build":
                if self.city.hex_tile.unit is not None:
                    msg = "Тайл города занят другим юнитом."
                    print(msg)
                    self.city.game_manager.hud_manager.dynamic_message_manager.create_message(msg)
                    return
                if not self._check_requirements(option_id, UNIT_BLUEPRINTS):
                    msg = f"Не выполнены требования для {UNIT_BLUEPRINTS[option_id].name}"
                    print(msg)
                    self.city.game_manager.hud_manager.dynamic_message_manager.create_message(msg)
                    return
                self.city.start_unit_recruitment(option_id)
                return
            break

    def _check_requirements(self, option_id, blueprints):
        blueprint = blueprints.get(option_id)
        if not blueprint or not hasattr(blueprint, 'requirements'):
            return True

        for requirement_id in blueprint.requirements:
            if requirement_id not in self.city.city_improvements:
                return False
        return True

    def _update_content(self):
        self.info_panel.hide()
        self.build_options_panel.hide()
        self._clear_build_option_buttons()

        if self.current_category == "info":
            self._show_info_content()
        elif self.current_category == "city_build":
            self._show_build_options_content(self.city.get_city_improvement_blueprints())
        elif self.current_category == "unit_build":
            self._show_build_options_content(self.city.get_unit_recruitment_blueprints())

    def _show_info_content(self):
        self.info_panel.show()
        info_list = self.city.get_city_report()
        self.info_text_box.html_text = self._format_list_to_html(info_list)
        self.info_text_box.rebuild()

    def _show_build_options_content(self, build_options):
        self._populate_build_options(build_options)
        self.build_options_panel.show()

    def _generate_option_description(self, option_data):
        description = option_data.description + '\nСтоимость:'

        resources = {
            "Золото": getattr(option_data, 'cost_gold', 0),
            "Пища": getattr(option_data, 'cost_food', 0),
            "Камень": getattr(option_data, 'cost_stone', 0),
            "Металл": getattr(option_data, 'cost_metal', 0),
        }

        for resource, cost in resources.items():
            if cost != 0:
                description += f"\n{resource}: {cost}"

        if hasattr(option_data, 'requirements') and option_data.requirements:
            description += "\nТребования:"
            for requirement in option_data.requirements:
                description += f"\n - {CITY_IMPROVEMENT_BLUEPRINTS[requirement].name}"
        return description

    def _create_build_option_button(self, option_id, option_data, y_offset):
        description = self._generate_option_description(option_data)
        is_available = True

        if self.current_category == "city_build":
            is_available = self._check_requirements(option_id, CITY_IMPROVEMENT_BLUEPRINTS)
        elif self.current_category == "unit_build":
            is_available = self._check_requirements(option_id, UNIT_BLUEPRINTS)

        button = pygame_gui.elements.UIButton(
            pygame.Rect(
                5,
                y_offset + self.CONTENT_START_X,
                self.build_options_panel.relative_rect.width - self.BUTTON_WIDTH_OFFSET,
                self.BUTTON_HEIGHT,
            ),
            option_data.name,
            manager=self.manager,
            container=self.build_options_container,
            tool_tip_text=description,
            object_id="#disabled_build_option" if not is_available else "#build_option_button"
        )
        return button

    def _clear_build_option_buttons(self):
        for button in self.build_option_buttons.values():
            button.kill()
        self.build_option_buttons = {}

    def _set_scrollable_area_dimensions(self, total_height):
        self.build_options_panel.set_scrollable_area_dimensions(
            (self.build_options_panel.relative_rect.width, total_height)
        )

    def _populate_build_options(self, build_options):
        y_offset = 0
        for option_id, option_data in build_options.items():
            button = self._create_build_option_button(option_id, option_data, y_offset)
            self.build_option_buttons[option_id] = button
            y_offset += self.BUTTON_HEIGHT + self.BUTTON_VERTICAL_MARGIN

        total_height = y_offset + self.CONTENT_START_X + self.BUTTON_VERTICAL_MARGIN
        self._set_scrollable_area_dimensions(total_height)

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
