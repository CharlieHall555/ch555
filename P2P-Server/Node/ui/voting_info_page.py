from __future__ import annotations  # Type checking


import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QSizePolicy, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.ui_events import UIEvents

import typing

if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents

MAX_FONT_SIZE = 30

class VotingInfoPage(QWidget):
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window

        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setupEvents()

    def setupEvents(self) -> None:
        server_events : ServerEvents = self.main_window.server_events
        ui_events : UIEvents = self.main_window.ui_events
        
        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.connected_page)
        )

        self.submitButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.load_cred_page)
        )

    def missing_file_alert(self):
        QMessageBox.warning(self, "Failed To Load", "Credentials.json is missing.")

    def focused(self , args):
        pass

    def create_widgets(self) -> None:
        self.titleLabel = QLabel("Voting Instructions", self)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mainTextLabel = QLabel("You can only vote once.\n You cannot change your vote after voting." , self)
        self.mainTextLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.submitButton = QPushButton("I Understand", self)
        self.submitButton.setSizePolicy(QSizePolicy.Expanding , QSizePolicy.Expanding)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def format(self):
        self.layout = QVBoxLayout()

        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)
    
        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.titleLabel.setMaximumHeight(80)
        self.titleLabel.setMinimumHeight(50)

        self.header_layout.addWidget(self.backButton , 2)
        self.header_layout.addWidget(self.titleLabel , 4)
        self.header_layout.addWidget(QWidget() , 2)

        self.center_layout.addWidget(self.mainTextLabel , 6)
        self.center_layout.addWidget(self.submitButton , 2)

        self.submitButton.setMaximumWidth(300)
        self.submitButton.setMaximumHeight(60)
        self.submitButton.setMinimumHeight(40)

        self.layout.addWidget(self.header_widget, 1)
        self.layout.addWidget(self.center_widget , 12)
        self.layout.addWidget(self.footerLabel , 1)
        
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout)
       
    def apply_styles(self):
        primary_color = "#6A0DAD"
        secondary_color = "#E6CCFF"
        tertiary_color = '#A8A8A8'

    def resizeEvent(self, event):
        """Dynamically adjust font sizes and button sizes on resize."""
        title_text_size = int(min(int(self.width() * 0.05), MAX_FONT_SIZE))
        self.titleLabel.setFont(QFont("Arial", title_text_size))  

        button_text_size = min(int(self.width() * 0.03), MAX_FONT_SIZE)  
        self.backButton.setFont(QFont("Arial", button_text_size))
        self.submitButton.setFont(QFont("Arial", button_text_size))

        label_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 1.5))  # Input field labels
        self.mainTextLabel.setFont(QFont("Arial", label_size))

        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  
        super().resizeEvent(event)
