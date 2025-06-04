from __future__ import annotations  # Type checking

import sys
import typing

from PyQt5.QtWidgets import QMainWindow , QMessageBox , QSpacerItem , QLineEdit , QWidget , QLabel, QPushButton , QVBoxLayout , QHBoxLayout, QGridLayout, QSizePolicy , QAction
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from utilities.utilities import is_valid_port

if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents
    from ui.server_interface import ServerInterface
    from ui.ui_events import UIEvents

MAX_FONT_SIZE = 30

class LoadElectorsPage(QWidget):
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setup_events()
    

    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Load", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.textLabel = QLabel(self)
        self.textLabel.setWordWrap(True)
        self.textLabel.setText("Loads all electors from the 'electors.json' file, if found in the working directory. An 'electors.json' can be generated with the generate_electors.py script.")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)


        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.loadButton = QPushButton("Load Electors")
        self.loadButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        

    def setup_events(self):

        ui_events : UIEvents = self.main_window.ui_events
        server_events : ServerEvents = self.main_window.server_events


        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.advanced_options)
        )

        self.loadButton.clicked.connect(
            lambda: ui_events.load_electors_from_file.emit()
        )

        server_events.sys_missing_electors_file.connect(self.missing_electors_file)
        
    def missing_electors_file(self):
        (QMessageBox.warning(self, "Failed To Load", "Electors.json is missing."))


    def format(self):
        """Use layouts for full responsiveness and centering."""
        self.layout: QVBoxLayout = QVBoxLayout()

        # Create a container widget for centering
        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)

        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)

        # Center everything
        self.center_layout.setAlignment(Qt.AlignCenter)
        self.center_layout.setSpacing(20)

        self.center_layout.addWidget(self.textLabel)
        self.center_layout.addWidget(self.loadButton)
      

        self.loadButton.setMaximumWidth(600)
        self.loadButton.setMaximumHeight(60)
        self.loadButton.setMinimumHeight(40)

        self.spacer_after_title = QWidget()
        self.spacer_after_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.header_layout.addWidget(self.backButton , 2)  # Left-aligned button
        self.header_layout.addWidget(self.titleLabel , 6 , alignment=Qt.AlignmentFlag.AlignCenter) # Centered title
        self.header_layout.addWidget(self.spacer_after_title , 2)  # Left-aligned button


        self.layout.addWidget(self.header_widget, 1)
        self.layout.addWidget(self.center_widget, 12)  # Main content
        self.layout.setAlignment(Qt.AlignCenter)  # Full vertical & horizontal centering
        self.layout.addWidget(self.footerLabel, 1)

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
        self.loadButton.setFont(QFont("Arial", button_text_size))

        label_size = int(min(int(self.width() * 0.025), MAX_FONT_SIZE // 1.5))  # Input field labels
        self.textLabel.setFont(QFont("Arial", label_size))

        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
