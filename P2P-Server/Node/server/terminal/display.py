from __future__ import annotations  # Type checking

from datetime import datetime
import time
import sys

# Type checking imports
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from blockchain.blockchain_snapshot import Snapshot
    from server.core.server import Server


class Display():
    def __init__(self , program_state):
        self.progam_state = program_state

    def initial_message(self):
        server = self.progam_state.get("server")
        print("Internet-Voting-Solution".center(36 , "-"))
        print("Running on...")
        print(f"Host : {server.host}")
        print(f"Port : {server.port}")
        print(f"Python Version : {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("-".center(36 , "-"))

    def show_connections(self):
        server = self.progam_state.get("server")
        print("Connections".center(36 , "-"))
        print("live connections:" + str(len(server.connections)) +"\n")
        for each_connection in server.connections:
            line = ""
            line += f"Node_Id : {each_connection.get("node_id" , "unknown")} "
            line += f"Host : {each_connection.get("host" , "unkown")} "
            line += f"Port : {each_connection.get("port" , "unkown")} "
            print(line)
        print("-"*36)
    
    def show_votes(self) -> None:
        server : Server = self.progam_state.get("server")
        print(server.snapshot.get_vote_tally())

    def show_candidates(self) -> None:
        server : Server = self.progam_state.get("server")
        print("Candidates".center(36 , "-"))
        candidates_dict = server.snapshot.get_candidates()
        for each_candidate in candidates_dict.values():
            line = ""
            line += f"Candidate Id : {each_candidate.get("candidate_id" , "unknown")} "
            line += f"Candidate Name : {each_candidate.get("candidate_name" , "unkown")} "
            print(line)

        print("-"*36)

    def show_global_node_table(self) -> None:
        server = self.progam_state.get("server")
        print("Global-Node-Table".center(36 , "-"))
        for entry in server.global_node_table.values():
            line = ""
            line += f"Node_Id : {entry.get("node_id" , "unknown")} "
            line += f"Host : {entry.get("host" , "unkown")} "
            line += f"Port : {entry.get("port" , "unkown")} "
            line += f"Updated : {time.time() - float(entry.get("last_seen" , 0)):.2f} Ago "
            print(line)
        print("-"*36)


    def show_peer_directory(self) -> None:
        server = self.progam_state.get("server")
        print("Peer-Directory".center(36 , "-"))
        for entry in server.peer_directory.values():
            line = ""
            public_key_string : str = entry.get("public_key" , "")
            public_key_string = public_key_string.lstrip("-----BEGIN PUBLIC KEY-----\n")
            public_key_string = public_key_string.rstrip("\n-----END PUBLIC KEY-----")
            public_key_string = public_key_string[:8] + "..."
            line += f"Node_Id : {entry.get("node_id" , "unknown")} "
            line += f"Public Key : {public_key_string} "
            print(line)
        print("-"*36)

    def show_blockchain_head(self , program_state):
        blockchain = program_state.get("blockchain")
        print("Blockchain-Head".center(36 , "-"))
        print(blockchain.head)
        print("-"*36)

        
    def show_blockchain(self , program_state):
        pass

    def show_snapshot(self):
        snapshot = self.progam_state.get("server").snapshot
        print("Snapshot-State".center(36 , "-"))
        print(f"Snapshot Hash : {snapshot.hash}")
        print(f"Blockchain Head : {snapshot.blockchain_head}")
        print(f"Lead validator : {snapshot.lead_validator}")
        print(f"Number of validators : {len(snapshot.validator_addresses)}")
        print("-"*36)

    def show_validators(self) -> None:
        snapshot : Snapshot = self.progam_state.get("server").snapshot
        validators : list = snapshot.get_validators()
        print("Validators-Node-Ids".center(36 , "-"))
        print(f"Number of validators : {len(validators)}")
        for each in validators:
            print(each)
        print("-"*36)

        



