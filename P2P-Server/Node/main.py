from __future__ import annotations  # Type checking



import sys
import os
import typing

from PyQt5.QtWidgets import QApplication, QMainWindow , QStackedWidget, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal


from ui.index_page import IndexPage  # Import the new IndexPage
from ui.connected_page import ConnectedPage
from ui.join_page import JoinPage
from ui.host_page import HostPage
from server.core.server_events import ServerEvents
from ui.blockchain_page import BlockchainPage
from ui.advanced_options_page import AdvancedOptions
from ui.snaphshot_page import SnapshotPage
from ui.server_interface import ServerInterface
from ui.block_page import BlockPage
from ui.transaction_page import TransactionPage
from ui.ui_events import UIEvents
from ui.load_electors_page import LoadElectorsPage
from ui.add_candidate import AddCandidatePage
from ui.ui_event_handler import UIEventHandler
from ui.voting_info_page import VotingInfoPage
from ui.voting_page import VotingPage
from ui.load_cred_page import LoadCredPage
from ui.load_from_mobile import LoadFromMobilePage
from ui.node_directory_page import NodeDirectoryPage
from ui.add_validator_page import AddValidatorPage
from ui.vote_display_page import VoteDisplayPage
from ui.api_events import APIEvents
from utilities.utilities import get_local_ipv4
from ui.candidates_page import CandidatesPage

from threads.server_thread import ServerThread
from threads.terminal_thread import TerminalThread
from threads.api_thread import APIServerThread
import asyncio
import socket
import argparse


if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents

# Global program state
program_state = {"running": True, "server": None}
args = None

class MainApp(QMainWindow):
    connect_signal : pyqtSignal = pyqtSignal(str , int , int) #target_host , target_port , node_port
    host_signal : pyqtSignal = pyqtSignal(int)
    server_events : ServerEvents
    server_interface : ServerInterface
    ui_event_handler : UIEventHandler
    stack : QStackedWidget

    def __init__(self , app):
        super().__init__()
        self.server_thread = None
        self.stack = QStackedWidget()
        self.server_events = ServerEvents()
        self.mobile_api_port = None
        self.ui_events = UIEvents()
        self.api_events = APIEvents()
        self.ui_event_handler = UIEventHandler(self.ui_events)
        self.server_interface = ServerInterface(self)
        self.local_ip = get_local_ipv4()
        self.app = app

        self.load_cred_page = LoadCredPage(self)
        self.index_page = IndexPage(self)
        self.voting_info_page = VotingInfoPage(self)
        self.connected_page = ConnectedPage(self)
        self.join_page = JoinPage(self)
        self.host_page = HostPage(self)
        self.blockchain_page = BlockchainPage(self)
        self.advanced_options = AdvancedOptions(self)
        self.snapshot_page = SnapshotPage(self)
        self.block_page = BlockPage(self)
        self.transaction_page = TransactionPage(self)
        self.add_elector_page = LoadElectorsPage(self)
        self.add_candidate_page = AddCandidatePage(self)
        self.voting_page = VotingPage(self)
        self.load_from_mobile_page = LoadFromMobilePage(self)
        self.add_validator_page = AddValidatorPage(self)
        self.node_directory_page = NodeDirectoryPage(self)
        self.show_candidates_page = CandidatesPage(self)
        self.vote_dispaly_page = VoteDisplayPage(self)

    
        self.stack.addWidget(self.add_candidate_page)
        self.stack.addWidget(self.connected_page)
        self.stack.addWidget(self.index_page)
        self.stack.addWidget(self.join_page)
        self.stack.addWidget(self.advanced_options)
        self.stack.addWidget(self.host_page)
        self.stack.addWidget(self.blockchain_page)
        self.stack.addWidget(self.snapshot_page)
        self.stack.addWidget(self.block_page)
        self.stack.addWidget(self.transaction_page)
        self.stack.addWidget(self.add_elector_page)
        self.stack.addWidget(self.voting_info_page)
        self.stack.addWidget(self.voting_page)
        self.stack.addWidget(self.load_cred_page)
        self.stack.addWidget(self.load_from_mobile_page)
        self.stack.addWidget(self.add_validator_page)
        self.stack.addWidget(self.node_directory_page)
        self.stack.addWidget(self.show_candidates_page)
        self.stack.addWidget(self.vote_dispaly_page)

        self.setCentralWidget(self.stack)

        self.stack.setCurrentWidget(self.index_page)

        

        self.connect_signal.connect(self.connect_to_server)
        self.host_signal.connect(self.host_server)

        self.connect_events()
        self.initUI()

    def connect_events(self):
        self.server_events.net_server_started.connect(
            lambda: self.switch_page(self.connected_page)
        )

        self.api_events.api_started.connect(
            lambda value: setattr(self , "mobile_api_port" , value)
        )

        self.server_events.sys_port_taken_already.connect(
            lambda port: (QMessageBox.warning(self, "Error", f"Port({port}) is already taken, Please try a diffrent port."), self.startup_failure())
        )

        self.server_events.net_initial_connection_failed.connect(
            lambda: (
                QMessageBox.warning(self, "Error", f"Initial connection failed please check the target address is correct and try again."),
                self.close()
                )
        )

    def switch_page(self, page, *args):
        """Switch to the given page."""
        self.stack.setCurrentWidget(page)
        if hasattr(page , "focused"):
            page.focused(args)

    def initUI(self):
        self.setWindowTitle("Internet Voting System")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(800, 600)
        self.setMaximumSize(1000 , 1000)

    def run(self):
        """Runs the PyQt application."""
        self.show()

    def server_started(self):
        self.api_thread.start()
        self.terminal_thread.start()

    def server_thread_started(self , server_thread):
        """Start TerminalThread only after the server is ready."""
        self.terminal_thread = TerminalThread(server_thread , program_state , app)
        port = 5000
        self.api_thread = APIServerThread(self.api_events , port , 10)
        self.mobile_api_port = self.api_thread.running_port
        self.api_thread.set_server_thread(server_thread)


    def connect_to_server(self , host , port , node_port_value):
        if self.server_thread is None:
            self.server_events.sys_server_ready.connect(self.server_thread_started)
            self.server_events.net_server_started.connect(self.server_started)
            self.server_thread = ServerThread(program_state , self.server_events)
            self.server_thread.set_initial_connection(True)
            self.server_thread.set_initial_connection_target(host , port)
            self.server_thread.set_port(node_port_value)
            self.server_thread.start()
            self.ui_event_handler.set_server_thread(self.server_thread)

  
    def host_server(self , port):
        if self.server_thread is None:
            self.server_events.sys_server_ready.connect(self.server_thread_started)
            self.server_events.net_server_started.connect(self.server_started)
            self.server_thread = ServerThread(program_state , self.server_events)
            self.server_thread.set_bootstrap(1)
            self.server_thread.set_port(port)
            self.server_thread.start()
            self.ui_event_handler.set_server_thread(self.server_thread)


    def terminal_mode_run(self , port , bootstrap , node_id = None):
        if self.server_thread is None:
            self.server_events.sys_server_ready.connect(self.server_thread_started)
            self.server_events.net_server_started.connect(self.server_started)
            self.server_thread = ServerThread(program_state , self.server_events)
            self.server_thread.set_port(port)
            self.server_thread.set_bootstrap(bootstrap)
            self.server_thread.set_node_id(node_id)
            self.server_thread.start()

    def startup_failure(self):
        if self.server_thread:
            self.server_thread.cleanup()
            self.server_thread = None

##main

def parse_args():
    parser = argparse.ArgumentParser(description="Blockchain Node Control Panel")
    parser.add_argument("--terminal-mode" , type=int, default=0 , choices=[0 , 1] , help="Terminal mode launches the App without the graphical interface")
    parser.add_argument("--port", type=int, default=5000, help="Port number for the server (default: 5000)")
    parser.add_argument("--bootstrap", type=int, choices=[0, 1], default=0, help="Set as bootstrap node (1 for True, 0 for False, default: 0)")
    parser.add_argument("--node-id", type=str , default=None, help="Override for nodeid of the launched node.")
    args = parser.parse_args()
    
    return args

if __name__ == "__main__":
   
    args = parse_args()
    app = QApplication(sys.argv)
    main_window = MainApp(app)
    if args.terminal_mode == 0:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        main_window.run()
    else:
        main_window.terminal_mode_run(args.port , bool(args.bootstrap) , args.node_id)
    sys.exit(app.exec_())