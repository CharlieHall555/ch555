"""
This module contains the server class which abstracts the I/O for the peer-to-peer network.

Server is the main class and is composed of most other classes in the implementation.
Server conatins the methods to connect and message with other nodes. Server keeps track
of all other nodes that are discovered and connected to.
"""
from __future__ import annotations  # Type checking


# Standard library imports
import asyncio
import hashlib
import json
import math
import os
import random
import time
import typing
import traceback  # Debug only

# Local imports
from blockchain.block import Block
from blockchain.transaction import Transaction
from blockchain.blockchain import Blockchain
from blockchain.blockchain_snapshot import Snapshot
from testing.intergration.logevents import LOG_EVENTS

from server.core.logger import Logger
from server.handlers.connection_handler import ConnectionHandler
from server.messaging.message_actions import handle_message
from server.messaging.message_proccessor import MessageProccessor
from server.handlers.discovery_handler import DiscoveryHandler, generate_discovered_nodes , generate_connected_peers, generate_global_nodes
from server.handlers.new_block_processor import NewBlockProcessor
from server.handlers.blockchain_operations import BlockchainOperations
from ui.ui_event_handler import UIEventHandler

from utilities.enum_encoder import EnumEncoder

# Server constants
import server.core.constants as CONSTANTS
from server.core.constants import MESSAGE_CODES

# Server modules
import utilities.authentication as authentication
import server.handlers.validator_actions as validator_actions
import server.handlers.lead_validator_actions as lead_validator_actions

if typing.TYPE_CHECKING:
    from server.core.server_events import ServerEvents
    from ui.ui_events import UIEvents
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


# End of imports

class Server:
    host : str
    port : int
    server : asyncio.base_events.Server | None
    message_buffer : str
    processed_messages : set
    logger : Logger
    block_chain : Blockchain
    snapshot : Snapshot
    peer_connection_numbers : list
    connections : list
    peer_directory : dict
    validator : bool
    lead_validator : bool
    temp_connections : dict
    working_block : Block
    node_id : str
    global_node_table : dict
    validator_addresses : set # a set of tuple addresses like (host , port) only tracked by other validators.
    server_events : ServerEvents
    ui_events : UIEvents
    message_proccessor : MessageProccessor
    discovery_handler : DiscoveryHandler
    new_block_proccessor : NewBlockProcessor
    connection_handler : ConnectionHandler
    blockchain_operations : BlockchainOperations

    node_private_key : authentication.RSAPublicKey
    node_public_key : authentication.RSAPrivateKey

    elector_public_key : Ed25519PublicKey | None
    elector_private_key : Ed25519PrivateKey | None

    def __init__(self , host , port , program_state , server_events : ServerEvents , node_id:typing.Optional[str] = None):
        self.host = host
        self.port = port
        self.server = None
        self.message_buffer = ""
        self.processed_messages = set()
        self.server_events = server_events

        # Composite Classes.
        self.message_proccessor = MessageProccessor(self)
        self.discovery_handler = DiscoveryHandler(self)
        self.new_block_proccessor = NewBlockProcessor(self)
        self.connection_handler = ConnectionHandler(self)
        self.blockchain_operations = BlockchainOperations(self)

        self.logger = Logger(f"{host}_{port}_log.txt" , False)

        self.block_chain = program_state.get("blockchain")
        self.snapshot = Snapshot()
        self.validator_addresses = set()

        self.peer_connection_numbers = []
        self.connections = [] #Only neighbors
        self.connection_status = {}
        self.peer_directory = {}

        self.initial_connection_target = None

        self.known_bootstraps = {}
        self.global_node_table = {}

        self.validator = False
        self.lead_validator = False

        self.temp_connections = {}

        self.node_type = "Node"
        self.node_private_key , self.node_public_key = authentication.generate_rsa_key_pair()
        self.node_id = node_id or authentication.generate_node_id(self.node_public_key)
        self.server_events.sys_new_node_id.emit(self.node_id)

        self.elector_public_key = None
        self.elector_private_key = None

        self.peer_directory[self.node_id] = {
            "node_id": self.node_id,
            "public_key": authentication.serialize_public_key(self.node_public_key)
        }

        self.server_events.net_node_directory_changed.emit(self.peer_directory.copy())


        self.server_events.net_node_directory_changed.emit(self.peer_directory.copy())

        self.global_node_table[self.node_id] = {
            "host": self.host,
            "port": self.port,
            "node_id": self.node_id,
            "last_seen": time.time(),
        }

    async def initial_setup(self : "Server" , bootstrap: bool = False , initial_connect: bool = False , initial_connection_host: str = None, initial_connection_port : int = None):

        # blockchain setup
        genesisBlock = Block()
        genesisBlock.set_previous_hash(0)
        self.block_chain.add_genesis_block(genesisBlock)
        self.block_chain.head = genesisBlock.hash
        self.working_block = Block(genesisBlock.hash)
        self.snapshot.blockchain_head = self.block_chain.head
        # setup if the node is a bootstrap node
        if bootstrap:
            validatorBlock = Block(self.block_chain.head)

            validatorTransaction = Transaction("ADD_VALIDATOR" , {
                "node_id" : self.node_id
            })

            testTransaction = Transaction("TEST" , "TEST")

            leadValidatorTransaction = Transaction("SET_LEAD_VALIDATOR" , {
                "node_id" : self.node_id
            })

            await validator_actions.self_became_validator(self , bootstrap=True)#bootstrap node always starts as a validator
            await lead_validator_actions.self_became_lead_validator(self)
            validatorBlock.add_transaction(validatorTransaction)
            validatorBlock.add_transaction(leadValidatorTransaction)
            self.working_block = validatorBlock
            self.blockchain_operations.finalize_block()

        # setup node to connect to initial connection location
        if initial_connect == True and (initial_connection_host is None or initial_connection_port is None) == False:
            self.initial_connection_target = {
                "host" : initial_connection_host,
                "port" : initial_connection_port
            }

    async def handle_connection(self, reader, writer , acceptor=True):
        addr = writer.get_extra_info('peername')
        self.host = addr[0]

        try:
            # if theyre not an acceptor but a sender the initial ip and port getting is handled in connect_to_peer

            # if connecting to network send the message to get list of validators
            while True:

                data = await reader.read(1024)
                if not data:
                    break
                self.message_buffer += data.decode()

                while "#" in self.message_buffer : # wait for a full message, wait for the "#" end char.
                    full_message , self.message_buffer = self.message_buffer.split("#", 1)
                    try:
                        full_message = str.strip(full_message, "#")
                        parsed_message = json.loads(full_message)
                        self.logger.Log(f"{LOG_EVENTS.MESSAGE_RECIEVED.value} ({addr})" , "info")
                        await handle_message(self , parsed_message , writer , acceptor)
                    except json.JSONDecodeError as e:
                        traceback.print_exc()
                        self.logger.Log(f"Error Decoding Message: {full_message}" , "error" , False)
                        return

        except OSError as e:
            self.logger.Log(f"Error with connection {addr} : {e}, (OS Error)" , "error")
        except Exception as e:
            self.logger.Log(f"Error with connection {addr}: {e}" , "error")
            traceback.print_exc()
            return
        finally:
            try:
                writer.close()
                await writer.wait_closed()  # Wait for the connection to close
            except ConnectionResetError as e:
                self.logger.Log(f"Connection reset during wait_closed for {addr}: {e}", "warn")
            except Exception as e:
                self.logger.Log(f"Unexpected error during writer cleanup for {addr}: {e}", "error")
            finally:
                # Safely remove the connection without modifying list during iteration
                self.connections = [conn for conn in self.connections if conn.get("writer") != writer]
                self.logger.Log(f"Connection with {addr} closed.", "info")

    def is_connected(self , addr):
        local_addr = self.server.sockets[0].getsockname()  
        if local_addr == addr:
            return True
        for eachConnection in self.connections:
            if (eachConnection.get('host') , eachConnection.get('port')) == addr:
                return True
        return False

    def set_proposal_time(self , new_value):
        CONSTANTS.BLOCK_PERIOD = new_value

    async def temp_connections_loop(self):
        # loop through temp connections if they have been open too long close
        prev_time = asyncio.get_event_loop().time()
        while True:
            await asyncio.sleep(0.1)
            current_time = asyncio.get_event_loop().time()
            delta_time = current_time - prev_time
            prev_time = current_time

            for addr , connection in self.temp_connections.copy().items():
                connection["time_idle"] = (connection.get("time_idle") or 0) + delta_time

                if connection.get("time_idle") > 5:
                    self.logger.Log(f"Connection closing with {addr[0] , addr[1]}, timeout" , "warn")
                    await self.close_temp_connection(connection.get("host") , connection.get("port"))

    async def after_disconnect(self):
        pass

    async def close_temp_connection(self , address , port):
        for addr , each_connection in self.temp_connections.items():
            if each_connection.get("host") == address and each_connection.get("port") == port:
                writer = each_connection.get("writer")
                try:
                    writer.close()
                    await writer.wait_closed()  # Ensure connection is fully closed
                    self.logger.Log(f"Closed temp connection with {address}:{port}", "info")
                except Exception as e:
                    self.logger.Log(f"Error closing temp connection with {address}:{port}: {e}", "error")
                finally:
                    self.temp_connections.pop((address, port), None)
                return

        self.logger.Log(f"No active connection found to close for {address}:{port}", "warn")

    async def set_up_temp_connection(self , peer_host , peer_port):
        # this should be used to connect to known nodes only and for short amounts of time or for private data.
        try:
            if self.is_connected((peer_host, peer_port)):
                self.logger.Log(f"Already connected to peer {peer_host}:{peer_port}", "info")
                return
            assert (peer_host != self.host) or (peer_port != self.port)
            reader, writer = await asyncio.open_connection(peer_host, peer_port)

            asyncio.create_task(self.handle_connection(reader, writer , False))
            self.temp_connections[(peer_host, peer_port)] = {
                "time_idle": 0,
                "writer": writer,
                "port" : peer_port,
                "host" : peer_host
            }
        except ConnectionRefusedError as e:
            self.logger.Log(f"Failed to connect to peer {peer_host}:{peer_port}: refused connection" , "error")
        except Exception as e:
            self.logger.Log(f"Failed to connect to peer {peer_host}:{peer_port}: {e}" , "error")
            traceback.print_exc()

    async def start_server(self):
        self.server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        addr = self.server.sockets[0].getsockname()

        asyncio.create_task(self.discovery_handler.discovery_gossip_loop())
        asyncio.create_task(self.temp_connections_loop())

        if self.initial_connection_target is not None:
            
            asyncio.create_task(
                self.initial_connection_try()
            )

        self.logger.Log(f"{LOG_EVENTS.SERVER_STARTED.value} ({self.host},{self.port})")
        self.server_events.net_server_started.emit()
        async with self.server:
            await self.server.serve_forever()

    async def initial_connection_try(self):
        await self.connection_handler.connect(
            self.initial_connection_target.get("host"),
            self.initial_connection_target.get("port"),
        )

    async def close_connection(self, host: str, port: str) -> None:
        for each_connection in self.connections.copy():
            if each_connection.get("host") == host and each_connection.get("port") == port:
                writer = each_connection.get("writer")

                if writer:  # Ensure writer exists before closing
                    try:
                        writer.close()
                        await writer.wait_closed()  # Ensure connection is fully closed
                        self.logger.Log(f"Closed connection with {host}:{port}", "info")
                    except Exception as e:
                        self.logger.Log(f"Error closing connection with {host}:{port}: {e}", "error")

                # Remove from connections safely
                self.connections = [conn for conn in self.connections if conn != each_connection]

                # Remove from connection status
                self.connection_status.pop((host, port), None)

        self.logger.Log(f"No active connection found to close for {host}:{port}", "warn")

    async def disconnect_from_all(self):
        """Disconnects the node from all connected peers."""
        connections_copy = self.connections.copy()  # Create a copy to avoid modification issues

        for each_connection in connections_copy:
            host, port = each_connection.get("host"), each_connection.get("port")
            writer = each_connection.get("writer")

            if writer:
                try:
                    writer.close()
                    await writer.wait_closed() 
                    self.logger.Log(f"Closed connection with {host}:{port}", "info")
                except Exception as e:
                    self.logger.Log(f"Error closing connection with {host}:{port}: {e}", "error")

            self.connections = [conn for conn in self.connections if conn != each_connection]
            self.connection_status.pop((host, port), None)

        # Clear temporary connections
        temp_connections_copy = list(self.temp_connections.keys())  # Avoid runtime modification issues
        for addr in temp_connections_copy:
            each_connection = self.temp_connections.get(addr)
            if each_connection:
                writer = each_connection.get("writer")
                if writer:
                    try:
                        writer.close()
                        await writer.wait_closed()
                        self.logger.Log(f"Closed temp connection with {addr[0]}:{addr[1]}", "info")
                    except Exception as e:
                        self.logger.Log(f"Error closing temp connection with {addr[0]}:{addr[1]}: {e}", "error")
                self.temp_connections.pop(addr, None)

        self.logger.Log("Disconnected from all peers.", "info")

    async def connect_to_node(self, peer_host : str , peer_port : int, is_initial: bool = False):
        """Handles the sender-side logic for connecting to a validator or a regular peer."""
        try:
            peer_host = str(peer_host)
            peer_port = int(peer_port)

            if self.is_connected((peer_host, peer_port)):
                self.logger.Log(f"Already connected to peer {peer_host}:{peer_port}", "info")
                return

            assert (peer_host != self.host) or (peer_port != self.port)
            reader, writer = await asyncio.open_connection(peer_host, peer_port)

            asyncio.create_task(self.handle_connection(reader, writer, False))

            # Construct message data
            message_data = {
                "node_id": self.node_id,
                "host": self.host,
                "port": self.port
            }

            formatted_message_data : dict | str

            if is_initial:
                message_data["public_key"] = authentication.serialize_public_key(self.node_public_key)
                message_data_str = json.dumps(message_data , sort_keys=True , cls=EnumEncoder)
                formatted_message_data = authentication.encrypt_with_public_key_rsa(
                    CONSTANTS.HANSHAKE_PUBLIC_KEY, message_data_str
                )
            else:
                formatted_message_data = message_data

            # Construct join request message
            initial_join_message = {
                "code": MESSAGE_CODES.BOOTSTRAP_JOIN_REQUEST.value if is_initial 
                else MESSAGE_CODES.JOIN_REQUEST.value,
                "message_type": "direct",
                "sender": self.node_id,
                "data": formatted_message_data,
                "timestamp": time.time(),
                "nonce": os.urandom(16).hex(),
            }

            # Generate message ID
            data_to_hash = str(initial_join_message["timestamp"]) + str(initial_join_message["sender"]) + str(initial_join_message["nonce"])
            initial_join_message["id"] = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()

            # Sign the message if it's not a validator connection
            if is_initial == False:
                data_to_sign = json.dumps(initial_join_message , sort_keys=True , cls=EnumEncoder)
                signature = authentication.generate_signature_str_rsa(self.node_private_key, data_to_sign)
                initial_join_message["signature"] = signature

            # Send the message
            initial_join_message_str = json.dumps(initial_join_message , sort_keys=True , cls=EnumEncoder) + "#"
            writer.write(initial_join_message_str.encode())
            await writer.drain()

            self.logger.Log(f"Initial listener message sent to {writer.get_extra_info('peername')}", "info")

            # Store connection

        except AssertionError:
            self.logger.Log("Cannot connect to self", "error")
        except Exception as e:
            if is_initial:
                self.server_events.net_initial_connection_failed.emit()
            self.logger.Log(f"Failed to connect to peer {peer_host}:{peer_port}: {e}", "error")
            traceback.print_exc()

    async def handle_join_request(self, message, writer, acceptor, is_initial: bool = False) -> None:
        """Handles both initial and regular join requests when setting up a new connection."""
        addr = writer.get_extra_info("peername")

        if acceptor:
            message_data : typing.Optional[dict]
            # Decrypt message if it's an initial join request
            if is_initial:
                decrypted_data = authentication.decrypt_with_private_key_rsa(
                    CONSTANTS.HANSHAKE_PRIVATE_KEY, message.get("data")
                )
                message_data = json.loads(decrypted_data)
            else:
                message_data = message.get("data")

            if message_data is None:
                self.logger.Log("Missing data", "error")
                return

            # Extract node details
            public_key = message_data.get("public_key")
            peer_host = writer.get_extra_info("peername")[0] #gets ip
            peer_port, node_id = message_data["port"], message_data["node_id"]

            self.logger.Log(
                f"Listener message received from {peer_host}:{peer_port}", "info"
            )

            # Store node information if not already in directory
            if is_initial and self.peer_directory.get(node_id) is None:
                self.peer_directory[node_id] = {
                    "node_id": node_id,
                    "public_key": public_key
                }
                self.server_events.net_node_directory_changed.emit(self.peer_directory.copy())


            # If the acceptor is a validator, update the global node table and send an update to all nodes with update peer directory
            if self.validator:
                self.global_node_table[node_id] = {
                    "host": peer_host,
                    "port": peer_port,
                    "node_id": node_id,
                    "last_seen" : time.time()
                }

                asyncio.create_task(validator_actions.send_node_discovery_message(self))  

            # Reject if too many connections
            if len(self.connections) >= CONSTANTS.MAX_CONNECTIONS:
                error_response = {
                    "code": 
                        MESSAGE_CODES.BOOTSTRAP_JOIN_REQUEST_REJECTED.value if is_initial 
                        else MESSAGE_CODES.BOOTSTRAP_JOIN_REQUEST_REJECTED.value,
                    "sender": self.node_id,
                    "data": {"message": "too many active connections"},
                }

                choice_addresses = []

                for i in range(0 , 3):
                    choice_connection = None
                    if self.validator:
                        choice_connection = random.choice(list(self.global_node_table.values()))
                    else:
                        choice_connection = random.choice(self.connections)

                    choice_host = choice_connection.get("host")
                    choice_port = choice_connection.get("port")
                    choice_addresses.append({
                        "host" : choice_host,
                        "port" : choice_port
                    })

                error_response["data"]["suggested"] = choice_addresses
                error_response_str = json.dumps(error_response) + "#"

                writer.write(error_response_str.encode())
                await writer.drain()
                self.logger.Log(
                    f"Connection refused: Max connections reached for {addr}", "warn"
                )
                if writer:
                    try:
                        writer.close()
                        await writer.wait_closed() 
                        self.logger.Log(f"connection closed", "error")
                    except Exception as e:
                        self.logger.Log(f"Error closing connection: {e}", "error")

                return
            else:

                # Add new connection if not already connected
                if not self.is_connected((peer_host, peer_port)):
                    self.connections.append(
                    {"host": peer_host, "port": peer_port, "writer": writer, "node_id": node_id}
                    )
                    self.server_events.net_connections_changed.emit(self.connections.copy())
                

                # Send request accepted response with network state
                response = {
                    "code": 
                        MESSAGE_CODES.BOOTSTRAP_JOIN_REQUEST_ACCEPTED.value if is_initial 
                        else MESSAGE_CODES.JOIN_REQUEST_ACCEPTED.value,
                    "sender": self.node_id,
                    "data": {
                        "discovered_nodes": generate_discovered_nodes(self),
                        "connected_peers": generate_connected_peers(self),
                        "global_peers" : generate_global_nodes(self) if self.validator else None,
                        "public_key": authentication.serialize_public_key(self.node_public_key),
                        "host": self.host,
                        "port": str(self.port),
                    },
                }

                await self.message_proccessor.send_direct_message(peer_host, peer_port, response)     

    async def handle_join_request_accepted(self ,  message : dict ,  writer : asyncio.StreamWriter , is_initial=False):
        data : typing.Optional[dict] = message.get("data")
        if data is None:
            self.logger.Log("error handling join request, message data is missing" , "error")
            return

        sender_id = message.get("sender")
        peer_host = writer.get_extra_info("peername")[0] #gets ip
        peer_port_str = data.get("port" , 0)
        peer_port = int(peer_port_str) 

        self.connections.append({"host": peer_host, "port": peer_port, "writer": writer, "node_id": sender_id})
        self.server_events.net_connections_changed.emit(self.connections.copy())
        self.connection_status[(peer_host, peer_port)] = "open"

        public_key = data.get("public_key")
        received_nodes : typing.Optional[list] = data.get("discovered_nodes")
        received_connections : typing.Optional[list] = data.get("connected_peers")

        if received_connections is None or received_nodes is None:
            self.logger.Log("error handling join request, missing connections or nodes." , "error")
            return

        for eachConnection in self.connections: # this is messy maybe should use a dict to store connections
            if eachConnection.get("host") == peer_host and eachConnection.get("port") == peer_port:
                eachConnection["node_id"] = sender_id # <- not really needed

        if self.peer_directory.get(sender_id) is None:
            self.peer_directory[sender_id] = {
                "node_id" : sender_id,
                "public_key" : public_key
            }

            self.server_events.net_node_directory_changed.emit(self.peer_directory.copy())


        discovered_nodes = data.get("discovered_nodes")
        self.discovery_handler.handle_received_nodes_list(discovered_nodes)

        global_peers_list = data.get("global_peers")

        if len(received_connections) > 0:
            self.discovery_handler.handle_received_connections_list(received_connections)

        if is_initial:
            self.server_events.net_connected_successfully_to_network.emit()

        # Request basic snapshot message
        message = {"code": MESSAGE_CODES.REQUEST_BASIC_SNAPSHOT.value, "data": ""}

        await self.message_proccessor.send_direct_message(peer_host, peer_port, message)
