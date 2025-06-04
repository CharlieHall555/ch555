from __future__ import annotations  # Type checking


import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from utilities.utilities import clamp
import typing
from utilities.book import Book

MAX_FONT_SIZE = 30

class BlockPage(QWidget):
    block_book : Book | None
    block_hash_list : typing.List[str]
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window

        self.block_book = None
        self.page = 0
        self.block_hash = "000000"
        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setupEvents()

    def setupEvents(self):

        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.blockchain_page)
        )

    def leftButtonClicked(self):
        self.page -= 1  
        self.page = clamp(self.page , 0 , self.block_book.length - 1)
        self.change_page()

    def rightButtonClicked(self):
        self.page += 1 
        self.page = clamp(self.page , 0 , self.block_book.length - 1)
        self.change_page()

    def change_page(self) -> None:
        self.pageTitleLabel.setText(f"page : {self.page}")
        if self.block_book is None or self.block_book.length <= 0: return
        page_data : typing.List[dict] = self.block_book.get_page(self.page)
        each_button : QPushButton
        for each_button in self.buttonList:
            each_button.setText("")
            each_button.buttonData = None

        for i, each_button in enumerate(self.buttonList):
            if 0 <= i < len(page_data):
                transaction_data = page_data[i]
                each_button.buttonData = transaction_data
                each_button.setText(transaction_data.get("operation" , ""))

        
    def create_block_button(self, block_number: int) -> QPushButton:
        button = QPushButton("", self)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setMinimumHeight(40)
        button.setFont(QFont("Arial", 14))
        button.clicked.connect(
            lambda:  self.transactionButtonClicked(button)
        )
        return button   
    
    def transactionButtonClicked(self , button):
        if hasattr(button , "buttonData") and button.buttonData is not None:
            self.main_window.switch_page(self.main_window.transaction_page , button.buttonData , self.block_hash)


    def focused(self , args):
        assert(args[0])
        self.block_hash = args[0]
        self.display()

    def display(self) -> None:
        self.titleLabel.setText(f"Block: {self.block_hash[:6]}")

        serialized_block : dict | None = self.main_window.server_interface.lookup_block(self.block_hash)
        if serialized_block is None: return
        block_data = serialized_block.get("data" , None)
        if block_data is None: return
        self.block_book = Book(block_data , 10)
        self.change_page()

    def create_widgets(self):
        self.titleLabel = QLabel("Block: None", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.pageTitleLabel = QLabel("Page: None" , self)
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

        self.navLeftButton.clicked.connect(self.leftButtonClicked)
        self.navRightButton.clicked.connect(self.rightButtonClicked)

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


        self.layout.addWidget(self.header_widget, 2)
        self.layout.addWidget(self.pageTitleLabel, 1)
        self.layout.addWidget(self.blockList, 14)
        self.layout.addLayout(self.navLayout)
        self.layout.addWidget(self.footerLabel, 1)

        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
       
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
