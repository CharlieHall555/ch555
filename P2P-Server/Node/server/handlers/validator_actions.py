"""This module contains the logic and methods used by all validator nodes."""
from __future__ import annotations  # Type checking

# Standard library imports
import asyncio
import random
import traceback
import typing
import time
import json
import os

# Blockchain imports
from blockchain.block import Block , load_from_dict
from server.core.logger import LOG_EVENTS
from blockchain.transaction import Transaction
import server.handlers.lead_validator_actions as lead_validator_actions
from server.handlers.discovery_handler import generate_global_nodes, generate_discovered_nodes

import utilities.authentication as authentication
from utilities.elector_loading import read_electors_file

from typing import TYPE_CHECKING
from server.core import constants

if TYPE_CHECKING:
    from server.core.server import Server

# Server imports
import server.handlers.blockchain_operations as blockchain_operations
from server.core.constants import MESSAGE_CODES

#function is not used in current implementation due to no verication method for new validators, this could be added later.
async def request_to_become_a_validator(server : Server): 
    """sends a request to become a validator to the lead validator."""
    if server.validator: return #already a validator.

    lead_validator_id = server.snapshot.get_lead_validator()
    if lead_validator_id:
        message = {
            "code" : constants.MESSAGE_CODES.PROPOSAL.value,
            "data" : {
                "type" : "ADD_VALIDATOR",
                "data" : server.node_id,
            }
        }
        await server.message_proccessor.ttl_broadcast(message , lead_validator_id)

async def self_became_validator(server : Server , bootstrap:bool=False):
    if server.validator: return print("already validator") #already a valdiator no need to process twice
    server.validator = True
    server.server_events.blc_became_validator.emit()
    server.logger.Log(f"{LOG_EVENTS.SELF_BECAME_VALIDATOR.value} ({server.node_id})" , "warn")


    #validator loop
    asyncio.create_task(validator_discovery_loop(server))
    asyncio.create_task(validator_loop(server))
    #request full blockchain
    if bootstrap == False:
        lead_validator = server.snapshot.get_lead_validator()  
        server.blockchain_operations.set_blockchain_lock(True) 

        message = {
            "code": MESSAGE_CODES.REQUEST_FULL_BLOCKCHAIN.value,
        }

        await server.message_proccessor.ttl_broadcast(message , target_node_id=lead_validator)

def add_candidate(server : Server , candidate_name : str) -> None:
    operation : str = "ADD_CANDIDATE"
    each_trans : Transaction
    n : int = 0
    for each_trans in server.working_block.data:
        if each_trans.operation == "ADD_CANDIDATE":
            n+=1
    next_candidate_id = server.snapshot.get_highest_candidate_id() or 0
    next_candidate_id += n + 1
    candidate_data : typing.Dict[str , str | int] = {
        "candidate_name" : candidate_name,
        "candidate_id" : next_candidate_id,
    }
    server.blockchain_operations.add_transaction_to_working(operation , candidate_data)

def verify_vote(server : Server, vote_sig:str , vote_nonce : str, voter_public_key_comp : str , choice_id:int) -> bool:
    #reconstruct vote package.

    reconstructed_vote_package : dict = {
        "elector_public_key" : voter_public_key_comp,
        "choice" : choice_id,
        "nonce" : vote_nonce,
    }

    valid_candidates = server.snapshot.get_candidates()

    #candidate valid check.
    candidate_entry = valid_candidates.get(choice_id , None)
    if candidate_entry is None: 
        server.logger.Log(f"{LOG_EVENTS.CANDIDATE_CHOSEN_NOT_VALID.value} ({choice_id})" , "warn")
        return False

    #elector registered check.
    if server.snapshot.is_elector_registered(voter_public_key_comp) == False:
        server.logger.Log(f"{LOG_EVENTS.UNKNOWN_ELECTOR_CREDS.value} ({voter_public_key_comp})" , "warn")
        return False

    if server.snapshot.has_elector_voted(voter_public_key_comp) == True:
        server.logger.Log(f"{LOG_EVENTS.ELECTOR_ALREADY_VOTED.value} ({voter_public_key_comp})" , "warn")
        return False

    #check vote signature.
    json_package : str = json.dumps(reconstructed_vote_package , sort_keys=True)
    voter_public_key = authentication.decompress_ecdsa_key(voter_public_key_comp , is_private=False)

    return authentication.verify_signature_ecdsa(voter_public_key , json_package , vote_sig)


def handle_vote(server : Server , vote_message : dict) -> None:
    message_data : typing.Dict[str,typing.Any] = vote_message.get("data" , None)
    vote_signature : str = message_data.get("signature" , None)
    vote_package : typing.Dict[str,typing.Any] = message_data.get("vote_package" , None)

    vote_nonce = vote_package.get("nonce" , None) 
    voter_public_key_str : str = vote_package.get("elector_public_key" , None)
    voter_public_key_str = voter_public_key_str.strip()
    choice_id : int = int(vote_package.get("choice" , "-999"))

    if verify_vote(
        server=server,
        vote_sig=vote_signature,
        vote_nonce=vote_nonce,
        voter_public_key_comp=voter_public_key_str,
        choice_id=choice_id,
    ) == True:
        #verification passed.
        vote_data = {
            "vote_choice" : choice_id,
            "voter_public_key" : voter_public_key_str,
            "vote_signature" : vote_signature,
            "nonce" : vote_nonce
        } 
        server.blockchain_operations.add_transaction_to_working("ADD_VOTE" , vote_data)
        server.logger.Log(f"{LOG_EVENTS.VOTE_COUNTED.value} ({choice_id})" , "info")
    else:
        server.logger.Log(f"{LOG_EVENTS.RECEIVED_VOTE_FAILED_VERIFCATION.value} ({choice_id})" , "warn")


async def send_node_discovery_message(server : Server):
    """Sends list of """
    list_discovered_peers = generate_discovered_nodes(server)
    node_discovery_message = {
        "code": MESSAGE_CODES.NODE_DISCOVERY.value,
        "data": {
            "data_timestamp": time.time(),
            "discovered_peers": list_discovered_peers,
        },
    }

    await server.message_proccessor.ttl_broadcast(node_discovery_message)

def new_lead_validator_id(server : Server) -> str:
    list_of_validators = sorted(server.snapshot.get_validators())

    hash_bytes = authentication.generate_sha256_hash(server.snapshot.blockchain_head).encode("utf-8")
    hash_int = int.from_bytes(hash_bytes, byteorder='big')

    chosen_index = (hash_int % len(list_of_validators)) + 1

    return list_of_validators[chosen_index-1]

async def send_reassign_message(server : Server , new_validator_id : str) -> None:

    block_nonce = os.urandom(16).hex()
    signature = authentication.generate_signature_str_rsa(server.node_private_key , block_nonce)

    server.blockchain_operations.add_transaction_to_working(
        "SET_LEAD_VALIDATOR", {
            "node_id" : new_validator_id,
        }
    ) 

    finalized_block = server.working_block
    server.blockchain_operations.finalize_block()

    finalize_message = {
        "code" : MESSAGE_CODES.NEW_BLOCK_ADDED.value,
        "data" : {
            "finalized_block" : finalized_block.serialize()
        }
    }

    await server.message_proccessor.ttl_broadcast(finalize_message)

async def validator_loop(server : Server):
    T : float = time.perf_counter()
    dt : float

    new_block_count : float = 0
    old_head = server.snapshot.blockchain_head

    while server.validator:
        try:
            now = time.perf_counter()
            dt = now - T
            T = now

            new_block_count += dt

            if old_head != server.snapshot.blockchain_head:
                old_head = server.snapshot.blockchain_head
                new_block_count = 0

            if new_block_count > constants.BLOCK_TIMEOUT:

                new_id = new_lead_validator_id(server)
                await send_reassign_message(server , new_id)
                new_block_count = 0
            
        except Exception as e:
            server.logger.Log(f"Validator loop error, {e}", "error")

        finally: 
            await asyncio.sleep(0)


async def validator_discovery_loop(server : Server):
    print("vs" , server.validator)
    while server.validator:
        try:
            # Build a list of peer info with addresses and timestamps, this is now only validators.
            asyncio.create_task(send_node_discovery_message(server))

            global_discovered_peers = generate_global_nodes(server)
            #this should only be sent from validators to other validators
            global_discovery_message = {
                "code" : MESSAGE_CODES.GLOBAL_NODE_DISCOVERY.value,
                "data" : {
                    "data_timestamp" : time.time(),
                    "global_nodes" : global_discovered_peers,
                }
            }

            #SEND TO VALIDAOTRS
            validator_addresses = server.snapshot.get_validators()

            each_validator_id : str
            for each_validator_id in validator_addresses:
                if each_validator_id == server.node_id: continue
                asyncio.create_task(server.message_proccessor.ttl_broadcast(global_discovery_message , target_node_id=each_validator_id))
                

        except Exception as e:
            server.logger.Log("Validator discovery protocol error", "error")
            traceback.print_exc()
        finally:
            await asyncio.sleep(3)

async def handle_new_block(server : Server , new_block_message : dict[str , typing.Any]) -> None:
    """this function will be used by non-lead validators to verify that a block is legitimate and append it to the ledger."""
    assert server.working_block
    #setup
    data = new_block_message.get("data" , {})
    block_data = data.get("finalized_block" , None)
    if block_data is None: return
    new_block = load_from_dict(block_data)
    #verifcation

    if new_block.hash == server.snapshot.blockchain_head:
        return

    each_transaction : Transaction
    for each_transaction in new_block.data:
        
        if each_transaction.operation == "ADD_VOTE":
            vote_choice = int(each_transaction.data.get("vote_choice" , "-999"))
            voter_public_key = each_transaction.data.get("voter_public_key" , "")
            vote_signature = each_transaction.data.get("vote_signature" , "")
            nonce = each_transaction.data.get("nonce" , "")

            result = verify_vote(
                server,
                vote_signature,
                nonce,
                voter_public_key,
                vote_choice
            )

            if result == True:
                continue
            else:
                server.logger.Log("Could not propergate block: ADD_VOTE operation could not be verified.")

    #verication passed (else return before here)
    server.working_block = new_block
    server.blockchain_operations.finalize_block()

    #echo the finalization meesage.
    finalize_message = {
        "code" : MESSAGE_CODES.NEW_BLOCK_ADDED.value,
        "data" : {
            "finalized_block" : new_block.serialize()
        }
    }
    
    await server.message_proccessor.ttl_broadcast(finalize_message)

def load_all_electors(server : Server) -> None:

    electors_dict = read_electors_file()
    if electors_dict is None:
        server.server_events.sys_missing_electors_file.emit()
        return

    each_elector_info : dict 
    for each_elector_info in electors_dict.values():
        load_elector(server , each_elector_info)

def handle_heartbeat(server : Server , message : dict) -> None:
    sender = message.get("sender")

    data = message.get("data")
    timestamp = float(message.get("timestamp" , 1))

    dict_entry = server.global_node_table.get(sender)
    if dict_entry is None: return

    #print(f"HEARTBEAT FROM {sender} at {data.get("host")},{data.get("port")}")
    if float(dict_entry.get("last_seen" , 0)) < timestamp:
        dict_entry["last_seen"] = timestamp
        #update ip and port if needed
     
        dict_entry["host"] = data.get("host")
        dict_entry["port"] = data.get("port")


def load_elector(server : Server , elector_info : dict) -> None:

    elector_public_key = elector_info.get("public_key")
    elector_private_key = elector_info.get("private_key")

    if elector_private_key is None or elector_public_key is None:
        server.logger.Log("could not load elector, missing public or private key")
        return

    print(elector_public_key , elector_private_key)
    server.blockchain_operations.add_transaction_to_working(
        "ADD_ELECTOR", 
        {
            "elector_public_key" : elector_public_key
        }
    )

async def start_new_lead_validator_vote(server : Server):
    """This function is used to decide a new lead validator if the current lead becomes unresponsive."""
    validators = server.snapshot.get_validators()
    ordered_validators = sorted(validators)
    hash_bytes = server.snapshot.blockchain_head
    hash_int = int.from_bytes(hash_bytes[:8], byteorder='big')
    m = len(validators)-1
    n = (hash_int % (m - 1))
    chosen_validator_id = validators[n]

    server.blockchain_operations.add_transaction_to_working(
        "SET_LEAD_VALIDATOR", 
        {
            "node_id" : chosen_validator_id
        }
    )

    await lead_validator_actions.submit_working_block_to_network(server)

async def handle_propose_validator(origin_node_id : str) -> None:
    pass
