from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, 
                             QProgressBar, QMessageBox, QGridLayout, QStackedWidget)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
import sys
import os
from PIL import Image

# Cesta k obrázkom so štítkami
if getattr(sys, 'frozen', False):
    IMAGE_PATH = os.path.join(sys._MEIPASS, "images")
else:
    IMAGE_PATH = os.path.join(os.path.expanduser("~"), "Desktop","Vyvoj(kopie)", "images")

TAG_IMAGES = [
    "2x_pack.png", "3x_pack.png", "4x_pack.png", "5x_pack.png", "6x_pack.png", 
    "7x_pack.png", "8x_pack.png", "9x_pack.png", "10x_pack.png", "12x_pack.png",
    "18x_pack.png", "24x_pack.png", "bio.png", "chlazene.png", "gluten free.png", 
    "lactose free.png", "mražené.png", "nízká cena.png", "Od farmáře.png", 
    "pet.png", "protein.png", "vegan.png", "novinka.png","prosekarna.png","jen_u_nas.png","balení.png","1kg.png","500g.png"
]

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Tagging App")
        self.setGeometry(100, 100, 450, 500)
        self.setStyleSheet("background-color: #FFEBEE; color: black;")
        
        self.button_font = QFont("Montserrat", 12, QFont.Weight.Bold)
        self.selected_position = (2, 0)  # Predvolená pozícia (prvý riadok, tretí stĺpec)

        layout = QVBoxLayout()

        self.button_select_images = self.create_button("Choose Images")
        self.button_select_images.clicked.connect(self.select_images)
        
        self.button_select_folder = self.create_button("Choose Target Folder")
        self.button_select_folder.clicked.connect(self.select_folder)

        self.tag_dropdown = QComboBox()
        self.load_tag_images()
        self.tag_dropdown.currentIndexChanged.connect(self.check_ready)

        self.button_run = self.create_button("Run", enabled=False)
        self.button_run.clicked.connect(self.process_images)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout.addWidget(self.button_select_images)
        layout.addWidget(self.button_select_folder)
        layout.addWidget(self.tag_dropdown)
        layout.addWidget(self.create_position_selector())
        layout.addWidget(self.button_run)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def create_button(self, text, enabled=True):
        button = QPushButton(text, self)
        button.setFont(self.button_font)
        button.setEnabled(enabled)
        self.set_button_style(button, enabled)
        return button

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


    def create_position_selector(self):
        position_widget = QWidget()
        grid_layout = QGridLayout()
        
        self.position_buttons = {}
        
        for row in range(3):
            for col in range(3):
                btn = QPushButton(f"{row+1},{col+1}")
                btn.setFont(self.button_font)
                btn.setStyleSheet(self.get_position_button_style((row, col) == self.selected_position))
                btn.clicked.connect(lambda checked, r=row, c=col: self.set_position(r, c))
                self.position_buttons[(row, col)] = btn
                grid_layout.addWidget(btn, row, col)
        
        position_widget.setLayout(grid_layout)
        return position_widget

    def set_position(self, row, col):
        self.selected_position = (row, col)
        for pos, button in self.position_buttons.items():
            button.setStyleSheet(self.get_position_button_style(pos == self.selected_position))

    def get_position_button_style(self, selected):
        if selected:
            return """
                QPushButton {
                    background-color: #F8BBD0; /* Zlatá farba pre vybranú pozíciu */
                    color: black;
                    padding: 10px;
                    border-radius: 15px;
                    border: 2px solid #C2185B;
                    font-weight: bold;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #E91E63;
                    color: white;
                    padding: 10px;
                    border-radius: 15px;
                    border: 2px solid #C2185B;
                }
                QPushButton:hover {
                    background-color: #D81B60;
                }
                QPushButton:pressed {
                    background-color: #C2185B;
                    border-style: inset;
                }
            """

    
    def load_tag_images(self):
        for tag in TAG_IMAGES:
            path = os.path.join(IMAGE_PATH, tag)
            if os.path.exists(path):
                icon = QIcon(QPixmap(path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
                self.tag_dropdown.addItem(icon, tag)
    
    def select_images(self):
        self.selected_files, _ = QFileDialog.getOpenFileNames(self, "Choose Images", "", "Images (*.png *.jpg *.jpeg)")
        self.check_ready()
    
    def select_folder(self):
        self.selected_folder = QFileDialog.getExistingDirectory(self, "Choose Target Folder")
        self.check_ready()
    
    def check_ready(self):
        ready = hasattr(self, 'selected_files') and hasattr(self, 'selected_folder') and self.tag_dropdown.currentIndex() >= 0
        self.button_run.setEnabled(ready)
        if ready:
            self.set_button_style(self.button_run, True)
        else:
            self.set_button_style(self.button_run, False)
    
    def process_images(self):
        tag_name = self.tag_dropdown.currentText()
        tag_path = os.path.join(IMAGE_PATH, tag_name)

        if not os.path.exists(tag_path):
            QMessageBox.warning(self, "Fail", f"Tag {tag_name} was not found!")
            return

        for image_path in self.selected_files:
            try:
                img = Image.open(image_path).convert("RGBA")
                tag = Image.open(tag_path).convert("RGBA").resize((img.width // 3, img.height // 3), Image.Resampling.LANCZOS)
                
                x_offset = self.selected_position[1] * (img.width // 3)
                y_offset = self.selected_position[0] * (img.height // 3)
                
                img.paste(tag, (x_offset, y_offset), tag)
                
                base_name, ext = os.path.splitext(os.path.basename(image_path))
                new_name = f"{base_name}_TAG.jpg"
                save_path = os.path.join(self.selected_folder, new_name)
                img.convert("RGB").save(save_path, "JPEG")
                
            except Exception as e:
                print(f"Chyba pri spracovaní obrázka {image_path}: {e}")
                pass
        QMessageBox.information(self, "Finished", "Images has been tagged!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
