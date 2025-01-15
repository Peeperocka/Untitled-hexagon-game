import pygame
import hex_utils


class Camera:
    def __init__(self, width, height, speed):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.speed = speed

    def apply(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def apply_point(self, point):
        return hex_utils.Point(point.x - self.x, point.y - self.y)
