"""This class handles the message proccessing logic for the server class"""
from __future__ import annotations  # Type checking

#Standard Library
import os
import json
import hashlib
import time
import traceback

#local Imports
import utilities.authentication as authentication
import server.core.constants as CONSTANTS
from utilities.enum_encoder import EnumEncoder
import math

# Type checking imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.server import Server


class MessageProccessor: 
    server : Server
    def __init__(self , server : Server):
        self.server = server

    # put ttl value in here becuase it should be added post signing, just makes it easier.
    def process_message(self , pre_json_message , ttl_value=0):
        pre_json_message["sender"] = self.server.node_id
        nonce_str = os.urandom(16).hex()
        pre_json_message["nonce"] = nonce_str
        pre_json_message["timestamp"] = time.time()
        data_to_hash = str(pre_json_message["timestamp"]) + pre_json_message["sender"] + nonce_str
        message_id = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()
        pre_json_message["id"] = message_id
        self.server.processed_messages.add(message_id)
        message_to_sign_str = json.dumps(pre_json_message , sort_keys=True , cls=EnumEncoder)

        pre_json_message["signature"] = authentication.generate_signature_str_rsa(self.server.node_private_key , message_to_sign_str)
        if ttl_value > 0: pre_json_message["ttl_value"] = ttl_value
        str_message = json.dumps(pre_json_message , sort_keys=True , cls=EnumEncoder)
        str_message += "#"
        return str_message
    
    def calculate_time_to_live(self): #need to rethink this
        connections = []
        for each_peer in self.server.peer_directory.values():
            connections.append(each_peer.get("connections", 0))

        n = max(1, len(connections))
        k = CONSTANTS.MIN_CONNECTIONS

        return max(1, math.ceil(math.log(n, max(1, k))) + 1)

    async def ttl_broadcast(self , pre_json_message , target_node_id:str=None):
        pre_json_message["message_type"] = "ttl"
        ttl_value = self.calculate_time_to_live()
        if target_node_id:
            pre_json_message["target_node"] = target_node_id

        str_message = self.process_message(pre_json_message , ttl_value)
        for eachConnection in self.server.connections:
            try:
                writer = eachConnection.get("writer")
                writer.write(str_message.encode())
                await writer.drain()
            except Exception as e:
                self.server.logger.Log(f"Failed to send message to a client: {e}" , "error")

    async def propergate_ttl(self , pre_json_message):
        ttl_value = int(pre_json_message.get("ttl_value") or 0)
        if ttl_value <= 0:
            return
        pre_json_message["ttl_value"] = ttl_value-1
        str_message = json.dumps(pre_json_message , sort_keys=True, cls=EnumEncoder)
        # we dont want to process_message because that will change timestamp and sender ect just add message seperator char.
        str_message += "#"

        for eachConnection in self.server.connections:
            try:
                writer = eachConnection.get("writer")
                writer.write(str_message.encode())
                await writer.drain()
            except Exception as e:
                self.server.logger.Log(f"Failed to send message to a client: {e}" , "error")
                traceback.print_exc()

    async def direct_broadcast(self, pre_json_message):
        # preprocess message
        pre_json_message["message_type"] = "direct"
        str_message = self.process_message(pre_json_message)

        for eachConnection in self.server.connections:
            try:
                writer = eachConnection.get("writer")
                writer.write(str_message.encode())
                await writer.drain()
            except Exception as e:
                self.server.logger.Log(f"Failed to send message to a client: {e}" , "error")


    async def send_direct_message(self, address , port , pre_json_message):
        # Preprocess message.
        pre_json_message["message_type"] = "direct"
        str_message = self.process_message(pre_json_message)

        for each_connection in self.server.connections:
            try:
                if each_connection.get("host") == address and each_connection.get("port") == port:
                    writer = each_connection.get("writer")
                    writer.write((str_message).encode())
                    await writer.drain()
                    self.server.logger.Log(f"Message sent to {address}" , "info")
                    return
            except Exception as e:
                self.server.logger.Log(f"Failed to send message to {address}: {e}" , "error")
                return

        self.server.logger.Log(f"Failed to send message to {address} no direct connection")

        # open a temp connection if there is no conneciton.

        try:
            await self.server.set_up_temp_connection(address , port)
            writer = self.server.temp_connections[(address,port)].get("writer")
            writer.write((str_message).encode())
            await writer.drain()
            await self.server.close_temp_connection(address , port)
        except:
             self.server.logger.Log(f"Failed to send message to {address} error sending.")
