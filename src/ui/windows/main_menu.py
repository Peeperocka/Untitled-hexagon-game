import pygame
import pygame_gui


class MainMenu:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.is_running = True
        self.start_game_requested = False

        self.lb = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(400, 400, 200, 50),text='Выход',manager=self.manager
        )

        self.sb = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(400, 300, 200, 50),text='Начать игру',manager=self.manager
        )

        self.rb = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(400, 200, 200, 50),text='Правила',manager=self.manager
        )


        self.clock = pygame.time.Clock()
        self.rules_window = None

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                self.manager.process_events(event)

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.sb:
                            self.start_game_requested = True
                            self.is_running = False
                        elif event.ui_element == self.lb:
                            self.is_running = False
                        elif event.ui_element == self.rb:
                            self.rules_window = display_rules(self.manager)

                if self.rules_window and event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.rules_window.cb:
                            self.rules_window.kill()
                            self.rules_window = None

            self.manager.update(time_delta)
            self.screen.fill((30, 30, 30))
            self.manager.draw_ui(self.screen)

            pygame.display.flip()

        return self.start_game_requested


def display_rules(manager):
    rw = pygame_gui.elements.UIWindow(rect=pygame.Rect(100, 100, 800, 600),manager=manager,window_display_title='Правила игры'
    )

    rt = [
        "Правила игры:",
        "1. Игроки делают поочередные ходы.",
        "2. ",
        "3. ",
        "",
        "",
        "Нажмите 'Закрыть', чтобы вернуться."
    ]

    for i, line in enumerate(rt):
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 10 + i * 30, 650, 30),text=line,manager=manager,container=rw
        )

    cb = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(320, 500, 160, 50),text='Закрыть',manager=manager,container=rw
    )

    rw.cb = cb

    return rw

def main():
    pygame.init()
    width, height = 1000, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Hexagons game")

    manager = pygame_gui.UIManager((width, height))

    main_menu = MainMenu(screen, manager)
    main_menu.run()

    pygame.quit()


if __name__ == '__main__':
    main()
