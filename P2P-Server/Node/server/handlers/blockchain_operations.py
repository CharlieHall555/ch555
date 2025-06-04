"""
This modules cotains functions that are used to manipulate the instance of the blockchain stored in the server class.
"""

from __future__ import annotations  # Type checking

# Standard library imports
import json
import typing
import asyncio
import traceback
import typing

# Type checking imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.server import Server

# Blockchain modules
from blockchain.blockchain_snapshot import Snapshot, load_snapshot_from_dict
from blockchain.block import Block, load_from_dict as load_block_from_dict
from blockchain.blockchain import (
    load_from_dict as load_blockchain_from_dict,
    Blockchain,
)
from blockchain.transaction import Transaction
import server.handlers.validator_actions as validator_actions
import server.handlers.lead_validator_actions as lead_validator_actions
import server.handlers.elector_actions as elector_actions
import utilities.authentication as auth

# Server modules
from server.core.constants import SNAPSHOT_OPERATIONS, MESSAGE_CODES
from server.core.logger import LOG_EVENTS


def initial_parse_transaction(server: Server, transaction: Transaction , parentBlock : Block) -> None:
    """The purpose of this parse is to parse for any action that needs to be taken based on the blockchain state."""
    if transaction.operation == "ADD_VALIDATOR":
        if transaction.data.get("node_id" , "") == server.node_id:
            asyncio.create_task(validator_actions.self_became_validator(server))
            server.logger.Log(f"{LOG_EVENTS.SELF_BECAME_VALIDATOR.value} ({server.node_id})", "info")
    elif transaction.operation == "SET_LEAD_VALIDATOR":
        if transaction.data.get("node_id" , "") == server.node_id:
            asyncio.create_task(lead_validator_actions.self_became_lead_validator(server))
            server.logger.Log(f"{LOG_EVENTS.SELF_BECAME_LEAD_VALIDATOR.value} ({server.node_id})", "info")
        elif server.lead_validator == True:
            asyncio.create_task(lead_validator_actions.self_no_longer_lead_validator(server))


    elif transaction.operation == transaction.operation == "ADD_VOTE":
        if server.elector_public_key is not None:
            compressed_elector_key = auth.compress_ecdsa_key(server.elector_public_key)
            voter_public_key = transaction.data.get("voter_public_key" , None)
            if voter_public_key == compressed_elector_key:
                asyncio.create_task(elector_actions.own_vote_detected(server , parentBlock.hash))
                server.logger.Log(f"{LOG_EVENTS.OWN_VOTE_DETECTED.value} ({parentBlock.hash})", "info")




def parse_transaction_for_snapshot(server: Server, transaction: Transaction) -> None:
    """The purpose of this parse is to update the snapshot state and also to emit any changes to the server interface."""
    if transaction.operation in SNAPSHOT_OPERATIONS:

        if transaction.operation == "ADD_VALIDATOR":
            node_id = transaction.data.get("node_id", "unknown")
            server.snapshot.add_validator(node_id)
            server.logger.Log(f"{LOG_EVENTS.VALIDATOR_ADDED_TO_LOCAL_SNAPSHOT.value} ({node_id})", "info")
            server.server_events.blc_validator_added.emit(node_id)
        elif transaction.operation == "SET_LEAD_VALIDATOR":
            node_id = transaction.data.get("node_id")
            server.snapshot.set_lead_validator(node_id)
            server.server_events.blc_lead_validator_set.emit(node_id)
            server.logger.Log(f"{LOG_EVENTS.LEAD_VALIDATOR_CHANGED_ON_LOCAL_SNAPSHOT.value} ({node_id})", "info")
        elif transaction.operation == "ADD_CANDIDATE":
            candidate_name = transaction.data.get("candidate_name")
            candidate_id = transaction.data.get("candidate_id")
            print(candidate_name , candidate_id)
            server.snapshot.add_candidate(
                candidate_name,
                candidate_id
            )
            server.logger.Log(f"{LOG_EVENTS.CANDIDATE_ADDED.value} ({candidate_name},{candidate_id})", "info")
            server.server_events.blc_candidate_added.emit(candidate_name , candidate_id)

        elif transaction.operation == "ADD_ELECTOR":
            server.snapshot.add_elector(transaction.data.get("elector_public_key"))
        elif transaction.operation == "ADD_VOTE":
            voter_public_key = transaction.data.get("voter_public_key")
            vote_choice = transaction.data.get("vote_choice")
            if vote_choice is None:
                return
            vote_choice = int(vote_choice)
            server.snapshot.set_elector_voted(voter_public_key, True)
            server.snapshot.add_vote(vote_choice)
            server.server_events.blc_new_vote_added.emit(server.snapshot.vote_tally.copy())

def parse_block(server: Server, block: Block) -> None:
    each_transaction: Transaction
    for each_transaction in block.data:
        initial_parse_transaction(server, each_transaction , block)
        parse_transaction_for_snapshot(server, each_transaction)

class BlockchainOperations:

    def __init__(self, server: Server):
        self.server = server
        self.lock_blockchain = False

        self.snapshot_update_events = {
            "blockchain_head": self.server.server_events.blc_snapshot_head_updated,
        }

    def set_blockchain_lock(self , value : bool) -> None:
        self.lock_blockchain = value

    def verify_hash_integrity(server: Server) -> bool:
        """returns a boolean verifiying if the blockchain's hashses are valid up to the current head"""
        # validation rules
        # 1st rule basic run make sure hashes match
        previous_block = server.block_chain.chain[0]
        for n in range(1, len(server.block_chain.chain) - 1):
            current_block = server.block_chain.chain[n]
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def load_snapshot(self, snapshot_data_str: str) -> None:
        """Deletes current snapshot state and creates a new snapshot from snapshot_data"""
        try:
            snapshot_data: typing.Dict[str, typing.Any] = json.loads(snapshot_data_str)
            assert snapshot_data is not None
            self.server.snapshot = load_snapshot_from_dict(snapshot_data)
            self.server.server_events.blc_new_snapshot_loaded.emit(self.server.snapshot.copy())
        except Exception as e:
            self.server.logger.Log(f"Could not load snapshot data: {e}.", "error")

    def set_snapshot_attr(self, attribute: str, new_value: typing.Any):
        """Method used to set a snapshot attribute. 
        If the attribute is connected to a pyqt singal through the snapshot_update_events table, this will also be called.
        Raises a KeyError if given attribute is not valid."""
        if hasattr(self.server.snapshot, attribute):
            setattr(self.server.snapshot, attribute, new_value)
            if attribute in self.snapshot_update_events.keys():
                event = self.snapshot_update_events.get(attribute)
                event.emit(new_value)
        else:
            raise KeyError(f"{attribute} is not a value attribute of server.snapshot")


    def new_working_block(self):
        """Creates a new empty working block."""
        self.server.working_block = Block(self.server.block_chain.head)


    def load_blockchain(self, blockchain_data_str: dict):
        """Deletes current blockchain state and creates a new blockchain from blockchain_data"""
        try:
            self.server.logger.Log(f"loading blockchain data this may take a while!", "warn")
            self.server.snapshot.reset()
            blockchain_data : typing.Dict[str, typing.Any] = json.loads(blockchain_data_str)
            received_head = blockchain_data.get("head")
            received_chain_list = blockchain_data.get("chainlist")
            assert received_head and received_chain_list
            loaded_blockchain: Blockchain = load_blockchain_from_dict(blockchain_data)
            self.server.server_events.blc_new_blockchain_loaded.emit()
            self.server.block_chain = loaded_blockchain
            for each_block in self.server.block_chain.chain:
                #parse block to make ensure snapshot is up to date.
                parse_block(self.server , each_block)
                self.server.server_events.blc_block_added.emit(each_block.serialize())

            self.server.logger.Log(f"completed loaded received blockchain data!", "warn")
           

        except Exception as e:
            self.server.logger.Log(f"failed to load received blockchain data, {e}", "error")
            traceback.print_exc()
        finally: 
            self.set_blockchain_lock(False)

  
    def load_block(self, blockdata_dict: dict):
        """Deletes current working block and replaces it with block generated from block_data.
        This method should be used with caution by validators who must verify a block before accepting.
        """
        new_block = load_block_from_dict(blockdata_dict)
        if new_block.hash == self.server.block_chain.head:
            return  # already processed
        self.server.working_block = new_block
        self.finalize_block()
        return new_block


    def add_transaction_to_working(self, operation: str, data: typing.Dict):
        """Adds transaction to local working block."""
        try:
            assert(self.server.working_block)
            new_transaction = Transaction(operation, data)
            self.server.working_block.add_transaction(new_transaction)
        except Exception as e:
            self.server.logger.Log(f"Error adding to working block {e}" , "error")


    def finalize_block(self):
        """A finalized block cannot be edited anymore."""
        try:
            if self.lock_blockchain == True: 
                print("blockchain is locked")
                return
            assert(self.server.block_chain)
            assert(self.server.working_block)

            #lock old block and add old block to blockchain
            self.server.working_block.set_previous_hash(self.server.snapshot.blockchain_head)
            old_block = self.server.working_block   
            self.server.block_chain.add_block(self.server.working_block, enforce_previous_hash=False)
            parse_block(self.server, old_block)
            self.set_snapshot_attr("blockchain_head" , self.server.block_chain.head)

            #create new working block to append new transactions to.
            self.new_working_block()

            #Fire events
            self.server.server_events.blc_blockchain_updated.emit(self.server.block_chain.serialize())
            self.server.server_events.blc_block_added.emit(old_block.serialize())
            
        except Exception as e:
            self.server.logger.Log(f"Error adding to finalising block; {e}" , "error")
            



