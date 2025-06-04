from __future__ import annotations  # Type checking

from PyQt5.QtWidgets import QApplication, QMainWindow , QStackedWidget, QMessageBox

import typing
from typing import List , Tuple

from threads.api_thread import Credentials

if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents
    from blockchain.blockchain_snapshot import Snapshot

class ServerInterface():
    connections : List
    n_connections : int
    validator_list : typing.List
    blockchain_head : str | None
    blockchain : dict
    node_directory : dict
    vote_tally : dict
    candidates : typing.List[typing.Tuple[str , int]]
    """This class will be used to store the state of a the server for easy lookup in UI classes"""
    def __init__(self , main_window):
        self.connections = []
        self.n_connections = 0
        self.blockchain_head = None
        self.main_window = main_window
        self.node_id = None

        self.node_directory = {}
        self.candidates = []
        self.blockchain = None
        self.lead_validator = None
        self.validator_list = []
        self.block_table = {}
        self.vote_tally = {}
        self.server_credentials = None

        self.confirm_message = QMessageBox(self.main_window.stack.currentWidget())
        self.confirm_message.setWindowTitle("Vote")
        self.confirm_message.setText("Vote has been submitted to blockchain!")
        self.confirmAcceptButton = self.confirm_message.addButton("Goto", QMessageBox.AcceptRole)
        self.confirmRejectButton = self.confirm_message.addButton("Close", QMessageBox.RejectRole)

        self.setup_events()

    def lookup_block(self , block_hash) -> dict | None:
        return self.block_table.get(block_hash , None)
    
    def vote_detected_alert(self):
        self.confirm_message.exec()

    def connection_changed(self , connections_list : List):
        self.n_connections = len(connections_list)
        self.connections = connections_list

    def new_snapshot_loaded(self , new_snapshot : Snapshot):
        self.validator_list = new_snapshot.validator_addresses
    
        self.candidates = []
        for each_candidate in new_snapshot.get_candidates().values():
            candidate_name = each_candidate.get("candidate_name")
            id = each_candidate.get("candidate_id")
            self.candidates.append((candidate_name , id))

        self.vote_tally = new_snapshot.vote_tally
        self.blockchain_head = new_snapshot.blockchain_head
        self.lead_validator = new_snapshot.lead_validator

    def new_vote_added(self , new_vote_tally : dict):
        print(new_vote_tally)
        self.vote_tally = new_vote_tally

    def setup_events(self) -> None:
        server_events : ServerEvents = self.main_window.server_events

        server_events.blc_own_vote_detected.connect(self.vote_detected_alert)

        server_events.sys_new_elector_creds_loaded.connect(
            lambda public_key , priv_key : (self.__setattr__("server_credentials" , (public_key , priv_key) ) )
        )

        server_events.blc_candidate_added.connect(
            lambda new_candidate_name , id : self.candidates.append((new_candidate_name , id))
        )

        server_events.blc_blockchain_updated.connect(
            lambda new_blockchain : self.__setattr__("blockchain" , new_blockchain)
        )

        server_events.sys_new_node_id.connect(
            lambda new_node_id : self.__setattr__("node_id" , new_node_id)
        )

        server_events.blc_snapshot_head_updated.connect(
            lambda new_head : self.__setattr__("blockchain_head" , new_head)
        )

        server_events.blc_validator_added.connect(
            lambda node_id : self.validator_list.append(node_id)
        )

        server_events.blc_lead_validator_set.connect(
            lambda node_id : self.__setattr__("lead_validator" , node_id)
        )

        server_events.blc_block_added.connect(
            lambda new_serialized_block: (self.block_table.__setitem__(new_serialized_block.get("hash" , 0) , new_serialized_block))
        )

        server_events.net_node_directory_changed.connect(
            lambda new_directory: self.__setattr__("node_directory" , new_directory)
        )

        server_events.net_connections_changed.connect(self.connection_changed)

        server_events.blc_new_blockchain_loaded.connect(
            lambda: self.__setattr__("block_table" , {})
        )

        server_events.blc_new_snapshot_loaded.connect(
            self.new_snapshot_loaded
        )

        server_events.blc_new_vote_added.connect(
            self.new_vote_added
        )
   