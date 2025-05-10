import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Main window setup
        self.setWindowTitle("Universal App")
        self.setMinimumSize(900, 600)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create sidebar for navigation
        self.setup_sidebar()
        
        # Create stacked widget for main content area
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack, 1)
        
        # Add placeholder pages
        self.setup_pages()
        
        # Set the initial page
        self.content_stack.setCurrentIndex(0)

    def setup_sidebar(self):
        # Create sidebar widget and layout
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar.setStyleSheet("background-color: #2C3E50;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        
        # Add title to sidebar
        title = QLabel("Universal App")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)
        
        # Add separator
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3E5771;")
        sidebar_layout.addWidget(separator)
        sidebar_layout.addSpacing(20)
        
        # Create navigation buttons
        self.nav_buttons = []
        nav_items = [
            {"name": "Home", "id": 0},
            {"name": "Project One", "id": 1},
            {"name": "Project Two", "id": 2},
            {"name": "Project Three", "id": 3},
            {"name": "Settings", "id": 4}
        ]
        
        for item in nav_items:
            button = QPushButton(item["name"])
            button.setCheckable(True)
            button.setFixedHeight(40)
            button.setStyleSheet("""
                QPushButton {
                    color: white;
                    border: none;
                    text-align: left;
                    padding-left: 15px;
                    border-radius: 5px;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #34495E;
                }
                QPushButton:checked {
                    background-color: #3498DB;
                }
            """)
            button.clicked.connect(lambda checked, idx=item["id"]: self.change_page(idx))
            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)
        
        # Set the first button as checked
        self.nav_buttons[0].setChecked(True)
        
        # Add stretch to push remaining items to bottom
        sidebar_layout.addStretch()
        
        self.main_layout.addWidget(sidebar)

    def setup_pages(self):
        # Create placeholder pages for the content area
        pages = [
            self.create_page("Welcome to Universal App", 
                            "This is the central hub for all projects. Select a project from the sidebar to begin."),
            self.create_page("Project One", 
                            "Project One content will appear here."),
            self.create_page("Project Two", 
                            "Project Two content will appear here."),
            self.create_page("Project Three", 
                            "Project Three content will appear here."),
            self.create_page("Settings", 
                            "Application settings will appear here.")
        ]
        
        for page in pages:
            self.content_stack.addWidget(page)

    def create_page(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Page title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(separator)
        layout.addSpacing(20)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 16px; color: #333;")
        layout.addWidget(desc_label)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return page

    def change_page(self, index):
        # Update button states
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)
        
        # Change the current page
        self.content_stack.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())