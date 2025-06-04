from __future__ import annotations  # Type checking
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton,  QVBoxLayout, QHBoxLayout, QListWidget, QSizePolicy, QMessageBox
from PyQt5.QtGui import QFont , QPixmap
from PyQt5.QtCore import Qt
from ui.ui_events import UIEvents
from ui.api_events import APIEvents
from utilities.qr_codes import generate_qr
from utilities.authentication import generate_sha256_hash
import typing

if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents

MAX_FONT_SIZE = 30

class LoadFromMobilePage(QWidget):
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
            lambda: self.main_window.switch_page(self.main_window.load_cred_page)
        )

      
    def missing_file_alert(self):
        QMessageBox.warning(self, "Failed To Load", "Credentials.json is missing.")

    def focused(self , args):
        import random 
        url = f"https://{self.main_window.local_ip}:{self.main_window.mobile_api_port}/credentials"
        generate_qr(url)
        qrImage = QPixmap("qr.png")
        if not qrImage.isNull():
            self.qrCode.setPixmap(qrImage)

        self.linkCode.setText(
            f"Link Code: {generate_sha256_hash(url)[:4]}"
        )
        
        

    def create_widgets(self) -> None:
        self.titleLabel = QLabel("Load From Mobile", self)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.qrCode = QLabel(self)
        self.linkCode = QLabel(self)
        self.linkCode.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        self.center_layout.addWidget(self.qrCode , 2)
        self.center_layout.addWidget(self.linkCode , 1)

        self.center_layout.setSpacing(20)

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


        label_size = int(min(int(self.width() * 0.03), MAX_FONT_SIZE // 1.5))  # Input field labels
        self.linkCode.setFont(QFont("Arial", label_size))


        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  
        super().resizeEvent(event)
