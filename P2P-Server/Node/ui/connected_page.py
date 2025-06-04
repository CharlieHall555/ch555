from __future__ import annotations  # Type checking

import sys
import typing
from PyQt5.QtWidgets import QMainWindow ,QLineEdit , QWidget , QLabel, QPushButton , QVBoxLayout , QHBoxLayout, QGridLayout, QSizePolicy , QAction
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

if typing.TYPE_CHECKING:
    from ui.server_interface import ServerInterface
    from server.core.server_events import ServerEvents

MAX_FONT_SIZE = 30

class ConnectedPage(QWidget):
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window

        self.create_widgets()
        self.format()
        self.setup_events()
        #self.apply_styles()

    def setup_events(self) -> None:

        server_events : ServerEvents = self.main_window.server_events

        self.voteButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.voting_info_page)
        )

        server_events.blc_snapshot_head_updated.connect(
            lambda value: self.blockchainHead.setText(f"Blockchain Head: {value[:6]}" )
        )

        server_events.blc_became_validator.connect(
            lambda: self.nodeStatus.setText("Node : Validator")
        )

        server_events.blc_became_lead_validator.connect(
            lambda: self.nodeStatus.setText("Node : Lead Validator")
        )

        server_events.blc_no_longer_validator.connect(
            lambda: self.nodeStatus.setText("Node : Validator")
        )
        

    def create_widgets(self):
        """Create all UI elements dynamically."""

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignLeft)

        self.optionsButton = QPushButton("Advanced Options", self)
        self.voteButton = QPushButton("Cast Vote", self)

        self.optionsButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.voteButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
       
        self.statusContainer = QWidget(self)

        self.nodeIdLabel = QLabel(self)
        self.nodeIdLabel.setAlignment(Qt.AlignCenter)


        self.connectionStatus = QLabel("Connection Status", self)
        self.connectionStatus.setAlignment(Qt.AlignCenter)

        self.blockchainHead = QLabel("Blockchain Head" , self)
        self.blockchainHead.setAlignment(Qt.AlignCenter)

        self.nodeStatus = QLabel("Node: Normal" , self)
        self.nodeStatus.setAlignment(Qt.AlignCenter)

        self.optionsButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.advanced_options)
        )

    def display(self):
        server_interface : ServerInterface = self.main_window.server_interface
        n_connections = server_interface.n_connections
        if n_connections > 0:
            self.connectionStatus.setText("Connection Status: Connected")
        else:
            self.connectionStatus.setText("Connection Status: Disconnected")

        self.nodeIdLabel.setText(f"Node Id : {server_interface.node_id}")
    
    def focused(self , args=()):
        self.display()

    def format(self):
        """Use layouts for full responsiveness and centering."""
        self.layout = QVBoxLayout(self)

        self.center_widget = QWidget(self)
        self.center_layout = QVBoxLayout(self.center_widget)

        self.status_layout = QVBoxLayout(self.statusContainer)
        self.status_layout.addWidget(self.connectionStatus)
        self.status_layout.addWidget(self.blockchainHead)
        self.status_layout.addWidget(self.nodeStatus)
        self.status_layout.addWidget(self.nodeIdLabel)
        self.status_layout.setSpacing(10)
        self.statusContainer.setLayout(self.status_layout)

        # Set sensible widget bounds
        for w in [self.optionsButton, self.voteButton]:
            w.setMaximumHeight(80)
            w.setMinimumHeight(30)
            w.setMaximumWidth(400)

        self.center_layout.addWidget(self.statusContainer , 8)
        self.center_layout.addWidget(self.voteButton , 4)
        self.center_layout.addWidget(self.optionsButton , 4)

        self.center_layout.setSpacing(40)
        self.center_layout.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(QWidget(self) , 1) #spacer
        self.layout.addWidget(self.center_widget, 14)
        self.layout.addWidget(self.footerLabel, 1)
        self.layout.setAlignment(Qt.AlignCenter)

        self.setLayout(self.layout)


    def apply_styles(self):
        primary_color = "#6A0DAD" 
        secondary_color = "#E6CCFF" 
        tertiary_color = '#A8A8A8' 

    def resizeEvent(self, event):
        """Dynamically adjust font sizes and widget sizes on resize."""
        font_large = min(int(self.width() * 0.04), MAX_FONT_SIZE)
        font_small = min(int(self.width() * 0.018), MAX_FONT_SIZE // 2)
        footer_text_size = min(int(self.width() * 0.015), MAX_FONT_SIZE // 2) 
    
        self.connectionStatus.setFont(QFont("Arial", font_small))
        self.blockchainHead.setFont(QFont("Arial", font_small))
        self.voteButton.setFont(QFont("Arial", font_large))
        self.nodeStatus.setFont(QFont("Arial", font_small))
        self.optionsButton.setFont(QFont("Arial", font_large))
        self.nodeIdLabel.setFont(QFont("Arial", font_small))
        
        self.footerLabel.setFont(QFont("Arial", footer_text_size))

        super().resizeEvent(event)
