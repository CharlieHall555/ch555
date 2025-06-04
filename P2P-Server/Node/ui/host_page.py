import sys
from PyQt5.QtWidgets import QMainWindow , QMessageBox , QSpacerItem , QLineEdit , QWidget , QLabel, QPushButton , QVBoxLayout , QHBoxLayout, QGridLayout, QSizePolicy , QAction
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from utilities.utilities import is_valid_port

MAX_FONT_SIZE = 30

class HostPage(QWidget):
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.host_signal = main_window.host_signal
        self.create_widgets()
        self.format()
        self.apply_styles()

    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Host", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.portLabel = QLabel("Port" , self)
        self.portEdit = QLineEdit(self)
        
        self.hostButton = QPushButton("Host" , self)
        self.hostButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.index_page)
        )

        self.hostButton.clicked.connect(self.host_button_clicked)


    def host_button_clicked(self):
        port_value = self.portEdit.text()
        if is_valid_port(port_value) == False:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid port number.")
            return
        
        port_value = int(port_value)
        self.host_signal.emit(port_value)

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

        # Add Port input field
        self.form_layout.addWidget(self.portLabel)
        self.form_layout.addWidget(self.portEdit)

        # Center form layout
        self.form_layout.setAlignment(Qt.AlignCenter)
        self.form_layout.setSpacing(10)

        # Add form widget and button to center layout
        self.center_layout.addWidget(self.form_widget)
        self.center_layout.addWidget(self.hostButton , alignment=Qt.AlignCenter)

        # Center everything
        self.center_layout.setAlignment(Qt.AlignCenter)
        self.center_layout.setSpacing(20)

        # Set widget size constraints
        self.portLabel.setMaximumWidth(400)
        self.portEdit.setMaximumWidth(400)
        self.hostButton.setMaximumWidth(400)

        self.hostButton.setMaximumHeight(60)
        self.hostButton.setMinimumHeight(40)

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
        self.hostButton.setFont(QFont("Arial", button_text_size))  
        self.backButton.setFont(QFont("Arial", button_text_size))  

        input_label_size = int(min(int(self.width() * 0.025), MAX_FONT_SIZE // 1.5))  # Input field labels
        self.portLabel.setFont(QFont("Arial", input_label_size))

        input_text_size = int(min(int(self.width() * 0.025), MAX_FONT_SIZE // 1.5))  # Text inside inputs
        self.portEdit.setFont(QFont("Arial", input_text_size))

        footer_text_size = int(min(int(self.width() * 0.015), MAX_FONT_SIZE // 2)) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
