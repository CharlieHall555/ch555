from __future__ import annotations  # Type checking

# Standard library imports
import json
import time
import typing
import asyncio
import random

# Asyncio imports
from asyncio.streams import StreamWriter
from server.core.logger import LOG_EVENTS

# Type checking imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.server import Server

# Server constants
import server.core.constants as CONSTANTS
from server.core.constants import MESSAGE_CODES, MAX_CONNECTIONS, VERIFCATION_EXEMPT_CODES

# Server modules
import utilities.authentication as authentication
import server.handlers.blockchain_operations as blockchain_operations
import server.handlers.discovery_handler as discovery_handler
import server.handlers.validator_actions as validator_actions
import server.handlers.lead_validator_actions as lead_validator_actions
from utilities.enum_encoder import EnumEncoder


#End of imports

# Initial message parsing
async def handle_message(server : Server, message: dict[str , typing.Any], writer: StreamWriter, acceptor: bool):
    """Takes the message and a dictionary, verifies it and calls any actions that result from the message."""#
    code = message.get("code")
    if is_message_valid(server , message) == False:
        return
    
    sender = message.get("sender")
    message_id = message.get("id")
    
    server.processed_messages.add(message_id) 

    message_type = message.get("message_type")
    if message_type == "ttl":
        asyncio.create_task(server.message_proccessor.propergate_ttl(message))
        #if the ttl message has a target node designated dont process the ttl message just propergate.
        if message.get("target_node") is not None and message.get("target_node") != server.node_id:
            return


    # handshake messages for bootsrap connections
    if code == MESSAGE_CODES.BOOTSTRAP_JOIN_REQUEST.value:
        await server.handle_join_request(message, writer, acceptor , is_initial=True)
    elif code == MESSAGE_CODES.BOOTSTRAP_JOIN_REQUEST_ACCEPTED.value:
        server.connection_handler.connection_success()
        await server.handle_join_request_accepted(message , writer , is_initial=True)
    elif code == MESSAGE_CODES.BOOTSTRAP_JOIN_REQUEST_REJECTED.value:
        #try again
        await server.connection_handler.connection_failed(message)

    #Other connections
    elif code == MESSAGE_CODES.JOIN_REQUEST.value:
        print("join request!")
        await server.handle_join_request(message, writer, acceptor , is_initial=False)
    elif code == MESSAGE_CODES.JOIN_REQUEST_ACCEPTED.value:
        server.connection_handler.connection_success()
        print("join worked")
        await server.handle_join_request_accepted(message , writer , is_initial=False)
    elif code == MESSAGE_CODES.JOIN_REQUEST_REJECTED.value:
        print("could not join")
        await server.connection_handler.connection_failed(message)
        

    #All other messages.
    elif code == MESSAGE_CODES.REQUEST_FULL_BLOCKCHAIN.value:
        await handle_request_full_blockchain(server , message)
    elif code == MESSAGE_CODES.REQUEST_BASIC_SNAPSHOT.value:
        await handle_request_basic_snapshot(server, message)
    elif code == MESSAGE_CODES.SEND_BASIC_SNAPSHOT.value:
        handle_recieved_snapshot(server, message)
    elif code == MESSAGE_CODES.SEND_FULL_BLOCKCHAIN.value:
        handle_recieved_blockchain(server, message)
    elif code == MESSAGE_CODES.CONNECTION_DISCOVERY.value:
        server.discovery_handler.handle_connection_discovery_message(message)
    elif code == MESSAGE_CODES.NODE_DISCOVERY.value:
        server.discovery_handler.handle_node_discovery_message(message)
    elif code == MESSAGE_CODES.GLOBAL_NODE_DISCOVERY.value:
        if server.validator == True:
            server.discovery_handler.handle_global_discovery_message(message)
    elif code == MESSAGE_CODES.HEARTBEAT.value:
        if server.validator:
            validator_actions.handle_heartbeat(server , message)
    elif code == MESSAGE_CODES.PING.value:
        handle_ping_message(server, message)
    elif code == MESSAGE_CODES.PROPOSE_VALIDATOR.value:
        pass
    elif code == MESSAGE_CODES.TEXT.value:
        handle_text_message(server, message)
    elif code == MESSAGE_CODES.VOTE.value:
        validator_actions.handle_vote(server , message)

    elif code == MESSAGE_CODES.NEW_BLOCK_ADDED.value:
        await server.new_block_proccessor.handle_new_block(message)
    elif code == MESSAGE_CODES.BECOME_VALIDATOR_REQUEST.value:
        pass
    elif code == MESSAGE_CODES.PROPOSAL.value:
        if server.validator:
            await lead_validator_actions.handle_proposal(server , message)
    else:
        server.logger.Log(f"Unknown message code: {code}", "warn")

def is_message_valid(server : Server , message : dict[str , typing.Any]) -> bool:
    if isinstance(message, dict) == False:
        return False
    
    code = message.get("code")
    if code is None:
        return False
    
    if (code in VERIFCATION_EXEMPT_CODES) == False and verify_message(server, message) == False:
        return False
        

    message_id = message.get("id")
    if message_id and message_id in server.processed_messages: 
        return False
    
    return True

def verify_message(server : Server, message : dict[str , typing.Any]):
    """verifies a message from the message signature by creating a shallow copy of the message dict to
    not modify the original message, returns a boolean """
    message_copy = message.copy()

    signature : str = str(message.get("signature"))
    message_copy.pop("signature", None)
    ttl_value = 0
    
    message_type = message.get("message_type")

    if message_type == "ttl":
        ttl_value = message_copy.pop("ttl_value", 0)

    sender = message.get("sender")

    peer_data = server.peer_directory.get(sender)
    if peer_data is None:
        print("No peer data")
        return False
    public_key_str = peer_data.get("public_key")
    if public_key_str is None:
        print("no public key str")
        return False

    output =  authentication.verify_signature_rsa(
        public_key_str, json.dumps(message_copy, sort_keys=True, cls=EnumEncoder), signature
    )

    return output


def handle_received_validators(server, message):

    message_data = message.get("data")
    assert message_data

    validators = message_data.get("validators")
    server.logger.Log("Got SEND_VALIDATORS message")

async def handle_request_full_blockchain(server : Server , message):
    sender = message.get("sender")
 
    response = {
        "code": MESSAGE_CODES.SEND_FULL_BLOCKCHAIN,
        "data": {
            "blockchain_data" : server.block_chain.to_json()
        },
    }

    await server.message_proccessor.ttl_broadcast(response , target_node_id=sender)


async def handle_request_basic_snapshot(server : Server , message):

    sender = message.get("sender")
 
    response = {
        "code": MESSAGE_CODES.SEND_BASIC_SNAPSHOT,
        "data": server.snapshot.to_json(),
    }

    await server.message_proccessor.ttl_broadcast(response , target_node_id=sender)


def handle_ping_message(server, message):
    """Handle the logic and action from the ping message."""
    pass


def handle_text_message(server : Server, message : dict):
    message_data : typing.Optional[typing.Dict] = message.get("data" , None)
    if message_data: 
        message_text = message_data.get("text" , None)
        if message_text:
            server.logger.Log(f"{LOG_EVENTS.MESSAGE_RECIEVED.value} ({message_text})" , "warn")

def handle_recieved_snapshot(server : Server, message):
    sender = message.get("sender")

    if server.snapshot.lead_validator is None or server.snapshot.is_lead_validator(sender):
        server.blockchain_operations.load_snapshot(message.get("data"))


def handle_recieved_blockchain(server : Server , message):
    sender = message.get("sender")
    message_data = message.get("data")
    blockchain_json = message_data.get("blockchain_data")
    server.blockchain_operations.load_blockchain(blockchain_json)




# --NEW-MESSAGES-



