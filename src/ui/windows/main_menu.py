import pygame
import pygame_gui


class MainMenu:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.is_running = True
        self.start_game_requested = False

        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(400, 400, 200, 50),
            text='Выход',
            manager=self.manager
        )

        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(400, 300, 200, 50),
            text='Начать игру',
            manager=self.manager
        )

        self.clock = pygame.time.Clock()

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                self.manager.process_events(event)

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.start_button:
                            self.start_game_requested = True
                            self.is_running = False
                        elif event.ui_element == self.quit_button:
                            self.is_running = False

            self.manager.update(time_delta)
            self.screen.fill((30, 30, 30))
            self.manager.draw_ui(self.screen)

            pygame.display.flip()

        return self.start_game_requested
