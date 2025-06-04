from __future__ import annotations  # Type checking

import typing

if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents

from PyQt5.QtCore import QThread, pyqtSignal
import asyncio
from server.core.server import Server
from blockchain.blockchain import Blockchain
from blockchain.block import Block

class ServerThread(QThread):
    server_ready_signal : pyqtSignal = pyqtSignal(object)
    server_events : ServerEvents

    def __init__(self, program_state , server_events):
        super().__init__()
        self.program_state = program_state
        self.server_events = server_events

        self.loop = None  # Asyncio event loop
        self.server = None

        self.port = None
        self.bootstrap = False
        self.node_id = None
        self.initial_connection = False
        self.target_host = None
        self.target_port = None

    def set_port(self , port):
        self.port = port

    def set_node_id(self , node_id : str):
        self.node_id = node_id
        
    def set_bootstrap(self , bootstrap):
        self.bootstrap = bootstrap

    def set_initial_connection(self , value):
        self.initial_connection = value

    def set_initial_connection_target(self , host , port):
        self.target_host = host
        self.target_port = port

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server())

    def cleanup(self):
        if self.server and self.server.server:
            self.loop.run_until_complete(self.server.server.wait_closed())
        self.loop.close()

    async def start_server(self):
        # initialization
        new_blockchain = Blockchain()
        self.program_state["blockchain"] = new_blockchain

        self.server = Server(
            "0.0.0.0", self.port, self.program_state, self.server_events , self.node_id
        )
        self.program_state["server"] = self.server
        self.server.block_chain = new_blockchain
        await self.server.initial_setup(
            self.bootstrap, self.initial_connection, self.target_host, self.target_port
        )
        self.server_events.sys_server_ready.emit(self)

        try:
            await self.server.start_server()  # Start asyncio server
        except OSError as e:
            if e.errno == 10048:
                print(f"[ERROR] Port {self.port} already in use.")
                self.server_events.sys_port_taken_already.emit(str(self.port))
            else:
                self.server_events.sys_launch_failure.emit()


