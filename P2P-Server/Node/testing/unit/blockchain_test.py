import os
import unittest
import sys
import random
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(project_root_dir)

import utilities.authentication as auth
from blockchain.blockchain import Blockchain , load_from_dict
from blockchain.block import Block
from blockchain.transaction import Transaction
from block_test import generate_block

def generate_blockchain(size : int) -> Blockchain:
    new_blockchain = Blockchain(False)
    for i in range(0 , size):
        new_block = generate_block(10)
        new_blockchain.add_block(new_block)
    return new_blockchain

class TestBlockchain(unittest.TestCase):
    def test_serialization_to_dict(self) -> None:
        origin_blockchain = generate_blockchain(100)
        serialized = origin_blockchain.serialize()
        loaded_blockchain = load_from_dict(serialized)
        self.assertEqual(loaded_blockchain.head , origin_blockchain.head)
        for i in range(0 , len(loaded_blockchain.chain) - 1):
            #print(loaded_blockchain.chain[i] , origin_blockchain.chain[i] , "\n")
            self.assertEqual(loaded_blockchain.chain[i].hash , origin_blockchain.chain[i].hash)

    def test_serialization_to_json(self) -> None:
        pass

if __name__ == '__main__':
    unittest.main()