import os
import csv
import requests
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QStackedWidget, QFileDialog, 
                             QFrame, QSizePolicy, QTextEdit, QProgressBar)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class ImageDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.csv_file = None
        self.target_folder = None

        self.setWindowTitle("Foodora Style App")
        self.setGeometry(100, 100, 400, 450)
        self.setStyleSheet("background-color: #FFEBEE; color: black; font-family: 'Arial', sans-serif;")

        self.button_font = QFont("Montserrat", 12, QFont.Weight.Bold)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Odstránil som záhlavie (Foodora banner)
        self.stacked_widget = QStackedWidget(self)
        self.download_view = self.create_download_view()
        self.stacked_widget.addWidget(self.download_view)  # Hneď sa pridáva download view
        self.stacked_widget.setCurrentWidget(self.download_view)

        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

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

    def create_download_view(self):
        view = QWidget()
        layout = QVBoxLayout()

        self.label_csv = QLabel("Vyberte CSV súbor:")
        layout.addWidget(self.label_csv)

        self.btn_select_csv = self.create_button("Vybrať CSV")
        self.btn_select_csv.clicked.connect(self.select_csv)
        layout.addWidget(self.btn_select_csv)

        self.label_folder = QLabel("Vyberte cieľový priečinok:")
        layout.addWidget(self.label_folder)

        self.btn_select_folder = self.create_button("Vybrať priečinok")
        self.btn_select_folder.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select_folder)

        self.btn_download = self.create_button("Spustiť sťahovanie", enabled=False)
        self.btn_download.clicked.connect(self.download_images)
        layout.addWidget(self.btn_download)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # Progress bar for download progress
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    

        view.setLayout(layout)
        return view

    def select_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Vyberte CSV súbor", "", "CSV Files (*.csv)")
        if file_path:
            self.csv_file = file_path
            self.label_csv.setText(f"CSV: {os.path.basename(file_path)}")
            self.update_download_button()

    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Vyberte cieľový priečinok")
        if folder_path:
            self.target_folder = folder_path
            self.label_folder.setText(f"Priečinok: {folder_path}")
            self.update_download_button()

    def update_download_button(self):
        if self.csv_file and self.target_folder:
            self.btn_download.setEnabled(True)
            self.set_button_style(self.btn_download, True)

    def download_images(self):
        if not self.csv_file or not self.target_folder:
            self.result_text.append("❌ Chýbajú požiadavky (CSV súbor alebo cieľový priečinok).")
            return
        
        self.result_text.append("🟡 Sťahovanie začalo...")
        failed = []
        
        with open(self.csv_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)
            
            if len(rows) < 2:
                self.result_text.append("❌ CSV súbor je prázdny alebo neplatný.")
                return
            
            total = len(rows) - 1
            for i, row in enumerate(rows[1:], 1):
                if len(row) < 2:
                    continue

                ean, img_url = row[0], row[1]
                img_path = os.path.join(self.target_folder, f"{ean}.jpg")
                
                try:
                    response = requests.get(img_url, timeout=10)
                    response.raise_for_status()
                    with open(img_path, "wb") as img_file:
                        img_file.write(response.content)
                    self.result_text.append(f"✅ {ean}.jpg uložený.")
                except requests.exceptions.RequestException:
                    failed.append(f"{ean} ({img_url})")
                
                # Update the download progress during the download process
                progress = int(i / total * 100)
                self.progress_bar.setValue(progress)  # Update the progress bar
                QApplication.processEvents()  # Make sure the UI updates during download

        if failed:
            self.result_text.append("\n❌ Nepodarilo sa stiahnuť tieto obrázky:")
            for item in failed:
                self.result_text.append(f" - {item}")
        
        self.result_text.append("\n✅ Sťahovanie dokončené.")
        self.progress_bar.setValue(100)  # Ensure the progress bar reaches 100% after completion

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDownloaderApp()
    window.show()
    sys.exit(app.exec())
