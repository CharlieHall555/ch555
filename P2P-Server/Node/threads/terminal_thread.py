import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from ui.index_page import IndexPage
from threads.server_thread import ServerThread
from server.terminal.commandrunner import CommandRunner

class TerminalThread(QThread):
    """Handles terminal input in a separate thread to avoid blocking the GUI."""

    def __init__(self , server_thread , program_state : dict , app):
        super().__init__()
        self.program_state = program_state
        self.server_thread = server_thread
        self.app = app

    def run(self):
        commandRunner = CommandRunner(self.program_state , self.server_thread)
        while self.program_state.get("running"):
            try:
                hold_time = self.program_state.get("hold_time" , 0)
                if hold_time >= 0: 
                    self.program_state["hold_time"] = 0
                    time.sleep(hold_time) #blocks thread

                text = input("Enter command: ").strip()
                if text:
                    commandRunner.runCommand(text)
            except EOFError:
                break  # Handle unexpected exit (e.g., user closes terminal)
        
        if self.program_state.get("running") == False:
            self.app.quit()