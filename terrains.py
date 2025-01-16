class Terrain:
    """
    Базовый класс для всех типов местности.
    """
    def __init__(self, color, cost, sprite=None):
        self.color = color
        self.cost = cost
        self.sprite = sprite

    def __repr__(self):
        return f"Terrain(color={self.color}, cost={self.cost}, has_sprite={self.sprite is not None})"


class GrassTerrain(Terrain):
    """
    Класс для травяной местности.
    """
    def __init__(self, sprite=None):
        super().__init__((0, 150, 0, 180), 1, sprite)


class MountainTerrain(Terrain):
    """
    Класс для горной местности.
    """
    def __init__(self, sprite=None):
        super().__init__((100, 100, 150, 180), 5, sprite)


class SandTerrain(Terrain):
    """
    Класс для песчаной местности.
    """
    def __init__(self, sprite=None):
        super().__init__((255, 255, 0, 110), 1, sprite)
