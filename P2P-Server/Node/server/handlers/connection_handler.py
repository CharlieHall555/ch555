from __future__ import annotations  # Type checking

# Type checking imports
import typing

from server.core.constants import MAX_CONNECTION_TRIES
import utilities.authentication as authentication

import asyncio

if typing.TYPE_CHECKING:
    from server.core.server import Server

class ConnectionHandler():
    server : Server
    def __init__(self , server):
        self.server = server
        self.connection_tries = 0
        self.is_initial = False
        self.tried = set()
        self.in_connection_loop = False

    async def connect(self , peer_host , peer_port): #check this out
        if self.in_connection_loop: 
            return
        
        self.is_initial = False
        if len(self.server.connections) == 0:
            self.is_initial = True

        self.connection_tries = 1
        self.in_connection_loop = True
        await self.server.connect_to_node(peer_host , peer_port , self.is_initial)

    def connection_success(self):
        """Connection was successful reset all the variables"""
        print("worked!")
        self.server.server_events.net_connected_successfully_to_network
        self.connection_tries = 0
        self.is_initial = False
        self.in_connection_loop = False
        

    async def connection_failed(self , failure_message):
        """Connection failed, this function is used to figure out what to do when a connection failure request was recieved by the message_actions"""
        print("failed")
        if self.in_connection_loop == False: return
        
        if self.connection_tries > MAX_CONNECTION_TRIES:
            self.connection_tries = 0
            self.is_initial = False
            self.in_connection_loop = False
            self.server.server_events.net_connection_failed.emit()

        data = failure_message.get("data")
        suggested_list : list = data.get("suggested")

        each_suggestion : typing.Dict
        for each_suggestion in suggested_list:
            each_port = each_suggestion.get("port")
            each_host = each_suggestion.get("host")
            if each_host is None or each_port is None: return
            each_port = int(each_port)
            addr = (each_host , each_port)
            if (addr in self.tried) == False and (each_port == self.server.port and each_host == self.server.host) == False:
                self.connection_tries += 1
                self.tried.add(addr)
                print("try again")
                await asyncio.sleep(2) #delay time before trying again
                await self.server.connect_to_node(each_host , each_port , self.is_initial)
                return
            
        print("ran out of candidates to connect to so failed.")
        self.connection_tries = 0
        self.is_initial = False
        self.in_connection_loop = False
        self.server.server_events.net_connection_failed.emit()


  

