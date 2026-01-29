import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QStackedWidget, QFileDialog, 
                             QFrame, QSizePolicy, QMessageBox, QProgressBar)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import gimp  # Predpokladám, že importujete svoj gimp.py skript

# Cesta k obrázkom so štítkami
if getattr(sys, 'frozen', False):
    IMAGE_PATH = os.path.join(sys._MEIPASS, "images")
else:
    IMAGE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "Vyvoj", "images")

TAG_IMAGES = [
    "2x_pack.png", "3x_pack.png", "4x_pack.png", "5x_pack.png", "6x_pack.png", 
    "7x_pack.png", "8x_pack.png", "9x_pack.png", "10x_pack.png", "12x_pack.png",
    "18x_pack.png", "24x_pack.png", "bio.png", "chlazene.png", "gluten free.png", 
    "lactose free.png", "mražené.png", "nízká cena.png", "Od farmáře.png", 
    "pet.png", "protein.png", "vegan.png", "novinka.png","prosekarna.png","jen_u_nas.png","balení.png","1kg.png","500g.png"
]

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Operations App")
        self.setGeometry(100, 100, 400, 450)
        self.setStyleSheet("background-color: #FFEBEE; color: black; font-family: 'Arial', sans-serif;")

        self.button_font = QFont("Montserrat", 12, QFont.Weight.Bold)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.header_frame = QFrame(self)
        self.header_frame.setStyleSheet("background-color: #E91E63;")
        self.header_frame.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self.header_frame.setMinimumHeight(60)

        self.header_label = QLabel("foodora", self.header_frame)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: white;")

        header_layout = QVBoxLayout(self.header_frame)
        header_layout.addWidget(self.header_label)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget(self)
        self.main_menu = self.create_main_menu()
        self.download_view = self.create_download_view()
        self.tagging_view = self.create_tagging_view()
        self.normalizer_view = self.create_normalizer_view()

        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.download_view)
        self.stacked_widget.addWidget(self.tagging_view)
        self.stacked_widget.addWidget(self.normalizer_view)
        self.stacked_widget.setCurrentWidget(self.main_menu)

        main_layout.addWidget(self.header_frame)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # Inicializujeme atribúty pre súbory na normalizáciu
        self.files_to_normalize = []

    def set_button_style(self, button, enabled):
        if enabled:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #E91E63;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    border: 2px solid #C2185B;
                }
                QPushButton:hover {
                    background-color: #D81B60;
                }
                QPushButton:pressed {
                    background-color: #C2185B;
                    border-style: inset;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #BDBDBD;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    border: 2px solid #9E9E9E;
                }
            """)

    def create_button(self, text, enabled=True):
        button = QPushButton(text, self)
        button.setFont(self.button_font)
        button.setEnabled(enabled)
        self.set_button_style(button, enabled)
        return button

    def create_main_menu(self):
        menu_widget = QWidget()
        layout = QVBoxLayout(menu_widget)

        self.button_download = self.create_button("Download from URL")
        self.button_download.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.download_view))
        layout.addWidget(self.button_download)

        self.button_tagging = self.create_button("Tagging")
        self.button_tagging.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.tagging_view))
        layout.addWidget(self.button_tagging)

        self.button_normalize = self.create_button("Normalize")
        self.button_normalize.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.normalizer_view))
        layout.addWidget(self.button_normalize)

        return menu_widget

    def create_download_view(self):
        from pic import ImageDownloaderApp
        download_view = ImageDownloaderApp()

        back_button = self.create_button("Back to Main Menu")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu))

        layout = QVBoxLayout()
        layout.addWidget(download_view)
        layout.addStretch()
        layout.addWidget(back_button)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        return container_widget

    def create_tagging_view(self):
        from app import MyApp
        tagging_view = MyApp()

        back_button = self.create_button("Back to Main Menu")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu))

        layout = QVBoxLayout()
        layout.addWidget(tagging_view)
        layout.addStretch()
        layout.addWidget(back_button)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        return container_widget

    def create_normalizer_view(self):
        from gimp import ImageNormalizerAppWrapper

        wrapper = ImageNormalizerAppWrapper()
        normalizer_view = wrapper.ImageNormalizerApp(wrapper)  # vytvoríme len GUI časť

        back_button = self.create_button("Back to Main Menu")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu))

        layout = QVBoxLayout()
        layout.addWidget(normalizer_view)
        layout.addStretch()
        layout.addWidget(back_button)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        return container_widget

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
