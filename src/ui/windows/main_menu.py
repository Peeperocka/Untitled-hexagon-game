import pygame
import pygame_gui

from src.utils.utils import load_image
import os


class MainMenu:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.themed_manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()),
                                                   os.path.join('data', 'theme', 'game_theme.json'))
        self.is_running = True
        self.load_game_requested = False
        self.new_game_requested = False
        self.sr = False
        self.clock = pygame.time.Clock()

        self.city = load_image('city.png', subdir='level_objects')
        self.im1 = load_image('archer.png', subdir='units')
        self.im2 = load_image('warrior.png', subdir='units')

        self.pos1 = [-300, 450]
        self.pos2 = [1000, 450]
        self.unit_t = True
        self.rules_screen_active = False
        self.new_game_screen_active = False
        self.load_game_screen_active = False

        self.ngb = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 100, 200, 50),
            text='Новая игра',
            manager=self.manager
        )

        self.lgb = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 150, 200, 50),
            text='Загрузить игру',
            manager=self.manager
        )

        self.rb = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 200, 200, 50),
            text='Правила',
            manager=self.manager
        )

        self.qb = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 300, 200, 50),
            text='Выход',
            manager=self.manager
        )

        self.menu_buttons = [self.ngb, self.lgb, self.rb, self.qb]

    def run(self):
        self.is_running = True
        self.load_game_requested = False
        self.new_game_requested = False
        self.sr = False
        self.rules_screen_active = False
        self.new_game_screen_active = False
        self.load_game_screen_active = False

        while self.is_running:
            td = self.clock.tick(120) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                self.manager.process_events(event)
                self.themed_manager.process_events(event)
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.qb:
                            self.is_running = False
                        elif event.ui_element == self.rb:
                            self.rules_screen_active = True
                            self.hide_menu_buttons()
                            self.rules()
                        elif event.ui_element == self.ngb:
                            self.new_game_screen_active = True
                            self.new_game_options()
                        elif event.ui_element == self.lgb:
                            self.load_game_screen_active = True
                            self.load_game_screen()

            if self.rules_screen_active:
                continue
            if self.new_game_screen_active:
                continue
            if self.load_game_screen_active:
                continue

            if self.unit_t:
                if self.pos1[0] < 1000:
                    self.pos1[0] += 3
                else:
                    self.pos1[0] = -300
                    self.unit_t = False
            else:
                if self.pos2[0] > -200:
                    self.pos2[0] -= 3
                else:
                    self.pos2[0] = 1000
                    self.unit_t = True

            self.screen.fill((29, 128, 10))
            self.screen.blit(self.city, (0, 0))
            if -200 <= self.pos1[0] <= 1000:
                self.screen.blit(self.im1, tuple(self.pos1))
            if -200 <= self.pos2[0] <= 1000:
                self.screen.blit(self.im2, tuple(self.pos2))
            self.manager.update(td)
            self.themed_manager.update(td)
            self.manager.draw_ui(self.screen)
            self.themed_manager.draw_ui(self.screen)
            pygame.display.flip()

        if self.new_game_requested:
            return "new_game", self.new_game_options_data
        elif self.load_game_requested:
            return "load_game", self.load_game_data
        else:
            return "quit", {}

    def rules(self):
        self.rules_manager = pygame_gui.UIManager((self.screen.get_width(), self.screen.get_height()),
                                                  os.path.join('data', 'theme', 'game_theme.json'))

        self.rules_background = pygame.Surface((800, 530))
        self.rules_background.fill(pygame.Color("#1D800A"))

        self.rules_text = [
            "               Краткое руководство",
            "Цель игры: уничтожить всех противников.",
            "Игровой процесс:",
            "  - Игра пошаговая, каждый игрок ходит по очереди.",
            "  - В свой ход вы можете перемещать юнитов и атаковать.",
            "  - Юниты могут атаковать только один раз за ход.",
            "  - Города производят ресурсы и могут создавать юнитов.",
            "  - Вы можете основать новый город, если в радиусе 5 клеток от",
            "    него нет других городов.",
            "  - Для постройки зданий или найма юнитов в городе нажмите 'Q'.",
            "Ресурсы:",
            "  - Золото, дерево, камень, металл и еда.",
            "  - Ресурсы производятся городами каждый ход.",
            "  - Юниты потребляют золото каждый ход.",
            "Управление юнитами:",
            "  - Выберите юнита, чтобы увидеть доступные действия.",
            "  - Синим подсвечиваются клетки для перемещения.",
            "  - Желтым - враги, которых можно атаковать после перемещения.",
            "  - Красным - враги, которых можно атаковать без перемещения.",
            "Управление городами:",
            "  - Нажмите на город, чтобы увидеть информацию.",
            "  - Нажмите 'Q', чтобы открыть меню города:",
            "  - В меню города доступны: постройка зданий и найм юнитов.",
            "Начало игры:",
            "  - Новая игра: выберите количество игроков и имя сохранения.",
            "  - Загрузить игру: выберите сохранение из списка.",
            "Сохранение и загрузка:",
            "  - Сохранить игру можно в меню паузы (Esc).",
            "  - Загрузить игру можно в главном меню.",
            "",
        ]

        self.text_box = pygame_gui.elements.UITextBox(
            html_text="<br>".join(self.rules_text),
            relative_rect=pygame.Rect((0, 0), (1000, 500)),
            manager=self.rules_manager,
            object_id=pygame_gui.core.ObjectID(class_id='@rules_text_box')
        )
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((500, 630), (150, 40)),
            text='Назад',
            manager=self.rules_manager
        )

        self.rules_screen_active = True
        while self.rules_screen_active:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rules_screen_active = False
                    self.is_running = False
                elif event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.back_button:
                            self.rules_screen_active = False
                            self.show_menu_buttons()
                            break

                self.rules_manager.process_events(event)
            self.screen.fill((29, 128, 10))
            self.screen.blit(self.rules_background, (160, 70))
            self.rules_manager.update(time_delta)
            self.rules_manager.draw_ui(self.screen)
            pygame.display.flip()
        self.rules_manager.clear_and_reset()

    def new_game_options(self):
        self.new_game_manager = self.themed_manager
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((550, 160), (300, 30)),
            text='Количество игроков:',
            manager=self.new_game_manager,
            object_id='@main_menu_label'
        )
        self.player_count_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=['2', '3', '4', '5', '6', '7', '8'],
            starting_option='2',
            relative_rect=pygame.Rect((550, 200), (300, 50)),
            manager=self.new_game_manager
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((550, 260), (300, 30)),
            text='Название сохранения:',
            manager=self.new_game_manager,
            object_id='@main_menu_label'
        )
        self.save_name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((550, 300), (300, 50)),
            manager=self.new_game_manager,
            placeholder_text='Название сохранения'
        )
        self.start_button_ng = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((550, 400), (140, 50)),
            text='Старт',
            manager=self.new_game_manager
        )
        self.cancel_button_ng = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((710, 400), (140, 50)),
            text='Отмена',
            manager=self.new_game_manager
        )

        self.new_game_options_data = {}
        self.new_game_screen_active = True

        while self.new_game_screen_active:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.new_game_screen_active = False
                    self.is_running = False
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.start_button_ng:
                            save_name = self.save_name_entry.get_text()
                            if not save_name:
                                save_name = 'savegame'
                            if not save_name.endswith('.json'):
                                save_name += '.json'
                            self.new_game_options_data = {
                                'player_count': int(self.player_count_dropdown.selected_option[0]),
                                'save_name': save_name
                            }
                            self.new_game_requested = True
                            self.new_game_screen_active = False
                            self.is_running = False
                        elif event.ui_element == self.cancel_button_ng:
                            self.new_game_screen_active = False
                            self.new_game_requested = False
                            break

                self.themed_manager.process_events(event)

            self.screen.fill((29, 128, 10))
            self.screen.blit(self.city, (0, 0))
            self.themed_manager.update(time_delta)
            self.themed_manager.draw_ui(self.screen)
            pygame.display.flip()
        self.new_game_manager.clear_and_reset()

    def load_game_screen(self):
        self.load_game_manager = self.themed_manager
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((550, 160), (300, 30)),
            text='Выберите сохранение:',
            manager=self.load_game_manager,
            object_id='@main_menu_label'
        )
        save_files = [f for f in os.listdir(os.path.join('data', 'saves')) if f.endswith('.json')]
        self.save_file_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=save_files if save_files else ['Нет сохранений'],
            starting_option=save_files[0] if save_files else 'Нет сохранений',
            relative_rect=pygame.Rect((550, 200), (300, 50)),
            manager=self.load_game_manager
        )

        self.load_button_lg = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((550, 300), (140, 50)),
            text='Загрузить',
            manager=self.load_game_manager
        )

        self.cancel_button_lg = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((710, 300), (140, 50)),
            text='Отмена',
            manager=self.load_game_manager
        )

        self.load_game_data = {}
        self.load_game_screen_active = True

        while self.load_game_screen_active:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.load_game_screen_active = False
                    self.is_running = False
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.load_button_lg:
                            selected_save = self.save_file_dropdown.selected_option[0]
                            if selected_save != 'Нет сохранений':
                                self.load_game_data = {'save_file': selected_save}
                                self.load_game_requested = True
                                self.load_game_screen_active = False
                                self.is_running = False
                        elif event.ui_element == self.cancel_button_lg:
                            self.load_game_screen_active = False
                            self.load_game_requested = False
                            break
                self.themed_manager.process_events(event)

            self.screen.fill((29, 128, 10))
            self.screen.blit(self.city, (0, 0))
            self.themed_manager.update(time_delta)
            self.themed_manager.draw_ui(self.screen)
            pygame.display.flip()
        self.load_game_manager.clear_and_reset()

    def hide_menu_buttons(self):
        """Hides the main menu buttons."""
        for button in self.menu_buttons:
            button.hide()

    def show_menu_buttons(self):
        """Shows the main menu buttons."""
        for button in self.menu_buttons:
            button.show()
