from blockchain.transaction import load_from_dict as load_transaction_from_dict, Transaction
import hashlib
import json

def load_from_dict(dict):
    new_block = Block()
    hash_value = dict.get("hash")
    data_list = dict.get("data")
    new_block.previous_hash = dict.get("previous_hash")

    for each_transaction_json in data_list:
        new_transaction = load_transaction_from_dict(each_transaction_json)
        new_block.add_transaction(new_transaction)

    return new_block

def load_from_json(json_str):
    loaded_dict = json.loads(json_str)
    return load_from_dict(loaded_dict)


class Block:
    """This class contains transactions and is the smallest unit that will be individually added to the blockchain"""
    def __init__(self, previous_hash=0):
        self.previous_hash = "0"
        # self.timestamp = timestamp
        self.data = []  # list of transactions
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Generates a hash string depending on block content."""
        data_to_hash = str(self.previous_hash)
        each_transaction : Transaction
        for each_transaction in self.data:
            data_to_hash += each_transaction.to_json()
        return hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()

    def set_previous_hash(self , new_previous_hash):
        if isinstance(new_previous_hash, int):
            new_previous_hash = str(new_previous_hash)
        self.previous_hash = new_previous_hash
        self.hash = self.calculate_hash()

    def add_transaction(self, transaction):
        self.data.append(transaction)
        self.hash = self.calculate_hash()

    def __str__(self) -> str:
        return f"Hash : {self.hash} \nLength : {len(self.data)} \nPrevious Hash : {self.previous_hash[:6]} \n   {self.data} \n" + ("-" * 36)

    def serialize(self) -> dict:
        """Generates a dictionary from the contents of the block."""
        output_dict = {}
        output_dict["hash"] = self.hash
        output_dict["previous_hash"] = self.previous_hash

        data_list = []
        for each_transaction in self.data:
            data_list.append(each_transaction.serialize())

        output_dict["data"] = data_list

        return output_dict

    def to_json(self)-> str:
        return json.dumps(self.serialize() , sort_keys=True , separators=(',', ':'))
