from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget, QProgressBar, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PIL import Image
import os
import numpy as np

class ImageNormalizerAppWrapper:
    def __init__(self):
        self.app = QApplication([])
        self.window = self.ImageNormalizerApp(self)
    
    def run(self):
        self.window.show()
        self.app.exec()

    @staticmethod
    def smart_autocrop(image, bg_threshold=10):
        image = image.convert('RGB')
        np_img = np.array(image)
        corners = [
            np_img[0, 0],
            np_img[0, -1],
            np_img[-1, 0],
            np_img[-1, -1]
        ]
        bg_color = np.mean(corners, axis=0)
        diff = np.abs(np_img - bg_color).sum(axis=2)
        mask = diff > bg_threshold

        if not mask.any():
            return image

        coords = np.argwhere(mask)
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        return image.crop((x0, y0, x1, y1))

    @classmethod
    def full_batch_gimp_style(cls, image_path, max_side=1500):
        image = Image.open(image_path)
        if image.mode == 'RGBA':
            background = Image.new('RGBA', image.size, (255, 255, 255, 255))
            background.paste(image, (0, 0), image)
            image = background.convert('RGB')
        else:
            image = image.convert('RGB')

        image = cls.smart_autocrop(image)

        side = int(max(image.width, image.height) * 1.04)
        new_image = Image.new('RGB', (side, side), (255, 255, 255))
        offset_x = (side - image.width) // 2
        offset_y = (side - image.height) // 2
        new_image.paste(image, (offset_x, offset_y))

        if side > max_side:
            new_image = new_image.resize((max_side, max_side), Image.Resampling.LANCZOS)

        return new_image

    @classmethod
    def batch_normalize_fixed(cls, filelist, progress_callback=None, max_side=1500):
        for i, filepath in enumerate(filelist):
            try:
                final_image = cls.full_batch_gimp_style(filepath, max_side=max_side)
                final_image.save(filepath, "JPEG")

                if progress_callback:
                    progress_callback(i + 1, len(filelist))
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    class ImageNormalizerApp(QMainWindow):
        def __init__(self, wrapper):
            super().__init__()
            self.wrapper = wrapper
            self.setWindowTitle("Batch Image Normalizer")
            self.setFixedSize(400, 300)
            self.set_background()

            layout = QVBoxLayout()

            self.select_button = QPushButton("Vybrať Obrázky")
            self.select_button.setStyleSheet(self.button_style(True))
            self.select_button.clicked.connect(self.select_files)
            layout.addWidget(self.select_button)

            self.button = QPushButton("Spustiť")
            self.button.setStyleSheet(self.button_style(False))
            self.button.setEnabled(False)
            self.button.clicked.connect(self.start_normalization)
            layout.addWidget(self.button)


            self.progress_bar = QProgressBar(self)
            self.progress_bar.setRange(0, 100)
            layout.addWidget(self.progress_bar)

            self.status_label = QLabel("Čakám na výber obrázkov...", self)
            layout.addWidget(self.status_label)

            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)

        def set_background(self):
            background_pixmap = QPixmap("background_image.jpg")
            palette = self.palette()
            brush = QBrush(background_pixmap)
            palette.setBrush(QPalette.ColorRole.Window, brush)
            self.setPalette(palette)

        def button_style(self, enabled):
            if enabled:
                return """
                    QPushButton {
                        background-color: #E91E63;
                        color: white;
                        padding: 10px;
                        border-radius: 10px;
                        border: 2px solid #C2185B;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #D81B60;
                    }
                    QPushButton:pressed {
                        background-color: #C2185B;
                        border-style: inset;
                    }
                """
            else:
                return """
                    QPushButton {
                        background-color: #BDBDBD;
                        color: white;
                        padding: 10px;
                        border-radius: 10px;
                        border: 2px solid #9E9E9E;
                    }
                """

        def select_files(self):
            files, _ = QFileDialog.getOpenFileNames(self, "Vyberte Obrázky", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if files:
                self.selected_files = files
                self.enable_normalize_button(True)
                self.status_label.setText("Obrázky sú vybrané môžeš spustiť.")
                
            else:
                self.enable_normalize_button(False)

        def enable_normalize_button(self, enable):
            self.button.setEnabled(enable)
            self.button.setStyleSheet(self.button_style(enable))


        def start_normalization(self):
            if hasattr(self, 'selected_files') and self.selected_files:
                self.status_label.setText("Začínam s normalizovaním...")
                self.progress_bar.setValue(0)
                self.wrapper.batch_normalize_fixed(self.selected_files, self.update_progress)
                self.selected_files = []
                self.enable_normalize_button(False)
                self.status_label.setText("Obrázky boli úspešne normalizované.")
            else:
                print("Neboli vybrané žiadne obrázky na spracovanie.")

        def update_progress(self, current, total):
            progress = int(current / total * 100)
            self.progress_bar.setValue(progress)
