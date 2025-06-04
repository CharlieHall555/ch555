from __future__ import annotations  # Type checking

import sys
import typing
from PyQt5.QtWidgets import QMainWindow ,  QMessageBox, QSpacerItem , QLineEdit , QWidget , QLabel, QPushButton , QVBoxLayout , QHBoxLayout, QGridLayout, QSizePolicy , QAction
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt , pyqtSignal
from utilities.utilities import is_valid_ip, is_valid_port

if typing.TYPE_CHECKING:
    from ui.ui_events import UIEvents

MAX_FONT_SIZE = 30

class AddCandidatePage(QWidget):
    ui_events : UIEvents
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.ui_events = main_window.ui_events
        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setup_events()

    def setup_events(self):


        self.submitButton.clicked.connect(self.submit_button_clicked)

        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.advanced_options)
        )

    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Add Candidate", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.candidateNameLabel = QLabel("Candidate Name" , self)
        self.candidateNameEdit = QLineEdit(self)
        
        self.submitButton = QPushButton("Submit" , self)
        self.submitButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def submit_button_clicked(self):
        candidateName = self.candidateNameEdit.text().strip()
        self.ui_events.add_candidated_pressed.emit(candidateName)

 
    def format(self):
        """Use layouts for full responsiveness and centering."""


        self.layout: QVBoxLayout = QVBoxLayout()

        # Create a container widget for centering
        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)

        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)

        # Create a form-like layout for input fields (host & port)
        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)

        # Add Host input field
        self.form_layout.addWidget(self.candidateNameLabel)
        self.form_layout.addWidget(self.candidateNameEdit)

    
        # Center form layout
        self.form_layout.setAlignment(Qt.AlignCenter)
        self.form_layout.setSpacing(10)

        # Add form widget and button to center layout
        self.center_layout.addWidget(self.form_widget)
        self.center_layout.addWidget(self.submitButton , alignment=Qt.AlignCenter)

        # Center everything
        self.center_layout.setAlignment(Qt.AlignCenter)
        self.center_layout.setSpacing(20)

        # Set widget size constraints
        self.candidateNameLabel.setMaximumWidth(400)
        self.candidateNameEdit.setMaximumWidth(400)
        self.submitButton.setMaximumWidth(400)

        self.submitButton.setMaximumHeight(60)
        self.submitButton.setMinimumHeight(40)

        # Build final layout

        # Build final layout
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

        button_text_size = int(min(int(self.width() * 0.03), MAX_FONT_SIZE))  
        self.submitButton.setFont(QFont("Arial", button_text_size))  
        self.backButton.setFont(QFont("Arial", button_text_size))  

        input_label_size = int(min(int(self.width() * 0.020), MAX_FONT_SIZE // 1.5))  # Input field labels
        self.candidateNameLabel.setFont(QFont("Arial", input_label_size))

        input_text_size = int(min(int(self.width() * 0.025), MAX_FONT_SIZE // 1.5))  # Text inside inputs
        self.candidateNameEdit.setFont(QFont("Arial", input_text_size))

        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
