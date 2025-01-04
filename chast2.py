import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QLabel


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Меню")
        self.setGeometry(100, 100, 300, 300)
        layout = QVBoxLayout()

        b_play = QPushButton("Играть")
        b_play.move(120, 120)
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
        self.sett_window = SetsWindow()
        self.sett_window.show()


class SetsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Настройки')
        self.setGeometry(150, 150, 300, 300)

        layout = QVBoxLayout()

        self.fps_l = QLabel("Выберите качество картинки :", self)
        layout.addWidget(self.fps_l)

        fps30 = QPushButton('низкое', self)
        fps30.clicked.connect(self.fpss30)
        layout.addWidget(fps30)

        fps60 = QPushButton('среднее', self)
        fps60.clicked.connect(self.fpss60)
        layout.addWidget(fps60)

        fps120 = QPushButton('высокое', self)
        fps120.clicked.connect(self.fpss120)
        layout.addWidget(fps120)

        close_button = QPushButton('Закрыть', self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def fpss30(self):
        self.save_settings(30)

    def fpss60(self):
        self.save_settings(60)

    def fpss120(self):
        self.save_settings(120)

    def fpss60(self):
        self.save_settings(60)

    def save_settings(self, fpser):
        print(f"Настройки сохранены, частота кадров", fpser)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec())





