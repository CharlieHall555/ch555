from blockchain.block import Block, load_from_dict as load_block_from_dict
import json

def load_from_dict(data : dict) -> "Blockchain":
    head : str = data.get("head" , None)
    chainlist : list = data.get("chainlist" , None)
    assert(head and chainlist)

    new_blockchain = Blockchain(False)

    serialized_block : dict
    for serialized_block in chainlist:
        new_block = load_block_from_dict(serialized_block) 
        new_blockchain.add_block(new_block)
    
    return new_blockchain


class Blockchain:
    """This class the classed used to store the local blockchain."""
    genesisBlock : Block
    chain : list[Block]

    head : str
    """The blockchain head stores the hash of the most recently finalized block, this is not the same as the head of the current working block."""
    def __init__(self , includeGenesis=False):
        self.chain = []
        #genesis node
        if includeGenesis:
            genesisBlock = Block()
            genesisBlock.set_previous_hash(0)
            self.chain.append(genesisBlock)
            self.head = genesisBlock.hash

    def reset(self):
        genesisBlock = Block()
        genesisBlock.set_previous_hash(0)
        self.chain.append(genesisBlock)
        self.head = genesisBlock.hash


    def add_block(self, new_block , enforce_previous_hash=True):
        """if true enforce previous hash authomatically sets the new blocks previous hash to the latest_block of the blockchain"""
        if enforce_previous_hash and len(self.chain) > 0:
            new_block.set_previous_hash(self.get_latest_block().hash)
        new_block.hash = new_block.calculate_hash()
        self.head = new_block.hash
        self.chain.append(new_block)

    def add_genesis_block(self, new_block : Block):
        new_block.set_previous_hash(0)
        self.head = new_block.hash
        self.chain.append(new_block)

    def get_latest_block(self):
        return self.chain[-1]
          
    def pretty_print(self):
        print("Blocks".center(36 , "-"))
        print(f"Blockchain Head: {self.head} \n")
        for each in self.chain:
            print(each)
        print("-"*36)

    def serialize(self):
        output_dict = {}
        output_dict["head"] = self.head   
        chain_list = []
        for each_block in self.chain:
            chain_list.append(each_block.serialize())
        output_dict["chainlist"] = chain_list

        return output_dict

    def to_json(self):
        return json.dumps(self.serialize() , sort_keys=True)

    def __str__(self):
        print(self.head)


