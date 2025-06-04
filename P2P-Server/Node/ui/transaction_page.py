import sys, json
from PyQt5.QtWidgets import QMainWindow , QMessageBox , QSpacerItem , QLineEdit , QWidget , QLabel, QPushButton , QVBoxLayout , QHBoxLayout, QGridLayout, QSizePolicy , QAction
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from utilities.utilities import is_valid_port

MAX_FONT_SIZE = 30

class TransactionPage(QWidget):
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.parent_blockhash = None
        self.data = None
        self.create_widgets()
        self.format()
        self.apply_styles()

    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Transaction Data", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mainLabel = QLabel("Data" , self)
        self.mainLabel.setAlignment(Qt.AlignCenter)
        self.mainLabel.setWordWrap(True)
        self.mainLabel.setScaledContents(True)
 
        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.block_page , self.parent_blockhash)
        )

    def focused(self , args): #args should be transaction data , parent_blockahs
        assert(args[0] and args[1])
        print(args)
        self.parent_blockhash = args[1]
        self.data = args[0]
        
        self.mainLabel.setText(json.dumps(self.data , sort_keys=True))

    def format(self):
        """Use layouts for full responsiveness and centering."""
        self.layout: QVBoxLayout = QVBoxLayout()

        # Create a container widget for centering
        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)

        # Build final layout

        # Build final layout
        self.spacer_after_title = QWidget()
        self.spacer_after_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.header_layout.addWidget(self.backButton , 2)  # Left-aligned button
        self.header_layout.addWidget(self.titleLabel , 6 , alignment=Qt.AlignmentFlag.AlignCenter) # Centered title
        self.header_layout.addWidget(self.spacer_after_title , 2)  # Left-aligned button

        self.layout.addWidget(self.header_widget, 1)
        self.layout.addWidget(self.mainLabel, 12)  # Main content
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
        self.backButton.setFont(QFont("Arial", button_text_size))  

        text_size = int(min(int(self.width() * 0.1), MAX_FONT_SIZE // 1.5))  # Text inside inputs
        self.mainLabel.setFont(QFont("Arial", text_size))  

        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
