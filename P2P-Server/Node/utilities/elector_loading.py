
from __future__ import annotations  # Type checking

#standard lib imports
import os
import typing
import json

import utilities.authentication as authentication

#type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server.core.server import Server
    from server.core.server_events import ServerEvents

def read_electors_file() -> typing.Optional[dict]:
    if os.path.exists("electors.json") == False:
        return None

    file = open("electors.json" , "r")
    output = json.load(file)
    file.close()
    return output

def read_credentials_file():
    if os.path.exists("credentials.json") == False:
            return None
    file = open("credentials.json" , "r")
    credentials = json.load(file)
    file.close()
    return credentials
