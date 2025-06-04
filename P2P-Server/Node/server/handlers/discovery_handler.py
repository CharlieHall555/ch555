from __future__ import annotations  # Type checking

# Standard library imports
import asyncio
import json
import random
import time
import traceback
import typing

# Type checking imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.server import Server

# Server imports
import utilities.authentication as authentication
from server.core.constants import MESSAGE_CODES, MIN_CONNECTIONS

def generate_connected_peers(server : Server) -> list:
    connected_peers = []
    for eachConnection in server.connections:

        connected_peers.append({
            "host" : eachConnection.get("host"),
            "port" : eachConnection.get("port"),
            "node_id": eachConnection.get("node_id" or 0)
        })

    return connected_peers
            
def generate_global_nodes(server : Server) -> list:
    """"""
    output = []
    for eachEntry in server.global_node_table.values():

        output.append({
            "host" : eachEntry.get("host"),
            "port" : eachEntry.get("port"),
            "node_id": eachEntry.get("node_id" or 0),
            "last_seen" : eachEntry.get("last_seen"),
        })

    return output

def generate_discovered_nodes(server : Server) -> list:
    """Generates a list of discovered peers, for each peer generates a dict with node_id and public_key"""
    list_discovered_peers = []
    for each_peer in server.peer_directory.values():
        # default to a tuple of 0 connections known at timestamp 0 if nothing is known about given peer
        list_discovered_peers.append({
            "node_id" : each_peer.get("node_id"),
            "public_key" : each_peer.get("public_key")
        })

    list_discovered_peers.append({
        "node_id" : server.node_id,
        "public_key" : authentication.serialize_public_key(server.node_public_key)
    })

    #watch this return
    return list_discovered_peers  

class DiscoveryHandler:
    server : Server
    def __init__(self , server : Server):
        self.server = server

    async def discovery_gossip_loop(self : DiscoveryHandler) -> None:
        server = self.server
        while True:
            try:

                #connection discovery message.
                connections_discovery_message = {
                    "code": MESSAGE_CODES.CONNECTION_DISCOVERY.value,
                    "message_timestamp" : time.time(),
                    "data": {
                        "connections_list" : generate_connected_peers(self.server)
                    }
                }

                await server.message_proccessor.direct_broadcast(connections_discovery_message)

                update_validators_message = {
                    "code": MESSAGE_CODES.HEARTBEAT.value,
                    "message_timestamp" : time.time(),
                    "data" : {
                        "port" : server.port,
                        "host" : server.host
                    }
                }

                await server.message_proccessor.ttl_broadcast(update_validators_message)

            except Exception as e:
                server.logger.Log("Discovery protocol error", "error")
                traceback.print_exc()
            finally:
                await asyncio.sleep(3)


    def handle_received_connections_list(self : DiscoveryHandler , received_connections : list):
        server = self.server
        unconnected = []
        for eachConnection in received_connections:
            host = eachConnection.get("host")
            port_str = eachConnection.get("port")
            port = int(port_str)
            addr = (host , port)
            if server.is_connected(addr) == False:
                unconnected.append(eachConnection)

        if len(unconnected) > 0: #if there a connections that are unconnected
            if len(server.connections) < MIN_CONNECTIONS:
                choice = random.choice(unconnected)
                choice_port , choice_host = choice.get("port"), choice.get("host")
                if not(self.server.port == choice_port and self.server.host == choice_host): #can't connect to self.
                    asyncio.create_task(
                        self.server.connect_to_node(choice_host , choice_port)
                    )

    def handle_received_connections_list_as_validator(self : DiscoveryHandler , received_connections : list)->None:
        server : Server = self.server

        for eachConnection in received_connections:
            host = eachConnection.get("host")
            port_str = eachConnection.get("port")
            port = int(port_str)
            addr = (host , port)
            node_id = eachConnection.get("node_id")
                
    
    def handle_received_nodes_list(self : DiscoveryHandler , received_nodes : list) -> None:
       
        server = self.server
        for eachNode in received_nodes:
            if server.peer_directory.get(eachNode.get("node_id")) is None:
                server.peer_directory[eachNode.get("node_id")] = {
                    "node_id" : eachNode.get("node_id"),
                    "public_key" : eachNode.get("public_key")
                }
        if len(received_nodes) > 0:
            self.server.server_events.net_node_directory_changed.emit(self.server.peer_directory.copy())

    def handle_global_discovery_message(self , json_message: dict[str , typing.Any]) -> None:
        """This message is only sent out by validators to validators to store the global node directory states"""
        try:

            server : Server = self.server
            sender = str(json_message.get("sender"))
            message_data : typing.Optional[dict] = json_message.get("data")
            if message_data is None:
                return
            node_list : typing.Optional[list] = message_data.get("global_nodes")
            if node_list is None:
                return
            
            each_received_node : typing.Dict[str , (str | int)]
            for each_received_node in node_list:
                node_id = each_received_node.get("node_id")
                exsisting_entry : typing.Optional[dict] = server.global_node_table.get(node_id , None)
                if exsisting_entry is None:
                    server.global_node_table[node_id] = each_received_node
                    continue

                exsisting_timestamp = exsisting_entry.get("timestamp" , 0)
                new_timestamp = exsisting_entry.get("timestamp" , 0)

                if new_timestamp > exsisting_timestamp:
                    server.global_node_table[node_id] = each_received_node

            
        except Exception as e:
            server.logger.Log("Exception handling global_discovery_message", "error")
            traceback.print_exc()
          

    def handle_node_discovery_message(self : DiscoveryHandler , json_message: dict[str , typing.Any]):
        server = self.server
        sender = str(json_message.get("sender"))
        message_data : typing.Optional[dict] = json_message.get("data")
        if message_data is None:
            return
        node_list : typing.Optional[list] = message_data.get("discovered_peers")
        if node_list is None:
            return
        self.handle_received_nodes_list(node_list)


    def handle_connection_discovery_message(self : DiscoveryHandler , json_message: dict):
        server = self.server
        sender = str(json_message.get("sender"))
        message_data : typing.Optional[dict] = json_message.get("data")

        if message_data is None:
            return

        connections_list : typing.Optional[list] = message_data.get("connections_list")

        if connections_list is None:
            return 

        self.handle_received_connections_list(connections_list)

