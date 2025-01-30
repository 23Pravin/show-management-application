import sys
import requests
import os
import re
from PySide2.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                              QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QPushButton, 
                              QDialog, QLineEdit, QLabel, QFormLayout, QTextEdit, QScrollArea, 
                              QFileDialog)
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from urllib.request import urlopen
import shutil

class AddShowDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Show")
        self.setModal(True)
        
        layout = QFormLayout()
        self.name_input = QLineEdit()
        self.code_input = QLineEdit()
        
        # Add validation
        self.name_input.textChanged.connect(self.validate_input)
        self.code_input.textChanged.connect(self.validate_input)
        
        # Add error labels
        self.name_error = QLabel()
        self.name_error.setStyleSheet("color: red")
        self.code_error = QLabel()
        self.code_error.setStyleSheet("color: red")
        
        # Image selection
        image_layout = QHBoxLayout()
        self.image_path = QLineEdit()
        self.image_path.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(self.image_path)
        image_layout.addWidget(browse_btn)
        
        layout.addRow("Show Name:", self.name_input)
        layout.addRow("", self.name_error)
        layout.addRow("Show Code:", self.code_input)
        layout.addRow("", self.code_error)
        layout.addRow("Image:", image_layout)
        
        self.submit_btn = QPushButton("Add")
        self.submit_btn.clicked.connect(self.accept)
        self.submit_btn.setEnabled(False)
        layout.addRow(self.submit_btn)
        
        self.setLayout(layout)
        
    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.image_path.setText(file_name)
    
    def validate_input(self):
        name_valid = True
        code_valid = True
        
        # Validate name
        name = self.name_input.text()
        if not name:
            self.name_error.setText("Name is required")
            name_valid = False
        elif not re.match("^[a-zA-Z0-9_]+$", name):
            self.name_error.setText("Name can only contain letters, numbers and underscore")
            name_valid = False
        else:
            self.name_error.setText("")
        
        # Validate code
        code = self.code_input.text()
        if not code:
            self.code_error.setText("Code is required")
            code_valid = False
        elif not re.match("^[A-Z][0-9]+$", code):
            self.code_error.setText("Code must start with uppercase letter followed by numbers")
            code_valid = False
        else:
            self.code_error.setText("")
        
        # Enable/disable submit button
        self.submit_btn.setEnabled(name_valid and code_valid)

class ShowListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Show List")
        self.setGeometry(100, 100, 800, 500)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.server_url = "http://localhost:3000"
        self.initUI()

    def initUI(self):
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left pane
        left_pane = QWidget()
        left_layout = QVBoxLayout()
        
        # Table first
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Show Name", "Show Code"])
        self.tableWidget.selectionModel().selectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.tableWidget)
        
        # Create button at bottom
        create_btn = QPushButton("Add Show")
        create_btn.clicked.connect(self.show_add_dialog)
        create_btn.setFixedHeight(40)  # Make button slightly bigger
        create_btn.setStyleSheet("QPushButton { font-weight: bold; }")  # Make it stand out
        left_layout.addWidget(create_btn)
        
        left_pane.setLayout(left_layout)
        
        # Right pane
        right_pane = QWidget()
        right_layout = QVBoxLayout()
        
        self.details_label = QLabel("Show Details")
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)
        
        # Add image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 200)
        
        # Add scroll area for image
        scroll = QScrollArea()
        scroll.setWidget(self.image_label)
        scroll.setWidgetResizable(True)
        
        right_layout.addWidget(self.details_label)
        right_layout.addWidget(self.details_text)
        right_layout.addWidget(scroll)
        
        right_pane.setLayout(right_layout)
        
        # Add panes to main layout
        main_layout.addWidget(left_pane, 1)
        main_layout.addWidget(right_pane, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.load_data()

    def get_next_image_number(self):
        images_dir = os.path.join(self.base_path, "public", "images")
        if not os.path.exists(images_dir):
            return 1
        
        existing_images = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not existing_images:
            return 1
            
        numbers = [int(os.path.splitext(f)[0]) for f in existing_images if os.path.splitext(f)[0].isdigit()]
        return max(numbers, default=0) + 1

    def show_add_dialog(self):
        dialog = AddShowDialog(self)
        if dialog.exec_():
            try:
                # Validate again before submitting
                name = dialog.name_input.text()
                code = dialog.code_input.text()
                
                if not re.match("^[a-zA-Z0-9_]+$", name) or not re.match("^[A-Z][0-9]+$", code):
                    QMessageBox.critical(self, "Error", "Invalid input detected")
                    return
                
                response = requests.get("http://localhost:3000/shows")
                shows = response.json()
                next_id = max([show.get('id', 0) for show in shows], default=0) + 1

                # Handle image
                relative_path = ""
                if dialog.image_path.text():
                    # Get next image number
                    next_image_num = self.get_next_image_number()
                    image_filename = f"{next_image_num}.png"  # Always use .png extension
                    
                    # Ensure public/images directory exists
                    images_dir = os.path.join(self.base_path, "public", "images")
                    os.makedirs(images_dir, exist_ok=True)
                    
                    # Copy and convert image to PNG
                    image_path = os.path.join(images_dir, image_filename)
                    
                    # Load and save as PNG using QPixmap
                    pixmap = QPixmap(dialog.image_path.text())
                    pixmap.save(image_path, "PNG")
                    
                    # Use server URL for image path
                    relative_path = f"{self.server_url}/images/{image_filename}"

                new_show = {
                    "id": next_id,
                    "name": dialog.name_input.text(),
                    "code": dialog.code_input.text(),
                    "imageUrl": relative_path
                }
                
                response = requests.post("http://localhost:3000/shows", json=new_show)
                response.raise_for_status()
                self.load_data()
                QMessageBox.information(self, "Success", "Show added successfully!")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Error", f"Failed to add show: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy image: {e}")

    def load_image_from_url(self, url):
        try:
            print(f"Attempting to load image from: {url}")  # Debug print
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.content
            pixmap = QPixmap()
            loaded = pixmap.loadFromData(data)
            
            if not loaded or pixmap.isNull():
                print(f"Failed to create pixmap from data")  # Debug print
                return None
                
            print(f"Successfully loaded image, size: {pixmap.width()}x{pixmap.height()}")  # Debug print
            scaled_pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return scaled_pixmap
        except Exception as e:
            print(f"Error loading image: {str(e)}")  # Debug print
            return None

    def on_selection_changed(self, selected, deselected):
        if selected.indexes():
            row = selected.indexes()[0].row()
            try:
                response = requests.get(f"{self.server_url}/shows")
                shows = response.json()
                show = shows[row]
                
                self.details_text.setText(f"Name: {show['name']}\nCode: {show['code']}\nImage URL: {show['imageUrl']}")
                
                if 'imageUrl' in show and show['imageUrl']:
                    print(f"Loading image for show: {show['name']}")  # Debug print
                    pixmap = self.load_image_from_url(show['imageUrl'])
                    if pixmap:
                        self.image_label.setPixmap(pixmap)
                        print("Successfully set pixmap to label")  # Debug print
                    else:
                        self.image_label.setText("Image not available")
                        print("Failed to load image")  # Debug print
                else:
                    self.image_label.clear()
                    self.image_label.setText("No image available")
                    
            except Exception as e:
                print(f"Error in selection change: {str(e)}")  # Debug print
                QMessageBox.critical(self, "Error", f"Failed to load show details: {e}")

    def load_data(self):
        try:
            response = requests.get("http://localhost:3000/shows")
            response.raise_for_status()
            shows = response.json()

            self.tableWidget.setRowCount(len(shows))
            for row, show in enumerate(shows):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(show["name"]))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(show["code"]))
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShowListWindow()
    window.show()
    sys.exit(app.exec_())
