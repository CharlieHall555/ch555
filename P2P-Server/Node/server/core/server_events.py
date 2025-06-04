from PyQt5.QtCore import QObject, pyqtSignal

class ServerEvents(QObject):
    #system events 
    sys_server_error : pyqtSignal = pyqtSignal(str) # error_message
    sys_server_ready : pyqtSignal = pyqtSignal(object)

    sys_missing_local_creds_file : pyqtSignal = pyqtSignal()
    """Passed Paremeters: None | Signal fired when the local creds doesn't load because it doesn't exsist."""

    sys_new_node_id : pyqtSignal = pyqtSignal(str)
    """Passed Paremeters: new_node_id : str | Signal fired when node id is first set"""

    sys_port_taken_already : pyqtSignal = pyqtSignal(str)
    """Passed Paremeters: port : str | Signal fired when port is already taken."""

    sys_launch_failure : pyqtSignal = pyqtSignal(str)


    sys_missing_electors_file : pyqtSignal = pyqtSignal()

    sys_new_elector_creds_loaded : pyqtSignal = pyqtSignal(str , str)
    """Passed Parameters : pubkey : str , privkey : str |  Fired when new local elector creds are loaded either by file or api."""

    #network events
    net_request_connect_to_node : pyqtSignal = pyqtSignal(str , str) # host, port
    """Passed Parameters: host : str , port : str | Signal used to request a """

    net_connected_successfully_to_network : pyqtSignal = pyqtSignal()
    """Passed Parameters : None | Signal fired when the node sucessfully connects to a node of the same network as targeted, note it may not be the specific host and port specifed, """

    net_connection_failed : pyqtSignal = pyqtSignal()
    """Passed Parameters : None | Signal fired when the node could not find a successful route to join the network targeted."""

    net_connections_changed : pyqtSignal = pyqtSignal(object)
    """Passed Parameters : n_connections | Signal fired when the number of connections changes."""

    net_node_directory_changed : pyqtSignal = pyqtSignal(object)
    """Passed Parameters : new_node_directory """


    net_initial_connection_failed : pyqtSignal = pyqtSignal()
    """Passed Parameters : None | Signal fired when the node could not find a successful route to join the network targeted. and it is the initial connection"""


    net_server_started : pyqtSignal = pyqtSignal()

    #blockchain events

    blc_new_snapshot_loaded: pyqtSignal = pyqtSignal(object)

    blc_new_blockchain_loaded: pyqtSignal = pyqtSignal()

    blc_became_lead_validator : pyqtSignal = pyqtSignal()
    """Passed Parameters : None : str | Signal fired when local node becomes a validator."""

    blc_no_longer_validator : pyqtSignal = pyqtSignal()
    """Passed Parameters : None : str | Signal fired when local node is no longer the lead validator."""


    blc_own_vote_detected : pyqtSignal = pyqtSignal(str)
    """Passed Parameters : block_hash_containing_transaction : str | Signal fired when the node's is detected in the blockchain state."""

    blc_new_vote_added : pyqtSignal = pyqtSignal(object)
    """Passed Parameters : vote_tally : dict"""

    blc_candidate_added : pyqtSignal = pyqtSignal(str , int)
    """Passed Parameters : new_candidate_name : str , new_candidate_id : int | Signal fired when a candidate is added to the local blockchain."""
    
    blc_block_added : pyqtSignal = pyqtSignal(object)
    """Passed Parameters: new_serialized_block : dict | Singal fired when a new block is added to the local blockchain."""

    blc_snapshot_head_updated = pyqtSignal(str)
    """Passed Parameters: new_head : str | Signal fired when the blockchain-head is updated."""

    blc_validator_added = pyqtSignal(str)
    """Passed Parameters: new_validator_id : str | Singal fired when a new validator is added to the local blockchain."""

    blc_lead_validator_set = pyqtSignal(str)
    """Passed Parameters: new_lead_validator_id : str | Signal fired when the lead validator is changed on the local blockchain."""

    blc_became_validator : pyqtSignal = pyqtSignal()

    blc_blockchain_updated : pyqtSignal = pyqtSignal(object)
    """Passed Parameters: new_serialized_blockchain : dict | Singal fired when there is a change to the local blockchain."""

    blc_request_block : pyqtSignal = pyqtSignal()
    blc_request_full_blockchain : pyqtSignal = pyqtSignal()

    blc_get_block : pyqtSignal = pyqtSignal(object)
    blc_get_full_blockchain : pyqtSignal = pyqtSignal(object)



