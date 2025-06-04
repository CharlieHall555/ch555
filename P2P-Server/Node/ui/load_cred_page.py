from __future__ import annotations  # Type checking


import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QSizePolicy, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.ui_events import UIEvents


import typing

if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents
    from ui.server_interface import ServerInterface
    from ui.api_events import APIEvents

MAX_FONT_SIZE = 30

class LoadCredPage(QWidget):
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.api_loaded = False

        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setupEvents()

    def setupEvents(self) -> None:
        server_events : ServerEvents = self.main_window.server_events
        ui_events : UIEvents = self.main_window.ui_events

        api_events : APIEvents = self.main_window.api_events

        api_events.api_started.connect(
            lambda : self.__setattr__("api_loaded" , True)
        )

        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.voting_info_page)
        )

        self.load_from_file.clicked.connect(
            lambda: ui_events.load_candidate_credentials_from_file.emit()
        )

        self.load_from_mobile.clicked.connect(self.load_from_mobile_clicked)

        server_events.sys_missing_local_creds_file.connect(
            lambda: self.missing_file_alert()
        )

    def load_from_mobile_clicked(self):
        if self.api_loaded:
            self.main_window.switch_page(self.main_window.load_from_mobile_page)  
        else:
            QMessageBox.information(self, "Info", "Server-Loading; Please try again in a few moments.")
      

    def missing_file_alert(self):
        QMessageBox.warning(self, "Failed To Load", "Credentials.json is missing.")

    def focused(self , args):
        server_interface : ServerInterface = self.main_window.server_interface
        if server_interface.server_credentials is not None:
           self.main_window.switch_page(self.main_window.voting_page)   

    def create_widgets(self) -> None:
        self.titleLabel = QLabel("Load Credentials", self)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.load_from_file = QPushButton("Load From File" , self)
        self.load_from_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.load_from_mobile = QPushButton("Load From Phone" , self)
        self.load_from_mobile.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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

        self.center_layout.addWidget(self.load_from_file , 2)
        self.center_layout.addWidget(self.load_from_mobile , 2)
    
        self.center_layout.setSpacing(20)

        self.load_from_file.setMaximumWidth(300)
        self.load_from_file.setMaximumHeight(60)
        self.load_from_file.setMinimumHeight(40)

        self.load_from_mobile.setMaximumWidth(300)
        self.load_from_mobile.setMaximumHeight(60)
        self.load_from_mobile.setMinimumHeight(40)

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
        self.load_from_file.setFont(QFont("Arial", button_text_size))
        self.load_from_mobile.setFont(QFont("Arial", button_text_size))

        label_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 1.5))  # Input field labels

        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  
        super().resizeEvent(event)
