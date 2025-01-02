import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Меню")
        self.setGeometry(100, 100, 300, 300)
        layout = QVBoxLayout()

        b_play = QPushButton("Играть")
        layout.addWidget(b_play)
        b_play.clicked.connect(self.d_play)

        b_exit = QPushButton("Выйти")
        layout.addWidget(b_exit)
        b_exit.clicked.connect(self.d_exit)

        b_loader = QPushButton("Загрузить сохранение")
        layout.addWidget(b_loader)
        b_loader.clicked.connect(self.d_loader)

        b_settings = QPushButton("Настройки")
        layout.addWidget(b_settings)
        b_settings.clicked.connect(self.d_settings)

        self.setLayout(layout)

    def d_play(self):
        print("что-то")

    def d_exit(self):
        sys.exit()

    def d_loader(self):
        try:
            with open('data.json', 'r') as json_file:
                z = json.load(json_file)
        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", "Файл данных не найден.")

    # обозначения: d - кратко деф, b - кнопка
    # не шарю как по другому лоадер сделать

    def d_settings(self):
        print("что-то!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec())
