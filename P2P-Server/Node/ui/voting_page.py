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

class VotingPage(QWidget):
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
            lambda: self.main_window.switch_page(self.main_window.connected_page)
        )

        self.submitButton.clicked.connect(
            self.onSubmitPressed
        )

        server_events.sys_new_elector_creds_loaded.connect(
            lambda: self.main_window.switch_page(self)
        )

        self.confirmAcceptButton.clicked.connect(
            self.SubmitVote
        )

    def SubmitVote(self) -> None:
        ui_events : UIEvents = self.main_window.ui_events
        choice_name = self.candidateDropDown.currentText()
        choice_id = self.name_id_mapping.get(choice_name , None) # type: ignore
        if choice_id:
            print("c=",choice_id)
            ui_events.submit_vote.emit(choice_id)
        else:
            QMessageBox.warning(self, "Error", "Could not parse vote choice id.")


    def onSubmitPressed(self):
        if self.checkbox.isChecked() == False:
            QMessageBox.warning(self, "Failed to submit", "Please check the box to submit.")
            return

        if self.candidateDropDown.currentText() is None:
            QMessageBox.warning(self, "Failed to submit", "Please select a candidate.")
            return

        self.confirm_message.exec()

    def create_widgets(self):
        """Create all UI elements dynamically."""
        self.titleLabel = QLabel("Ballot", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.confirm_message = QMessageBox(self)
        self.confirm_message.setWindowTitle("Confirm Vote")
        self.confirm_message.setText(f"Submit Vote For {"Candidate Name"}")
        self.confirmAcceptButton = self.confirm_message.addButton("Confirm", QMessageBox.AcceptRole)
        self.confirmRejectButton = self.confirm_message.addButton("Cancel", QMessageBox.RejectRole)

        self.footerLabel = QLabel("Internet Voting System, Charlie Hall (CH555), University Of Leicester", self)
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.candidateLabel = QLabel("Candidates" , self)
        self.candidateLabel.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("Back" , self)
        self.backButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.candidateDropDown = QComboBox()

        self.checkboxLabel = QLabel("I Understand that my vote is final once submitted and cannot be changed." , self)
        self.checkboxLabel.setWordWrap(True)
        self.checkboxLabel.setAlignment(Qt.AlignCenter)

        self.checkbox = QCheckBox("I Understand" , self)
        self.checkbox.setChecked(False)

        self.submitButton = QPushButton("Submit Button", self)
        self.submitButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)



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

        self.center_layout.addWidget(self.candidateLabel , 1)
        self.center_layout.addWidget(self.candidateDropDown , 1)
        self.center_layout.addWidget(self.checkboxLabel , 1)
        self.center_layout.addWidget(self.checkbox , 1)
        self.center_layout.addWidget(self.submitButton , 1)

        self.center_layout.setAlignment(Qt.AlignCenter)

        self.submitButton.setMaximumHeight(80)
        self.submitButton.setMinimumHeight(50)
        self.submitButton.setMaximumWidth(400)

        self.layout.addWidget(self.header_widget , 1)
        self.layout.addWidget(self.center_widget , 14)
        self.layout.setAlignment(Qt.AlignCenter)  # Full vertical & horizontal centering
        self.layout.addWidget(self.footerLabel , 1)

        self.setLayout(self.layout)

    def update_display(self):
        self.candidateDropDown.clear()
        self.checkbox.setChecked(False)
        self.candidateDropDown.addItems(self.candidates)

    def focused(self , args : typing.Tuple):
        self.name_id_mapping = {} # type: ignore
        self.candidates = []
        server_interface : ServerInterface = self.main_window.server_interface
        for candidate_info in server_interface.candidates:
            name : str = candidate_info[0]
            id_ : int = candidate_info[1]
            self.candidates.append(name)
            self.name_id_mapping[name] = id_ # type: ignore
        self.update_display()    

        

    def apply_styles(self):
        primary_color = "#6A0DAD" 
        secondary_color = "#E6CCFF" 
        tertiary_color = '#A8A8A8' 

    def resizeEvent(self, event):
        """Dynamically adjust font sizes and button sizes on resize."""
        title_text_size = min(int(self.width() * 0.05), MAX_FONT_SIZE) 
        self.titleLabel.setFont(QFont("Arial", title_text_size)) 

        button_text_size = min(int(self.width() * 0.03), MAX_FONT_SIZE)  
        self.submitButton.setFont(QFont("Arial", button_text_size))  
        self.backButton.setFont(QFont("Arial", button_text_size))  

        label_text_size = min(int(self.width() * 0.025), MAX_FONT_SIZE)  
        self.candidateLabel.setFont(QFont("Arial", label_text_size)) 
        self.candidateDropDown.setFont(QFont("Arial", label_text_size)) 
        self.checkbox.setFont(QFont("Arial", label_text_size)) 
        self.confirm_message.setFont(QFont("Arial", label_text_size)) 
        self.checkboxLabel.setFont(QFont("Arial", label_text_size)) 

        footer_text_size = min(int(self.width() * 0.015), MAX_FONT_SIZE // 2) 
        self.footerLabel.setFont(QFont("Arial", footer_text_size))  

        super().resizeEvent(event)
