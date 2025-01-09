import os
import sys
import pygame


def load_image(name, colorkey=None):
    filename = os.path.join('data', name)

    if not os.path.isfile(filename):
        print(f"Файл с изображением '{filename}' не найден")
        sys.exit()

    image = pygame.image.load(filename)

    if colorkey is not None:
        image = image.convert()

        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)

    else:
        image = image.convert_alpha()

    return image
