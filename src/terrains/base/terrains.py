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
