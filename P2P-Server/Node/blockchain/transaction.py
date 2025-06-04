import hashlib
import json

def load_from_json(json_str : str):
    """Creates a instance of transaction from a dictionary passed as a json string."""
    loaded_dict = json.loads(json_str)
    loaded_data = json.loads(loaded_dict["data_json"])
    operation_str = loaded_dict["operation"]
    assert(operation_str and loaded_data)
    new_transaction = Transaction(operation_str , loaded_data)
    return new_transaction

def load_from_dict(dict : dict) -> "Transaction":
    """Creates a instance of transaction from a dictionary passed as a parameter."""
    operation_str = dict.get("operation")
    data = dict.get("data")
    new_transaction = Transaction(operation_str , data)
    return new_transaction


class Transaction:
    data : dict
    hash : str
    """This class contains the individual operations added on the blockchain, it will be used to make up
    Blocks that will be added to the blockchain."""
    def __init__(self , operation , data):
        self.operation = operation
        self.data = data
        self.hash = self.calculate_hash()
        
    def calculate_hash(self) -> str:
        data_to_hash = (str(self.operation) + str(self.data))
        return hashlib.sha256(data_to_hash.encode()).hexdigest()

    def serialize(self) -> dict:
        transaction_dict = {}
        transaction_dict["operation"] = self.operation
        transaction_dict["data"] = self.data
        return transaction_dict
    
    def to_json(self) -> str:
        return json.dumps(self.serialize() , sort_keys=True)
    
    def __str__(self):
        return self.operation + json.dumps(self.data) + self.hash

    def __repr__(self):
        return str(self)