from __future__ import annotations  # Type checking

#standard lib
from PyQt5.QtCore import Qt
import os
import asyncio
import json
import random
import typing

import server.handlers.elector_actions as elector_actions
import server.handlers.validator_actions as validator_actions
import server.handlers.lead_validator_actions as lead_validator_actions
import utilities.elector_loading as elector_loading

# Type checking imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.server import Server
    from threads.server_thread import ServerThread

    from ui.ui_events import UIEvents


class UIEventHandler():
    """This class handles events going from ui -> server.
    It catches the signal and the safely queues the action to be executed on the serverThread."""
    ui_events : UIEvents
    server_thread : ServerThread | None
    def __init__(self , ui_events : UIEvents):
        self.ui_events = ui_events
        self.server_thread = None
        self.setup_events()

    def set_server_thread(self , server_thread : ServerThread) -> None:
        self.server_thread = server_thread


    def setup_events(self):
        self.ui_events.add_candidated_pressed.connect(self.add_candidate)
        self.ui_events.load_candidate_credentials_from_file.connect(self.load_elector_creds_from_file)
        self.ui_events.submit_vote.connect(self.submit_vote)
        self.ui_events.load_electors_from_file.connect(self.load_all_electors_from_file)
        self.ui_events.add_validator_pressed.connect(self.add_validator)
    
    def load_all_electors_from_file(self):
        if self.server_thread.server is not None and self.server_thread.loop is not None:
            self.server_thread.loop.call_soon_threadsafe(
                validator_actions.load_all_electors,
                self.server_thread.server
            )
                
    def add_candidate(self , candidate_name : str):
        if self.server_thread.server is not None and self.server_thread.loop is not None:
            self.server_thread.loop.call_soon_threadsafe(
                validator_actions.add_candidate,
                self.server_thread.server, 
                candidate_name
            )
            
    def add_validator(self , node_id : str):
        if self.server_thread.server is not None and self.server_thread.loop is not None:
            asyncio.run_coroutine_threadsafe(
                lead_validator_actions.add_validator(self.server_thread.server,node_id),
                self.server_thread.loop
            )
    
    def load_elector_creds_from_file(self):
        if self.server_thread.server is not None and self.server_thread.loop is not None:
             self.server_thread.loop.call_soon_threadsafe(
                elector_actions.load_credentials_from_file,
                self.server_thread.server
            )

    def submit_vote(self):
        if self.server_thread.server is not None and self.server_thread.loop is not None:
                
            asyncio.run_coroutine_threadsafe(
                elector_actions.propose_vote(self.server_thread.server,1),
                self.server_thread.loop
            )