"""Tests the server opens and closes normally, default to a pass, no need to check logs"""
import os
import sys
import logparser

params = {
    "1" : {
        "port" : 8000, "bootstrap" : 1,
        "input":"""pause 10
        quit"""
    },
    2 : {
        "port" : 8001, "bootstrap" : 0,
        "input":"""pause 2
        connect "127.0.0.1" 8001
        pause 8
        quit"""
    }
}

expected_operations_in_logs = ["SERVER_STARTED"]

def test_case():
    output = {}
    output["passed"] = False

    log_8000 = logparser.generate_log("0.0.0.0" , "8000")
    
    for each_log in log_8000.entries:
        if each_log.operation in expected_operations_in_logs:
            expected_operations_in_logs.remove(each_log.operation)

    if len(expected_operations_in_logs) == 0:
        output["passed"] = True
        return output
    else:
        output["passed"] = False
        output["fail_reason"] = f"Expected operations not found: {str(expected_operations_in_logs)}"

    return output