from __future__ import annotations  # Type checking

#standard lib
import os
import json

# Type checking imports
from typing import TYPE_CHECKING

import server.core.constants as constants

import utilities.authentication as authentication
from utilities.elector_loading import read_credentials_file

if TYPE_CHECKING:
    from server.core.server import Server, ServerEvents
    from blockchain.blockchain_snapshot import Snapshot 
    from threads.api_thread import Credentials



async def propose_vote(server : Server, vote_choice_id : int):
    """request to add a vote, note vote data is encryped using the voter credential private key as known by the server. 
    this is a special type of proposal becuase we cant just use a normal proposal becuase the private keys would be expose to all
    on the network through ttls, so the public key and private key must be encrypted"""

    #simple 'client' side sanity check here, checking the voter is voting for a valid option as known by the client

    print("ra")

    lead_validator_id = server.snapshot.get_lead_validator()
 
    if lead_validator_id is None: 
        print("lead_validator_id missing")
        return

    if server.elector_private_key is None or server.elector_public_key is None:
        print("elector credentials must be submitted before")
        return

    vote_package = {
        "elector_public_key" : authentication.compress_ecdsa_key(server.elector_public_key),
        "choice" : vote_choice_id,
        "nonce" : os.urandom(16).hex(),
    }

    signature = authentication.generate_signature_ecdsa(server.elector_private_key , json.dumps(vote_package , sort_keys=True))
    message = {
        "code" : constants.MESSAGE_CODES.VOTE.value,
        "data" : {
            "vote_package" : vote_package,
            "signature" : signature
        }
    }

    print(message)
    await server.message_proccessor.ttl_broadcast(message , lead_validator_id)

async def own_vote_detected(server : Server , blockhash : str):#
    server.logger.Log("own vote" , "warn")
    server.server_events.blc_own_vote_detected.emit(blockhash)

def load_credentials_from_file(server : Server):
    server_events : ServerEvents = server.server_events
    credentials = read_credentials_file()
    if credentials is None:
        server_events.sys_missing_local_creds_file.emit()
        server.logger.Log("electors.json missing." , "warn")
        return

    compressed_public_key = credentials.get("public_key")
    compressed_private_key = credentials.get("private_key")
    try:
        server.elector_private_key = authentication.decompress_ecdsa_key(compressed_private_key , is_private=True)
        server.elector_public_key = authentication.decompress_ecdsa_key(compressed_public_key , is_private=False)
    except Exception as e:
        return


    server_events.sys_new_elector_creds_loaded.emit(compressed_public_key , compressed_private_key)
    server.logger.Log("new elector credentails loaded" , "warn")

def load_credentials_from_api(server : Server , credentials:Credentials=None):
    server_events : ServerEvents = server.server_events

    if credentials is None:
        server_events.sys_missing_local_creds_file.emit()
        server.logger.Log("electors.json missing." , "warn")
        return
    
    print(credentials)

    compressed_public_key = credentials.public_key
    compressed_private_key = credentials.private_key
    try:
        server.elector_private_key = authentication.decompress_ecdsa_key(compressed_private_key , is_private=True)
        server.elector_public_key = authentication.decompress_ecdsa_key(compressed_public_key , is_private=False)
    except Exception as e:
        server.logger.Log(f"failed to load credentials from api. {e}" , "warn")
        return

    server_events.sys_new_elector_creds_loaded.emit(compressed_public_key , compressed_private_key)
    server.logger.Log("new elector credentails loaded" , "warn")
