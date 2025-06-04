import sys
from PyQt5.QtWidgets import QMainWindow ,QLineEdit , QWidget , QLabel, QPushButton , QVBoxLayout , QHBoxLayout, QGridLayout, QSizePolicy , QAction
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

MAX_FONT_SIZE = 30

class IndexPage(QWidget):
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window

        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setup_events()

    def setup_events(self):
        self.joinButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.join_page)
        )

        self.createButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.host_page)
        )

    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Home", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.optionsLabel = QLabel("Options" , self)
        self.optionsLabel.setAlignment(Qt.AlignCenter)

        self.joinButton = QPushButton("Join Election Server", self)
        self.createButton = QPushButton("Create Election Server", self)

        self.joinButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.createButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

       

    def format(self):
        """Use layouts for full responsiveness and centering."""
        self.layout: QVBoxLayout = QVBoxLayout()

        # Create a container widget for centering
        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)

        self.center_layout.addWidget(self.optionsLabel)
        self.center_layout.addWidget(self.joinButton)
        self.center_layout.addWidget(self.createButton)

        self.center_layout.setAlignment(Qt.AlignCenter)
        self.center_layout.setSpacing(20)

        self.optionsLabel.setMaximumHeight(80)
        self.optionsLabel.setMinimumHeight(50)

        self.joinButton.setMaximumHeight(80)
        self.joinButton.setMinimumHeight(50)
        self.createButton.setMaximumHeight(80)
        self.createButton.setMinimumHeight(50)

        self.joinButton.setMaximumWidth(400)
        self.createButton.setMaximumWidth(400)
        self.optionsLabel.setMaximumWidth(400)

        self.layout.addWidget(self.titleLabel , 1)
        self.layout.addWidget(self.center_widget , 14)
        self.layout.setAlignment(Qt.AlignCenter)  # Full vertical & horizontal centering
        self.layout.addWidget(self.footerLabel , 1)

        self.setLayout(self.layout)

   

    def apply_styles(self):
        primary_color = "#6A0DAD" 
        secondary_color = "#E6CCFF" 
        tertiary_color = '#A8A8A8' 

    def resizeEvent(self, event):
        """Dynamically adjust font sizes and button sizes on resize."""
        title_text_size = min(int(self.width() * 0.05), MAX_FONT_SIZE) 
        self.titleLabel.setFont(QFont("Arial", title_text_size)) 

        button_text_size = min(int(self.width() * 0.03), MAX_FONT_SIZE)  
        self.joinButton.setFont(QFont("Arial", button_text_size))  
        self.createButton.setFont(QFont("Arial", button_text_size)) 
        self.optionsLabel.setFont(QFont("Arial", button_text_size)) 

        footer_text_size = min(int(self.width() * 0.015), MAX_FONT_SIZE // 2) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
