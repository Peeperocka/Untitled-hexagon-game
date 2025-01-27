# Untitled-hexagon-game

## Установка

### Установка зависимостей
Python 3 должен быть уже установлен.
Используйте pip для установки зависимостей:

```
pip install -r requirements.txt
```

## Краткое руководство: Создание нового юнита в игре

Этот гайд вкратце описывает шаги по созданию нового юнита в игре, используя систему блюпринтов и `GameEntityFactory`.

**Шаг 1: Определите Блюпринт Юнита (Unit Blueprint)**

Создайте описание вашего юнита в виде **блюпринта**. Блюпринт – это контейнер данных о юните: имя, характеристики, стоимость и поведение.  Используйте `UnitBlueprint` для этого.

Откройте файл с блюпринтами (`src/entities/base/blueprints.py`) и найдите `UnitBlueprint`.  Создайте новый экземпляр для вашего юнита.

Структура `UnitBlueprint`:

```python
from dataclasses import dataclass
from typing import List, Type

@dataclass
class UnitBlueprint:
    """Блюпринт для юнитов (не тайловых объектов)."""
    name: str
    description: str
    base_health: int
    base_attack: int
    cost_gold: int
    cost_food: int
    requirements: List[str]
    implementation_class: Type
```

*   **`name` (str):** Уникальное имя юнита (например, "Рыцарь", "Гоблин").
*   **`description` (str):** Краткое описание юнита.
*   **`base_health` (int):** Начальное здоровье юнита.
*   **`base_attack` (int):** Базовая атака юнита.
*   **`cost_gold` (int):** Стоимость в золоте для найма.
*   **`cost_food` (int):** Стоимость в еде для найма.
*   **`requirements` (List[str]):** Список требований для найма (улучшения города, технологии). Пустой список `[]`, если нет требований.
*   **`implementation_class` (Type):** Python класс, реализующий поведение юнита (`src.entities.base.game_objects.Unit`).  Можно использовать базовый класс `Unit` или создать свой.

**Пример: Блюпринт для "Рыцаря"**

```python
# ... другие импорты и блюпринты ...
from src.entities.game.units import Knight  # Импорт класса Knight

# ... другие блюпринты ...

knight_blueprint = UnitBlueprint(
    name="Рыцарь",
    description="Тяжелый пехотинец, силен в ближнем бою.",
    base_health=150,
    base_attack=20,
    cost_gold=80,
    cost_food=40,
    requirements=[],
    implementation_class=Knight  # Используем класс Knight
)
```

**Шаг 2: (Опционально) Создайте Класс Реализации Юнита**

Если юниту нужно особое поведение, создайте новый Python класс. Если юнит простой, можно использовать или расширить существующий класс.

Пример класса `Knight` в `src/entities/game/units.py`:

```python
# src/entities/game/units.py

from src.entities.base.game_objects import Unit
import pygame # Если нужно pygame

class Knight(Unit):
    """
    Представляет юнита Рыцарь в игре.
    """
    def __init__(self, hex_tile, player, game_manager, blueprint):
        super().__init__(hex_tile, player, game_manager, blueprint)
        # Инициализация для Рыцаря (если нужно)
        # self.image = pygame.transform.scale(load_image("knight.png", subdir="units"), (50, 50))

    # Можно переопределить методы из Unit для особого поведения.
    def special_attack(self, target_unit):
        # Логика особой атаки Рыцаря
        print(f"{self.blueprint.name} выполняет особую атаку на {target_unit.blueprint.name}!")
        # ... расчет урона и эффекты ...
        pass
```

**Шаг 3: Зарегистрируйте Блюпринт Юнита**

Зарегистрируйте блюпринт в реестре игры, чтобы игра могла его найти.

Откройте файл реестров (`src/entities/game/registry.py`). Найдите словарь `UNIT_BLUEPRINTS`. Добавьте ваш блюпринт, используя уникальный ID (например, "knight").

В `src/entities/game/registry.py`:

```python
# src/entities/game/registry.py

from .units import Warrior, Cavalry, Archer, Crossbowman, Knight # Импорт класса Knight
from src.entities.base.blueprints import UnitBlueprint

# ... другие реестры ...

UNIT_BLUEPRINTS = {
    "warrior": UnitBlueprint( ... ),
    "cavalry": UnitBlueprint( ... ),
    "archer": UnitBlueprint( ... ),
    "crossbowman": UnitBlueprint( ... ),
    "knight": knight_blueprint,      # Регистрация блюпринта Рыцаря с ID "knight"
    # ... другие блюпринты ...
}

# ... остаток файла ...
```

**Важно:** ID юнита в `UNIT_BLUEPRINTS` должен совпадать с ID, используемым при создании юнита через `GameEntityFactory`.

**Шаг 4: Используйте `GameEntityFactory` для создания юнитов**

Используйте `GameEntityFactory.create_unit` для создания юнитов в игре.

Найдите класс `GameEntityFactory` (`src/utils/factories.py`). Метод `create_unit` создает экземпляры юнитов.

```python
# src/utils/factories.py

from src.entities.base.blueprints import CityImprovementBlueprint, UnitBlueprint
from src.entities.game.registry import CITY_BLUEPRINTS, UNIT_BLUEPRINTS, TILE_BUILDING_BLUEPRINTS, CITY_IMPROVEMENT_BLUEPRINTS
from src.entities.base.game_objects import Unit, Building
from src.entities.game.level_objects import City
from src.entities.game.units import Warrior, Cavalry, Archer, Crossbowman, Knight # Импорт класса Knight


class GameEntityFactory:
    @staticmethod
    def create_unit(unit_id: str, hex_tile, player, game_manager) -> Unit:
        blueprint = UNIT_BLUEPRINTS[unit_id] # Получаем блюпринт по ID
        implementation_class = blueprint.implementation_class
        return implementation_class(hex_tile, player, game_manager, blueprint)

    # ... другие методы фабрики ...
```

Для создания "Рыцаря" вызовите `GameEntityFactory.create_unit("knight", ...)` с ID "knight".

**Пример: Создание Рыцаря в `main_gamer`:**

```python
# ... внутри функции main_gamer ...

def place_units_for_testing(board, player1, player2, player1_units_data, player2_units_data):
    # ... код ...

    player1_data = [
        ("cavalry", (0, 0, 0)),
        ("knight", (-1, 3, -2)), # Размещаем юнита "knight"
        ("archer", (-1, 1, 0)),
        ("crossbowman", (-1, 2, -1)),
    ]
    player2_data = [
        ("warrior", (3, 0, -3)),
        ("warrior", (3, 1, -4)),
        ("warrior", (2, 2, -4)),
    ]
    place_units_for_testing(board, player1, player2, player1_data, player2_data)

    # ... остаток функции ...
```
