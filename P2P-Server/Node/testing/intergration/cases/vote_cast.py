"""Tests the server opens and closes normally, default to a pass, no need to check logs"""
import os
import sys
import logparser #ignore this error it will resolve correctly.

params = {
    "1" : { #create root node
        "port" : 8000, "bootstrap" : 1,
        "input":"""pause 2
        add_candidate "A" 1
        pause 0.5
        le
        pause 7
        quit"""
    },
    "2" : { #voting node
        "port" : 8001, "bootstrap" : 0,
        "input":"""pause 2
        connect "127.0.0.1" 8000
        pause 0.5
        lc
        pause 5
        vote 1
        quit"""
    }
}

expected_in_bootstrap_log = ["SERVER_STARTED" , "ADD_CANDIDATE" , "VOTE_COUNTED"]
expected_in_voter_log = ["SERVER_STARTED" , "ADD_CANDIDATE" ]

def test_case():
    output = {}
    output["passed"] = False

    bootstrap_log = logparser.generate_log("0.0.0.0" , "8000")
    voter_log = logparser.generate_log("0.0.0.0" , 8001)
    
    #check logs
    for each_log in bootstrap_log.entries:
        if each_log.operation in expected_in_bootstrap_log:
            expected_in_bootstrap_log.remove(each_log.operation)

    for each_log in voter_log.entries:
        if each_log.operation in expected_in_voter_log:
            expected_in_voter_log.remove(each_log.operation)

    #Verify test
    if len(expected_in_bootstrap_log) == 0 and len(expected_in_voter_log) == 0:
        output["passed"] = True
        return output
    else:
        output["passed"] = False
        output["fail_reason"] = f"Expected operations not found: Voter-Node-Log: {str(expected_in_voter_log)}, Bootstrap-Node-Log: {str(expected_in_bootstrap_log)}"

    return output