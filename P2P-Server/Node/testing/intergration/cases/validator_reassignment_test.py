"""Tests the server opens and closes normally, default to a pass, no need to check logs"""
import os
import sys
import logparser

params = {
    "1" : {
        "port" : 8000, "bootstrap" : 1, "node-id" : "A",
        "input":"""pause 5 
        add_validator B
        pause 5
        quit"""
    },
    2 : {
        "port" : 8001, "bootstrap" : 0, "node-id" : "B",
        "input":"""pause 2
        connect "127.0.0.1" 8000
        pause 30
        quit"""
    },
    3 : {
        "port" : 8002, "bootstrap" : 0, "node-id" : "C",
        "input":"""pause 2
        connect "127.0.0.1" 8000
        connect "127.0.0.1" 8001
        pause 30
        quit"""
    }
}

expected_operations_in_log_A = ["SERVER_STARTED" ,  ]
expected_operations_in_log_B = ["SERVER_STARTED" , "NODE_BECAME_VALIDATOR" , "SELF_BECAME_LEAD_VALIDATOR" , "LEAD_VALIDATOR_CHANGED_ON_LOCAL_SNAPSHOT"]
expected_operations_in_log_C = ["SERVER_STARTED" , "LEAD_VALIDATOR_CHANGED_ON_LOCAL_SNAPSHOT" , "VALIDATOR_ADDED_TO_LOCAL_SNAPSHOT"]

def test_case():
    output = {}
    output["passed"] = False

    log_A = logparser.generate_log("0.0.0.0" , "8000")
    log_B = logparser.generate_log("0.0.0.0" , "8001")
    log_C = logparser.generate_log("0.0.0.0" , "8000")
    
    for each_entry in log_A.entries:
        if each_entry.operation in expected_operations_in_log_A:
            expected_operations_in_log_A.remove(each_entry.operation)

    for each_entry in log_B.entries:
        if each_entry.operation in expected_operations_in_log_B:
            expected_operations_in_log_B.remove(each_entry.operation)

    for each_entry in log_C.entries:
        if each_entry.operation in expected_operations_in_log_C:
            expected_operations_in_log_C.remove(each_entry.operation)

    

    if len(expected_operations_in_log_A) == 0 and len(expected_operations_in_log_B) == 0 and len(expected_operations_in_log_C) == 0:
        output["passed"] = True
        return output
    else:
        output["passed"] = False
        output["fail_reason"] = f"""Expected operations not found: 
            Node_A : {str(expected_operations_in_log_A)},
            Node_B : {str(expected_operations_in_log_B)},
            Node_C : {str(expected_operations_in_log_C)},
        """

    return output