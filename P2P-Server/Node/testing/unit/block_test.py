import os
import unittest
import sys
import random
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(project_root_dir)

import utilities.authentication as auth
from blockchain.blockchain import Blockchain
from blockchain.block import Block, load_from_dict, load_from_json
from blockchain.transaction import Transaction

def generate_block(size : int) -> Block:
    new_block = Block()
    for i in range(0 , size):
        new_transaction = Transaction("test" , random.randint(0 , 999))
        new_block.add_transaction(new_transaction)
    return new_block

class TestBlockchain(unittest.TestCase):
    def test_serialization_to_dict(self) -> None:
        test_block = generate_block(100)
        serialized_block = test_block.serialize()
        loaded_block = load_from_dict(serialized_block)
        self.assertEqual(loaded_block.hash , test_block.hash)

    def test_serialization_to_json(self) -> None:
        test_block = generate_block(100)
        serialized_block = test_block.serialize()
        serialized_block_json : str = json.dumps(serialized_block , sort_keys=True)
        loaded_block = load_from_json(serialized_block_json)
        self.assertEqual(loaded_block.hash , test_block.hash)

if __name__ == '__main__':
    unittest.main()
