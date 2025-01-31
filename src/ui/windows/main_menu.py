import pygame
import pygame_gui


class MainMenu:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.is_running = True
        self.start_game_requested = False
        self.clock = pygame.time.Clock()

        self.city = pygame.image.load('city.png')
        self.im1 = pygame.image.load('archer.png')
        self.im2 = pygame.image.load('warrior.png')

        self.pos1 = [-200, 500]
        self.pos2 = [1000, 500]
        self.unit_t = True



        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 400, 200, 50),
            text='Выход',
            manager=self.manager
        )

        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 300, 200, 50),
            text='Начать игру',
            manager=self.manager
        )

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
            if self.unit_t:
                if self.pos1[0] < 1000:
                    self.pos1[0] += 2
                else:
                    self.pos1[0] = -100
                    self.unit_t = False
            else:
                if self.pos2[0] > -100:
                    self.pos2[0] -= 2
                else:
                    self.pos2[0] = 1000
                    self.unit_t = True


            self.screen.fill((57, 255, 20))
            self.screen.blit(self.city, (0, 0))
            if 0 <= self.pos1[0] <= 1000:
                self.screen.blit(self.im1, tuple(self.pos1))
            if 0 <= self.pos2[0] <= 1000:
                self.screen.blit(self.im2, tuple(self.pos2))
            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()

        return self.start_game_requested



def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption('Главное меню')
    manager = pygame_gui.UIManager((1000, 800))

    menu = MainMenu(screen, manager)
    start_game = menu.run()

    if start_game:
        print("Начать игру")

    pygame.quit()


if __name__ == '__main__':
    main()
