from __future__ import annotations  # Type checking

# Standard library imports
import json
import time
import typing
import math

import server.core.constants as CONSTANTS
from server.handlers import validator_actions
import server.handlers.blockchain_operations as blockchain_operations
from blockchain.block import Block, load_from_dict
import utilities.authentication as auth
from blockchain.transaction import Transaction
from server.core.logger import LOG_EVENTS

# Type checking imports
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from server.core.server import Server


class NewBlockProcessor:
    """This class will handle the 'NEW_BLOCK_ADDED' message command for both validator nodes and normal nodes."""

    def __init__(self, server: Server):
        self.server = server
        self.count_dict = {}

    def get_validator_threshold(self) -> int:
        n_validators = len(self.server.snapshot.get_validators())
        if n_validators == 2: return 1
        if n_validators == 3: return 1
        """Returns the number of NEW_BLOCK_ADDED messages recieved from validators needed before a node appends to local node"""
        return math.ceil(CONSTANTS.CONSENSUS_RATIO * n_validators)

    async def handle_new_block(self, new_block_message: dict) -> None:
        """docstring"""
        message_code = new_block_message.get("code", 0)
        message_data = new_block_message.get("data" , {})
        block_data = message_data.get("finalized_block")
        new_block_hash = block_data.get("hash")

        assert(message_code == CONSTANTS.MESSAGE_CODES.NEW_BLOCK_ADDED.value)
        assert(new_block_hash)

        if self.server.lead_validator:
            return
        if self.server.validator == True:  # Validator Node handling.
            await validator_actions.handle_new_block(self.server, new_block_message) #Validator block handling is handled in seperate class.
        else:  # Normal node handling
            currentValue : int = self.count_dict.get(new_block_hash , 0)

            if new_block_message.get("sender" , "") in self.server.snapshot.get_validators():
                #check proposal was sent by validator or leadvalidator.
                self.count_dict[new_block_hash] = currentValue + 1
        
                validator_threshold : int = self.get_validator_threshold()

                if self.count_dict.get(new_block_hash , 0) >= validator_threshold:
                    
                    #check submit block trans is valid.
                    
                    if self.verify_new_submit_sig(block_data):
                        self.accept_new_block(block_data)
                    else:
                        self.server.logger.Log(f"{LOG_EVENTS.SUBMIT_BLOCK_TRANSACTION_INVALID.value} ()", "warn")


                 

    def accept_new_block(self, block_data):
        self.count_dict = {}
        new_block = self.server.blockchain_operations.load_block(block_data)

    def verify_new_submit_sig(self , block_data):
        constructed_block : Block = load_from_dict(block_data)
        if len(constructed_block.data) <= 0:
                return False
        
        last_trans : Transaction= constructed_block.data[-1]

        if last_trans.operation == "SET_LEAD_VALIDATOR": return True
                    
        signed_nonce : typing.Optional[str] = last_trans.data.get("signed_nonce" , None)
        if signed_nonce is None: 
            return False
        
        signature : typing.Optional[str] = last_trans.data.get("signature" , None)
        if signature is None:
            return False

        lead_validator_id :str = self.server.snapshot.lead_validator
        lead_validator_entry : dict = self.server.peer_directory.get(lead_validator_id , {})
        lead_validator_pub_key : typing.Optional[str] = lead_validator_entry.get("public_key" , None)

        if lead_validator_pub_key is None:
            return False

        return auth.verify_signature_rsa(
            lead_validator_pub_key,
            signed_nonce,
            signature
        )