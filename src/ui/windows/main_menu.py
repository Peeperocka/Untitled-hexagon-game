import pygame
import pygame_gui

from src.utils.utils import load_image


class MainMenu:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.is_running = True
        self.start_game_requested = False
        self.sr = False
        self.clock = pygame.time.Clock()

        self.city = load_image('city.png', subdir='level_objects')
        self.im1 = load_image('archer.png', subdir='units')
        self.im2 = load_image('warrior.png', subdir='units')

        self.pos1 = [-300, 450]
        self.pos2 = [1000, 450]
        self.unit_t = True

        self.qb = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 400, 200, 50),
            text='Выход',
            manager=self.manager
        )

        self.sb = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 300, 200, 50),
            text='Начать игру',
            manager=self.manager
        )

        self.rb = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(700, 200, 200, 50),
            text='Правила',
            manager=self.manager
        )

    def run(self):
        while self.is_running:
            td = self.clock.tick(120) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                self.manager.process_events(event)
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.sb:
                            self.start_game_requested = True
                            self.is_running = False
                        elif event.ui_element == self.qb:
                            self.is_running = False
                        elif event.ui_element == self.rb:
                            self.sr = True

            if self.sr:
                self.rules()
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

            self.screen.fill((57, 255, 20))
            self.screen.blit(self.city, (0, 0))
            if -200 <= self.pos1[0] <= 1000:
                self.screen.blit(self.im1, tuple(self.pos1))
            if -200 <= self.pos2[0] <= 1000:
                self.screen.blit(self.im2, tuple(self.pos2))
            self.manager.update(td)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()

        return self.start_game_requested

    def rules(self):
        rs = pygame.Surface((700, 800))
        A = pygame.font.Font(None, 36)
        rs.fill((57, 255, 20))
        text_lines = [
            "Правила игры:",
            "1. ",
            "2. ",
            "3.",
            "Нажмите на любую кнопку для закрытия"
        ]

        for i, line in enumerate(text_lines):
            t = A.render(line, True, (0, 0, 0))
            rs.blit(t, (20, 20 + 35 * i))
        while self.sr:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sr = False
                elif event.type == pygame.KEYDOWN:
                    self.sr = False

            self.screen.fill((57, 255, 20))
            self.screen.blit(rs, (200, 150))
            pygame.display.flip()
