import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    board = HexBoard(10, 10, 50)

    # Добавление юнита на доску
    warrior_tile = board.grid[5][5]  # Пример: юнит на клетке (5, 5)
    warrior = Warrior(warrior_tile)
    board.game_objects.append(warrior)

    camera = Camera(800, 600, 5)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass

        screen.fill(board.black)

        # Отрисовка карты
        screen.blit(board.map_surface, (0, 0))

        # Отрисовка юнитов
        for game_object in board.game_objects:
            game_object.render(screen, camera)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# короче просто пока типа юнита добавлена штучка и делал ее действия по типу перемещения и тд мелкого