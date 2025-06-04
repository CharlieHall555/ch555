import json , hashlib , typing
import utilities.authentication as authentication
import typing

def load_snapshot_from_dict(data : typing.Dict) -> "Snapshot":
    new_snapshot = Snapshot()
    new_snapshot.blockchain_head = data.get("blockchain_head" , "0")
    new_snapshot.hash = data.get("hash" , "0")
    new_snapshot.validator_addresses = data.get("validator_addresses" , [])
    new_snapshot.election_candiates = data.get("election_candidates" , {})
    new_snapshot.lead_validator = data.get("lead_validator" , None)

    vote_tally_data : dict = data.get("vote_tally" , {})
    new_snapshot.vote_tally = {}
    
    for key , vote_tally in vote_tally_data.items():
        candidate_id = int(key)
        new_snapshot.vote_tally[candidate_id] = vote_tally

    return new_snapshot

class Snapshot:
    """This class tracks important state changes on the blockchain to avoid a node having to parse the whole blockchain"""
    lead_validator : str
    blockchain_head : str
    hash : str
    election_candiates : dict
    elector_dict : dict
    vote_tally : dict
    
    def __init__(self):
        self.validator_addresses = []
        self.lead_validator = None
        self.blockchain_head = "0"
        self.hash = "0"
        self.election_candiates = {} #abritary candiate name and candiate id
        self.elector_dict = {}
        self.vote_tally = {}

    def add_vote(self , candidate_id : int) -> None:
        current_tally = self.vote_tally.get(candidate_id , None) 
        if current_tally is None:
            self.vote_tally[candidate_id] = 1
        else:
            self.vote_tally[candidate_id] = current_tally + 1

    def get_vote_tally(self) -> typing.Dict:
        return self.vote_tally
    
    def add_candidate(self , candidate_name : str , candidate_id : int):
        self.election_candiates[candidate_id] = {
            "candidate_name" : candidate_name,
            "candidate_id" : candidate_id
        }

    def get_highest_candidate_id(self) -> int | None:
        ids : set = set()
        for each_candidate_id in self.election_candiates.keys():
            ids.add(each_candidate_id)
        if len(ids) > 0:
            return max(ids)
        else:
            return None

    def get_candidates(self) -> dict:
        return self.election_candiates
    
    def add_validator(self , node_id : str):
        self.validator_addresses.append(node_id)
        self.hash = self.calculate_snapshot_hash()

    def set_lead_validator(self , node_id : str):
        self.lead_validator = node_id
        self.hash = self.calculate_snapshot_hash()

    def to_json(self):
        return json.dumps({
            "blockchain_head" : self.blockchain_head,
            "hash" : self.hash,
            "lead_validator" : self.lead_validator,
            "validator_addresses" : self.validator_addresses,
            "election_candidates" : self.election_candiates,
            "vote_tally" : self.vote_tally
        })
    
    def is_a_validator(self , target_id : str):
        return target_id in self.validator_addresses

    def is_lead_validator(self , sender_id : str):
        if self.lead_validator is None: return False
        return sender_id == self.lead_validator

    def get_lead_validator(self) -> str:
        """returns the locally known lead validator."""
        return self.lead_validator

    def get_validators(self)-> typing.List[str]:
        return self.validator_addresses

    def calculate_snapshot_hash(self):
        data_to_hash = ""
        data_to_hash = data_to_hash + json.dumps(self.validator_addresses , sort_keys=True) + ","
        data_to_hash = data_to_hash + json.dumps(self.election_candiates , sort_keys=True) + ","
        data_to_hash = data_to_hash + self.blockchain_head + ","
        data_to_hash = data_to_hash + str(self.lead_validator or 0)
        return hashlib.sha256(data_to_hash.encode()).hexdigest()

    def reset(self):
        self.validator_addresses = []
        self.lead_validator = ()
        self.hash = "0"
    
    def add_elector(self , elector_public_key : str)-> None:
        public_key_hash = authentication.generate_sha256_hash(elector_public_key)
        
        self.elector_dict[public_key_hash] = {
            "public_key" :  elector_public_key,
            "voted" : False
        }

    def copy(self) -> "Snapshot":
        """Returns a 1 layer deep copy of snapshot, all sub attributes are shallow copied"""
        new_snapshot = Snapshot()
        new_snapshot.blockchain_head = self.blockchain_head
        new_snapshot.hash = self.hash
        new_snapshot.validator_addresses = self.validator_addresses.copy()
        new_snapshot.election_candiates = self.election_candiates.copy()
        new_snapshot.lead_validator = self.lead_validator
        new_snapshot.vote_tally = self.vote_tally.copy()
        return new_snapshot


    def is_elector_registered(self , elector_public_key : str):
        public_key_hash = authentication.generate_sha256_hash(elector_public_key)
        elector_info : typing.Dict = self.elector_dict.get(public_key_hash , None)
        if elector_info is None: 
            return False 
        else:
            return True

    def has_elector_voted(self  , elector_public_key : str ) -> typing.Optional[bool]:
        public_key_hash = authentication.generate_sha256_hash(elector_public_key)

        elector_info : typing.Dict = self.elector_dict.get(public_key_hash , None)
        if elector_info is None: return

        return elector_info.get("voted" , False)

    def set_elector_voted(self , elector_public_key : str , vote_status : bool) -> None:
        public_key_hash = authentication.generate_sha256_hash(elector_public_key)

        elector_info = self.elector_dict.get(public_key_hash , None)
        if elector_info is None: return

        elector_info["voted"] = vote_status