"""This module contains the methods and logic used by lead validators nodes"""
from __future__ import annotations  # Type checking

# Standard library imports
import asyncio
import random
import traceback
import typing
import time
import os

# Blockchain imports
from blockchain.block import Block , load_from_dict

from blockchain.transaction import Transaction
import utilities.authentication as auth

from typing import TYPE_CHECKING
from server.core import constants
from server.core.logger import LOG_EVENTS

if TYPE_CHECKING:
    from server.core.server import Server
    from server.core.server_events import ServerEvents

# Server imports
import server.handlers.blockchain_operations as blockchain_operations
from server.core.constants import MESSAGE_CODES

async def self_became_lead_validator(server : Server ):
    if server.lead_validator: return print("already validator") #already a valdiator no need to process twice
    server.lead_validator = True
    #server.server_events.blc_became_validator.emit()
    server.logger.Log(f"{LOG_EVENTS.SELF_BECAME_VALIDATOR.value} ({server.node_id})" , "warn")

    server_events : ServerEvents = server.server_events
    server_events.blc_became_lead_validator.emit()

    #validator loop
    asyncio.create_task(lead_validator_loop(server))

async def self_no_longer_lead_validator(server : Server ):
    if server.lead_validator == False: return print("not a validator") #already a valdiator no need to process twice
    server.lead_validator = False
    #server.server_events.blc_became_validator.emit()
    print("no longer lead validator")

    #validator loop
    asyncio.create_task(lead_validator_loop(server))

async def add_validator(server : Server, node_id : int) -> None:

    nonce = os.urandom(16).hex()
    signed_data = f"({node_id},{nonce})"
    signature = auth.generate_signature_str_rsa(server.node_private_key , nonce)

    validator_transaction_data =  {
        "node_id" : node_id,
        "signed_data" : signed_data,
        "signature" : signature
    }

    server.blockchain_operations.add_transaction_to_working("ADD_VALIDATOR" , validator_transaction_data)

async def handle_proposal(server : Server , proposal_message : dict) -> None:
    """This function will only be used by lead_validators, it will handle proposal requests"""
    proposal = proposal_message.get("data")
    if proposal is None: return

    proposal_type = proposal.get("type")
    proposal_data = proposal.get("data")
    if not(proposal_data and proposal_type): return

    if proposal_type == "ADD_VALIDATOR":
        await add_validator(server , proposal_data)

async def lead_validator_loop(server : Server):
    while server.lead_validator:
        try:
            await submit_working_block_to_network(server)
        except Exception as e:
            server.logger.Log("Discovery protocol error", "error")
            traceback.print_exc()
        finally:
            await asyncio.sleep(constants.BLOCK_PERIOD)

async def submit_working_block_to_network(server : Server):

    block_nonce = os.urandom(16).hex()
    signature = auth.generate_signature_str_rsa(server.node_private_key , block_nonce)

    server.blockchain_operations.add_transaction_to_working(
        "SUBMIT_BLOCK", {
            "node_id" : server.node_id,
            "signed_nonce" : block_nonce,
            "signature" : signature
        }
    )  # generate some random test data

    finalized_block = server.working_block
    # print("SENT" , len(finalized_block.data))
    server.blockchain_operations.finalize_block()

    finalize_message = {
        "code" : MESSAGE_CODES.NEW_BLOCK_ADDED.value,
        "data" : {
            "finalized_block" : finalized_block.serialize()
        }
    }

    await server.message_proccessor.ttl_broadcast(finalize_message)


def add_candidate(server : Server , candidate_name : str , candidate_id : int) -> None:
    server.blockchain_operations.add_transaction_to_working(
        "ADD_CANDIDATE",
        {
            "candidate_id" : candidate_id,
            "candidate_name" : candidate_name
        }
    
    )
