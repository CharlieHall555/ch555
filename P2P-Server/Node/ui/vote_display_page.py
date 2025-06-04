import sys
import typing
from PyQt5.QtWidgets import QMainWindow ,QLineEdit , QWidget , QMessageBox,  QLabel, QPushButton , QCheckBox ,QComboBox, QVBoxLayout , QHBoxLayout, QGridLayout, QSizePolicy , QAction
from PyQt5.QtGui import QFont , QIcon
from PyQt5.QtCore import Qt

if typing.TYPE_CHECKING:
    from ui.server_interface import ServerInterface
    from server.core.server_events import ServerEvents
    from ui.ui_events import UIEvents

MAX_FONT_SIZE = 30

class VoteDisplayPage(QWidget):
    candidates : typing.List[str]
    name_id_mapping = typing.Dict[str,int]
    def __init__(self , main_window : QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.candidates = []
        self.name_id_mapping = {} # type: ignore
        self.create_widgets()
        self.format()
        self.apply_styles()
        self.setup_events()

    def setup_events(self) -> None:

        server_events : ServerEvents = self.main_window.server_events
        
        self.backButton.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.advanced_options)
        )

        self.candidateDropDown.currentTextChanged.connect(
            self.drop_down_change
        )


    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Vote Display Page", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.subtitleLabel = QLabel("Current Vote Tally", self) 
        self.subtitleLabel.setAlignment(Qt.AlignCenter)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.tallyLabel = QLabel("Tally:" , self)
        self.tallyLabel.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.candidateDropDown = QComboBox()


    def format(self):
        """Use layouts for full responsiveness and centering."""
        self.layout: QVBoxLayout = QVBoxLayout()

        # Create a container widget for centering
        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)
        
        self.header_widget = QWidget()
        self.header_layout : QHBoxLayout = QHBoxLayout(self.header_widget)


        self.header_layout.addWidget(self.backButton , 2)
        self.header_layout.addWidget(self.titleLabel , 4)
        self.header_layout.addWidget(QWidget() , 2)

        self.center_layout.addWidget(self.subtitleLabel , 1)
        self.center_layout.addWidget(self.tallyLabel , 1)
        self.center_layout.addWidget(self.candidateDropDown , 1)

        self.center_layout.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.header_widget , 1)

        self.layout.addWidget(QWidget(self) ,5)
        self.layout.addWidget(self.center_widget , 4)
        self.layout.addWidget(QWidget(self) , 5)
        self.layout.setAlignment(Qt.AlignCenter)  # Full vertical & horizontal centering
        self.layout.addWidget(self.footerLabel , 1)

        self.setLayout(self.layout)

    def update_dropdown(self):
        self.candidateDropDown.clear()
        self.candidateDropDown.addItems(self.candidates)

    def drop_down_change(self):
        current_text = self.candidateDropDown.currentText()
        server_interface : ServerInterface = self.main_window.server_interface

        candidate_name = current_text
        candidate_id = self.name_id_mapping.get(candidate_name , None)
        if candidate_id is None: return
        candidate_id = int(candidate_id)
        vote_tally_for_candidate = server_interface.vote_tally.get(candidate_id , 0)

        self.tallyLabel.setText(f"Tally: {vote_tally_for_candidate}")

        print(self.name_id_mapping)
        print(self.candidates)
        print(server_interface.vote_tally)


        pass

    def focused(self , args : typing.Tuple):
        self.name_id_mapping = {} # type: ignore
        self.candidates = []
        server_interface : ServerInterface = self.main_window.server_interface
        for candidate_info in server_interface.candidates:
            name : str = candidate_info[0]
            id_ : int = int(candidate_info[1])
            self.candidates.append(name)
            self.name_id_mapping[name] = id_ # type: ignore
        self.update_dropdown()    

        

    def apply_styles(self):
        primary_color = "#6A0DAD" 
        secondary_color = "#E6CCFF" 
        tertiary_color = '#A8A8A8' 

    def resizeEvent(self, event):
        """Dynamically adjust font sizes and button sizes on resize."""
        title_text_size = min(int(self.width() * 0.05), MAX_FONT_SIZE) 
        self.titleLabel.setFont(QFont("Arial", title_text_size)) 

        button_text_size = min(int(self.width() * 0.03), MAX_FONT_SIZE)  
        self.backButton.setFont(QFont("Arial", button_text_size))  
        self.subtitleLabel.setFont(QFont("Arial", button_text_size)) 

        label_text_size = min(int(self.width() * 0.025), MAX_FONT_SIZE)  
        self.tallyLabel.setFont(QFont("Arial", label_text_size)) 
        self.candidateDropDown.setFont(QFont("Arial", label_text_size)) 


        footer_text_size = min(int(self.width() * 0.015), MAX_FONT_SIZE // 2) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
