import os
import sys
import pygame


def load_image(name, colorkey=None, subdir=None):
    base_path = os.path.join('data', 'images')
    if subdir:
        filename = os.path.join(base_path, subdir, name)
    else:
        filename = os.path.join(base_path, name)

    if not os.path.isfile(filename):
        raise ValueError(f"Файл с изображением '{filename}' не найден")

    image = pygame.image.load(filename)

    if colorkey is not None:
        image = image.convert()

        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)

    else:
        image = image.convert_alpha()

    return image
