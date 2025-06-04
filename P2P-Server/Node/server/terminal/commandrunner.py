from __future__ import annotations  # Type checking

# Type checking imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.server import Server

from server.terminal.display import Display
from server.core.constants import MESSAGE_CODES
import server.handlers.blockchain_operations as blockchain_operations
import server.handlers.validator_actions as validator_actions
import server.handlers.lead_validator_actions as lead_validator_actions
import server.handlers.elector_actions as elector_actions

import utilities.elector_loading as elector_loading
import re
import asyncio
import time
import json

class CommandRunner:
    def __init__(self , program_state , server_thread):
        self.program_state = program_state
        self.server_thread = server_thread
        self.CommandMappings = {}
        self.CommandMappings["help"] = self.help
        self.CommandMappings["exit"] = self.exit
        self.CommandMappings["quit"] = self.exit
        self.CommandMappings["connections"] = self.connections
        self.CommandMappings["log"] = self.log
        self.CommandMappings["logs"] = self.log
        self.CommandMappings["message"] = self.message
        self.CommandMappings["dir"] = self.peer_directory
        self.CommandMappings["head"] = self.blockchain_head
        self.CommandMappings["add_transaction"] = self.add_transaction
        self.CommandMappings["finalize"] = self.finalize_block
        self.CommandMappings["show_blocks"] = self.show_blocks
        self.CommandMappings["verify_blockchain"] = self.verify_blockchain
        self.CommandMappings["show_snapshot"] = self.show_snapshot
        self.CommandMappings["ss"] = self.show_snapshot
        self.CommandMappings["sb"] = self.show_blocks
        self.CommandMappings["global_dir"] = self.show_global_nodes
        self.CommandMappings["connect"] = self.connect
        self.CommandMappings["disconnect"] = self.disconnect
        self.CommandMappings["show_validators"] = self.show_validators
        self.CommandMappings["sv"] = self.show_validators
        self.CommandMappings["add_validator"] = self.add_validator
        self.CommandMappings["av"] = self.add_validator
        self.CommandMappings["le"] = self.load_electors
        self.CommandMappings["load_credentials"] = self.load_credentials
        self.CommandMappings["lc"] = self.load_credentials
        self.CommandMappings["sc"] = self.show_candidates
        self.CommandMappings["show_candidates"] = self.show_candidates
        self.CommandMappings["add_candidate"] = self.add_candidate
        self.CommandMappings["vote"] = self.vote
        self.CommandMappings["pause"] = self.pause
        self.CommandMappings["show_votes"] = self.show_votes
        self.CommandMappings["sv"] = self.show_votes
        self.CommandMappings["set_block_proposal_time"] = self.set_block_proposal_time

        self.CommandMessages = {}
        self.CommandMessages["help"] = "Displays all valid commands."
        self.CommandMessages["exit"] = "Exits the program."
        self.CommandMessages["connections"] = "Displays a summary of all current connections"
        self.CommandMessages["show_blocks"] = "Displays a summary of all blocks in the local blockchain"
        self.CommandMessages["head"] = "Displays the head of the local copy of the blockchain."
        self.CommandMessages["dir"] = "Shows the list of discovered nodes."
        self.CommandMessages["show_blocks"] = "Displays all blocks."
        self.CommandMessages["show_snapshot"] = "Show the current blockchain snapshot state."
        self.CommandMessages["global_dir"] = "Shows the global node directory showing IPs, Ports and NodeIds, Only shows on validators."
        self.CommandMessages["connect"] = 'Initiate a connection to a node by IP and Port, Example connect "127.0.0.1" 8000'
        self.CommandMessages["disconnect"] = "Disconnects from all connections"
        self.CommandMessages["show_validators"] = "Shows all known validator nodes."
        self.CommandMessages["load_credentials"] = "Loads local elector credentials if the credentials.json exsists."
        self.CommandMessages["show_candidates"] = "Shows the current candidates recorded on the local blockchain."
        self.CommandMessages["add_candidate"] = 'Adds a candidate, Example add_candidate "Mr Smith" 1.'
        self.CommandMessages["vote"] = "Casts a vote for a given candidate_id, Example: vote 1."
        self.CommandMessages["pause"] = "Pauses the input thread for a given amount of seconds, Example: pause 10."
        self.CommandMessages["show_votes"] = "Shows the current tally of vote as recorded on the local blockchain."
        self.Display = Display(self.program_state)
        self.Display.initial_message()

    def runCommand(self, unparsedtext):
        if len(unparsedtext) > 0:
            command, *arg = str.split(unparsedtext)
            command = str.lower(command)
            if self.CommandMappings.get(command) is None:
                print("[IO] Unknown command. Consider using 'help' to see all commands.")
            else:
                function = self.CommandMappings.get(command)
                if asyncio.iscoroutinefunction(function):
                    asyncio.run_coroutine_threadsafe(
                    function(unparsedtext), self.server_thread.loop
                )
                else:
                    function(unparsedtext)
        else:
            print(".")

    def pause(self , unparsedtext="") -> None:
        match = re.match(r"pause\s+(\d+(?:\.\d+)?)", unparsedtext)
        if match:
            seconds = float(match.group(1))
            self.program_state["hold_time"] = seconds

    def set_block_proposal_time(self , unparsedtext="") -> None:
        server : Server = self.program_state.get("server")
        match = re.match(r'set_block_proposal_time\s+(\d+(?:\.\d+)?)', unparsedtext)
        if match:
            proposal_time = int(match.group(1))
            self.server_thread.loop.call_soon_threadsafe(
            server.set_proposal_time,
            proposal_time
        )

    def show_votes(self , unparsedtext="") -> None:
        self.Display.show_votes()

    async def vote(self , unparsedtext="") -> None:
        server : Server = self.program_state.get("server")
        match = re.match(r'vote (\d+)', unparsedtext)
        if match:
            candidate_id = int(match.group(1))  # Extract number
            await elector_actions.propose_vote(server , candidate_id)
        else:
            print("[IO] Invalid command usage, shoud be vote <candidate_id :: int>")
            print('[IO] Example: vote 1 ')
       

    def verify_blockchain(self , unparsedtext="") -> None:
        server : Server = self.program_state.get("server")

    
    def show_blocks(self , unparsedtext="") -> None:

        server : Server = self.server_thread.server

        self.server_thread.loop.call_soon_threadsafe(
                server.block_chain.pretty_print
        )

    def log(self , unparsedtext=""):
        self.program_state["server"].Logger.display_logs()

    def peer_directory(self , unparsedtext=""):
        self.Display.show_peer_directory()

    def show_snapshot(self , unparsedtext=""):
        self.Display.show_snapshot()

    def show_validators(self , unparsedtext=""):
        self.Display.show_validators()

    async def add_validator(self , unparsedtext="" ) -> None:
        """Usage: add_validator <nodeid>"""
        server = self.program_state.get("server")

        if server is None:
                return

        pattern = r'^add_validator\s+([a-zA-Z0-9]+)$'
        match = re.match(pattern, unparsedtext.strip())
        
        if match:
            node_id = match.group(1)
            asyncio.run_coroutine_threadsafe(
                lead_validator_actions.add_validator(self.server_thread.server,node_id),
                self.server_thread.loop
            )
        else:
            print("[IO] invalid command format.")

       

    def show_global_nodes(self , unparsedtext=""):
        self.Display.show_global_node_table()

    def load_electors(self , unparsedtext=""):
        server : Server = self.program_state.get("server") 
        self.server_thread.loop.call_soon_threadsafe(
            validator_actions.load_all_electors,
            server
        ) 

    def load_credentials(self , unparsedtext=""):
        server = self.program_state.get("server") 
        self.server_thread.loop.call_soon_threadsafe(
            elector_actions.load_credentials_from_file,
            server
        )

    def connections(self , unparsedtext=""):
        self.Display.show_connections()

    def show_candidates(self ,  unparsedtext=""):
        self.Display.show_candidates()

    def add_candidate(self ,  unparsedtext="") -> None:
        server : Server = self.program_state.get("server")
        match = re.match(r'^add_candidate\s+"([^"]+)"\s+(\d+)$', unparsedtext)
        if match:
            candidate_name = match.group(1)  # Extract name inside quotes
            candidate_id = int(match.group(2))  # Extract number
            self.server_thread.loop.call_soon_threadsafe(
                lead_validator_actions.add_candidate,
                server,
                candidate_name,
                candidate_id
            )
        else:
            print("[IO] Invalid command usage, shoud be add_candidate <candidate_name :: string> <candidate_id :: int>")
            print('[IO] Example: add_candidate "Mr Smith" 1 ')


    def blockchain_head(self , unparsedtext=""):
        self.Display.show_blockchain_head(self.program_state)

    def add_transaction(self ,unparsedtext="" ):
        server : Server = self.program_state.get("server")
        pattern = r'^add_transaction\s+"([^"]+)"\s+"([^"]+)"$'
        match = re.match(pattern, unparsedtext)
        if match:
            operation, data = match.groups()
            server.blockchain_operations.add_transaction_to_working(operation , data)
        else:
            print("[IO] Invalid command usage, shoud be add_transaction <action :: string> <data :: string>")

    def finalize_block(self , unparsedtext=""):
        server : Server = self.program_state.get("server")
        server.blockchain_operations.finalize_block()

    async def connect(self , unparsedtext="") -> None:
        pattern = r'^connect\s+"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"\s+(\d+)$'       
        match = re.match(pattern, unparsedtext)
        if match:
            host , port = match.groups()
            host = host.strip('"')
            port = int(port)

            server : Server = self.program_state.get("server")

            if server is None:
                return

            asyncio.run_coroutine_threadsafe(
                server.connection_handler.connect(host , port),
                self.server_thread.loop
            )
        else:
            print("[IO] Invalid command usage, shoud be connect <host :: string> <port :: int>")

    def help(self , unparsedtext=""):
        print("Help".center(36 , "-"))
        print()
        print("Command".ljust(20 , " ") + "Description \n")
        for CommandKey , Message in self.CommandMessages.items():
            print(f"{CommandKey:<20}: {Message}")
        print("-" * 36)

    async def disconnect(self , unparsedtext="") -> None:
        server : Server = self.program_state["server"]
        await server.disconnect_from_all()

    def exit(self , unparsedtext=""):
        print("exit")
        self.program_state["running"] = False
        
      
    async def message(self, unparsedtext):
        #send direct to connection
        pattern = r'^message\s+"([\d\.]+)"\s+(\d+)\s+"(.+)"$'
        match = re.match(pattern, unparsedtext)
        server : Server = self.program_state.get("server")

        if match:
            address = match.group(1)
            port = int(match.group(2))
            text_to_send = match.group(3).strip()

            message_json = {
                "code": MESSAGE_CODES.TEXT.value,
                "data": {
                    "text": text_to_send
                }
            }

            asyncio.run_coroutine_threadsafe(
                server.message_proccessor.send_direct_message(address, port, message_json),
                self.server_thread.loop
            )
        else:
            print('[IO] Invalid command. Usage: send "<address>" <port> "<message>"')
        

 