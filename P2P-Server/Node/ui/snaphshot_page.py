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

MAX_FONT_SIZE = 30

class SnapshotPage(QWidget):
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.host_signal = main_window.host_signal
        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setupEvents()

    def setupEvents(self) -> None:
        server_events : ServerEvents = self.main_window.server_events

        server_events.blc_snapshot_head_updated.connect(
            self.display
        )

    def focused(self , args=()) -> None:
        self.display()


    def display(self) -> None:
        server_interface : ServerInterface = self.main_window.server_interface
        if server_interface.blockchain_head:
            self.blockChainHashLabel.setText(f"Blockchain Head: {server_interface.blockchain_head[:6]}")
        if server_interface.lead_validator:
            self.leadValidatorLabel.setText(f"Lead-Validator: {server_interface.lead_validator}")   
        if server_interface.validator_list:
            self.numberOfValidatorsLabel.setText(f"Number Of Validators: {len(server_interface.validator_list)}")  

    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Snapshot", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.blockChainHashLabel = QLabel("Hash" , self)
        self.blockChainHashLabel.setWordWrap(True)
        self.numberOfValidatorsLabel = QLabel("Number of Validators" , self)
        self.leadValidatorLabel = QLabel("lead Validator")

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.advanced_options)
        )


    def format(self):
        """Use layouts for full responsiveness and centering."""
        self.layout: QVBoxLayout = QVBoxLayout()

        # Create a container widget for centering
        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)

        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)

        self.center_layout.addWidget(self.blockChainHashLabel)
        self.center_layout.addWidget(self.leadValidatorLabel)
        self.center_layout.addWidget(self.numberOfValidatorsLabel)

        # Center everything
        self.center_layout.setAlignment(Qt.AlignCenter)
        self.center_layout.setSpacing(20)

        # Set widget size constraints

        self.blockChainHashLabel.setMaximumWidth(600)
        self.blockChainHashLabel.setMaximumHeight(60)
        self.blockChainHashLabel.setMinimumHeight(40)

        self.numberOfValidatorsLabel.setMaximumWidth(400)
        self.numberOfValidatorsLabel.setMaximumHeight(60)
        self.numberOfValidatorsLabel.setMinimumHeight(40)

        self.leadValidatorLabel.setMaximumWidth(400)
        self.leadValidatorLabel.setMaximumHeight(60)
        self.leadValidatorLabel.setMinimumHeight(40)

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

        button_text_size = min(int(self.width() * 0.03), MAX_FONT_SIZE)  
        self.backButton.setFont(QFont("Arial", button_text_size))

        label_size = int(min(int(self.width() * 0.025), MAX_FONT_SIZE // 1.5))  # Input field labels
        self.numberOfValidatorsLabel.setFont(QFont("Arial", label_size))
        self.leadValidatorLabel.setFont(QFont("Arial", label_size))
        self.blockChainHashLabel.setFont(QFont("Arial", label_size))


        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
