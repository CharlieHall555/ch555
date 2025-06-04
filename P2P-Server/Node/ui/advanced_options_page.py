from __future__ import annotations  # Type checking


import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QSizePolicy, QGridLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from utilities.utilities import clamp
import typing
from utilities.book import Book

MAX_FONT_SIZE = 30

class AdvancedOptions(QWidget):
    v_layou : QVBoxLayout   
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window

        self.page = 0
        self.create_widgets()
        self.format()
        self.setup_events()
        self.apply_styles()



    def create_widgets(self):
        self.titleLabel = QLabel("Advanced Options", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignLeft)

        self.addCandidateButton = QPushButton("Add Candidate" , self)
        self.addCandidateButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.viewCandidateButton = QPushButton("View Candidates" , self)
        self.viewCandidateButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.blockchainHistoryButton = QPushButton("View Blockchain" , self)
        self.blockchainHistoryButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.snapShotButton = QPushButton("View Snapshot" , self)
        self.snapShotButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.addValidatorButton = QPushButton("Add Validator" , self)
        self.addValidatorButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.loadElectorsButton = QPushButton("Load Electors")
        self.loadElectorsButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.nodeDirectoryButton = QPushButton("Node Directory")
        self.nodeDirectoryButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.showVoteButton = QPushButton("Vote Tally")
        self.showVoteButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def setup_events(self):

        self.showVoteButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.vote_dispaly_page)
        )

        self.blockchainHistoryButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.blockchain_page)
        )

        self.snapShotButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.snapshot_page)
        )

        self.viewCandidateButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.show_candidates_page)
        )

        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.connected_page)
        )

        self.loadElectorsButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.add_elector_page)
        )

        self.addCandidateButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.add_candidate_page)
        )

        self.addValidatorButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.add_validator_page)
        )

        self.nodeDirectoryButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.node_directory_page)
        )

    def format(self) -> None:
        self.v_layou = QVBoxLayout()

        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)

        self.titleLabel.setMaximumHeight(80)
        self.titleLabel.setMinimumHeight(50)

        self.center_widget = QWidget()
        self.center_layout = QGridLayout(self.center_widget)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.setSpacing(20)


        self.blockchainHistoryButton.setMaximumHeight(80)
        self.blockchainHistoryButton.setMinimumHeight(50)
        self.blockchainHistoryButton.setMaximumWidth(400)

        self.nodeDirectoryButton.setMaximumHeight(80)
        self.nodeDirectoryButton.setMinimumHeight(50)
        self.nodeDirectoryButton.setMaximumWidth(400)

        self.snapShotButton.setMaximumHeight(80)
        self.snapShotButton.setMinimumHeight(50)
        self.snapShotButton.setMaximumWidth(400)

        self.addValidatorButton.setMaximumHeight(80)
        self.addValidatorButton.setMinimumHeight(50)
        self.addValidatorButton.setMaximumWidth(400)

        
        self.loadElectorsButton.setMaximumHeight(80)
        self.loadElectorsButton.setMinimumHeight(50)
        self.loadElectorsButton.setMaximumWidth(400)

        self.addCandidateButton.setMaximumHeight(80)
        self.addCandidateButton.setMinimumHeight(50)
        self.addCandidateButton.setMaximumWidth(400)

        self.viewCandidateButton.setMaximumHeight(80)
        self.viewCandidateButton.setMinimumHeight(50)
        self.viewCandidateButton.setMaximumWidth(400)

        self.showVoteButton.setMaximumHeight(80)
        self.showVoteButton.setMinimumHeight(50)
        self.showVoteButton.setMaximumWidth(400)

        self.center_layout.addWidget(self.blockchainHistoryButton , 1 , 0)
        self.center_layout.addWidget(self.snapShotButton , 2 , 0)
        self.center_layout.addWidget(self.addValidatorButton , 3 , 0)
        self.center_layout.addWidget(self.loadElectorsButton , 4 , 0)
        self.center_layout.addWidget(self.addCandidateButton , 1 , 1)
        self.center_layout.addWidget(self.viewCandidateButton , 2 , 1)
        self.center_layout.addWidget(self.nodeDirectoryButton , 3 , 1)
        self.center_layout.addWidget(self.showVoteButton , 4 , 1)

        self.header_layout.addWidget(self.backButton , 2)
        self.header_layout.addWidget(self.titleLabel , 4)
        self.header_layout.addWidget(QWidget() , 2)

        self.v_layou.addWidget(self.header_widget, 1)
        self.v_layou.addWidget(self.center_widget , 14)
        self.v_layou.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Full vertical & horizontal centering
        self.v_layou.addWidget(self.footerLabel, 1)

        self.v_layou.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.v_layou)


    def apply_styles(self):
        primary_color = "#6A0DAD"
        secondary_color = "#E6CCFF"
        tertiary_color = '#A8A8A8'

    def resizeEvent(self, event):
        title_size = min(int(self.width() * 0.05), MAX_FONT_SIZE)
        self.titleLabel.setFont(QFont("Arial", title_size))

        button_text_size = min(int(self.width() * 0.03), MAX_FONT_SIZE)  
        self.blockchainHistoryButton.setFont(QFont("Arial", button_text_size))
        self.backButton.setFont(QFont("Arial", button_text_size))
        self.snapShotButton.setFont(QFont("Arial", button_text_size))
        self.addValidatorButton.setFont(QFont("Arial", button_text_size))
        self.loadElectorsButton.setFont(QFont("Arial", button_text_size))
        self.addCandidateButton .setFont(QFont("Arial", button_text_size))
        self.viewCandidateButton.setFont(QFont("Arial", button_text_size))
        self.nodeDirectoryButton.setFont(QFont("Arial", button_text_size))
        self.showVoteButton.setFont(QFont("Arial", button_text_size))


        footer_size = min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)
        self.footerLabel.setFont(QFont("Arial", footer_size))

        super().resizeEvent(event)
