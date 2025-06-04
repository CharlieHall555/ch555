from __future__ import annotations  # Type checking


import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from utilities.utilities import clamp
import typing
from utilities.book import Book

if typing.TYPE_CHECKING:
    from ui.server_interface import ServerInterface

MAX_FONT_SIZE = 30

class NodeDirectoryPage(QWidget):
    server_interface : ServerInterface
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window

        self.server_interface = self.main_window.server_interface
        self.page = 0
        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setupEvents()

    def create_widgets(self):
        self.titleLabel = QLabel("Node Directory", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.pageTitleLabel = QLabel("Page : None" , self)
        self.pageTitleLabel.setAlignment(Qt.AlignCenter)

        self.blockList = QWidget(self)
        self.blockList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.navLeftButton = QPushButton("<", self)
        self.navRightButton = QPushButton(">", self)

        self.navLeftButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.navRightButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignLeft)

   
        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.advanced_options)
        )

        self.navLeftButton.clicked.connect(self.leftButtonClicked)
        self.navRightButton.clicked.connect(self.rightButtonClicked)

    def leftButtonClicked(self):
        self.page -= 1  
        self.page = clamp(self.page , 0 , self.nodes_book.length - 1)
        self.reload_page()

    def rightButtonClicked(self):
        self.page += 1 
        self.page = clamp(self.page , 0 , self.nodes_book.length - 1)
        self.reload_page()


    def reload_page(self) -> None:
        
        self.pageTitleLabel.setText(f"Page: {self.page}")

        page_data : typing.List[dict] = self.nodes_book.get_page(self.page)
        each_button : QPushButton
        for each_button in self.buttonList: #reset buttons
            each_button.setText("")

        for i, each_button in enumerate(self.buttonList):
            if 0 <= i < len(page_data):
                node_hash = page_data[i].get("node_id" , "")
                text = node_hash
                if self.server_interface.node_id == node_hash:
                    text += " (self)"
                print("vlist =" , self.server_interface.validator_list)
                if node_hash in self.server_interface.validator_list:
                    text += " (validator)"
                each_button.setText(text)
                if node_hash == self.server_interface.lead_validator:
                    text += " (lead)"
                    
                each_button.setText(text)


    def create_block_button(self, block_number: int) -> QPushButton:
        button = QPushButton("", self)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setMinimumHeight(40)
        button.setFont(QFont("Arial", 14))
        return button


    def format(self):
        self.layout = QVBoxLayout()

        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)

        self.navLayout = QHBoxLayout()
        self.navLayout.addWidget(self.navLeftButton)
        self.navLayout.addStretch()
        self.navLayout.addWidget(self.navRightButton)

        self.blockListLayout = QVBoxLayout()
        self.blockList.setLayout(self.blockListLayout)

        self.buttonList = []

        for i in range(0 , 10):
            b = self.create_block_button(i)
            self.buttonList.append(b)
            self.blockListLayout.addWidget(b)

    
        self.titleLabel.setMaximumHeight(80)
        self.titleLabel.setMinimumHeight(50)

        self.header_layout.addWidget(self.backButton , 2)
        self.header_layout.addWidget(self.titleLabel , 4)
        self.header_layout.addWidget(QWidget() , 2)

        self.navLeftButton.setMaximumWidth(100)
        self.navRightButton.setMaximumWidth(100)

        self.blockList.setMinimumHeight(400)

        self.layout.addWidget(self.header_widget, 1)
        self.layout.addWidget(self.pageTitleLabel , 1)
        self.layout.addWidget(self.blockList, 14)
        self.layout.addLayout(self.navLayout)
        self.layout.addWidget(self.footerLabel, 1)

        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

    def setupEvents(self):
        pass

    def focused(self , *args):
        self.display()


    def display(self):
        print(list(self.server_interface.node_directory.values()))
        self.nodes_book = Book(data=list(self.server_interface.node_directory.values()) , page_size=10)
        self.reload_page()

    def apply_styles(self):
        primary_color = "#6A0DAD"
        secondary_color = "#E6CCFF"
        tertiary_color = '#A8A8A8'

    def resizeEvent(self, event):
        title_size = min(int(self.width() * 0.05), MAX_FONT_SIZE)
        self.titleLabel.setFont(QFont("Arial", title_size))

        list_font_size = min(int(self.width() * 0.025), MAX_FONT_SIZE)
        self.blockList.setFont(QFont("Arial", list_font_size))

        self.pageTitleLabel.setFont(QFont("Arial", list_font_size))

        nav_font_size = min(int(self.width() * 0.03), MAX_FONT_SIZE)
        self.navLeftButton.setFont(QFont("Arial", nav_font_size))
        self.navRightButton.setFont(QFont("Arial", nav_font_size))
        self.backButton.setFont(QFont("Arial", nav_font_size))
        
        footer_size = min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)
        self.footerLabel.setFont(QFont("Arial", footer_size))

        super().resizeEvent(event)
