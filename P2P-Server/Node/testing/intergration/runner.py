# standard lib imports
import subprocess
import time
import os
import typing
import io
import argparse

from cases.server_creation_test import test_case as server_creation_test, params as server_creation_test_params
from cases.vote_cast import test_case as vote_cast_test, params as vote_cast_params
from cases.validator_creation import test_case as validator_creation_test, params as validator_creation_params
from cases.validator_reassignment_test import test_case as validator_reassignment_test, params as validator_reassignment_params

testcases = [
    ("server_creation" , server_creation_test, server_creation_test_params),
    ("vote_casting" , vote_cast_test , vote_cast_params),
    ("validator_creation" , validator_creation_test , validator_creation_params),
    ("validator_reassignment" , validator_reassignment_test , validator_reassignment_params)
]

reports = []

running_nodes = []

max_run_time = 30  # seconds

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.join(current_dir , "..", "..")
logs_dir = os.path.join("logs")
input_dir = os.path.join("input_scripts")

print(project_root_dir)

scripts_dir = os.path.join("scripts")

def clean_logs() -> None:
    if os.path.isdir(logs_dir):
        for filename in os.listdir(logs_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(logs_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

def clean_inputs() -> None:
    if os.path.isdir(input_dir):
        for filename in os.listdir(input_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(input_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

def launch_node(port: int, input_str : str, bootstrap: int = 0 , node_id = None):
    try:    
        # Create a unique file for each node input
        input_filename = os.path.join("input_scripts", f"node_input_{port}.txt")
        os.makedirs("input_scripts", exist_ok=True)

        with open(input_filename, "w", encoding="utf-8") as f:
            f.write(input_str)

        # Open the file for reading and pass it as stdin
        input_file = open(input_filename, "r", encoding="utf-8")

        args = [
            "python", os.path.join(project_root_dir, "main.py"),
            "--terminal-mode", "1",
            "--port", str(port),
            "--bootstrap", str(int(bootstrap)),             
        ]

        if node_id:
            args.append("--node-id")
            args.append(node_id)

        proc = subprocess.Popen(
            args,
            stdin=input_file,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        running_nodes.append(proc)
        return proc
    except Exception as e:
        print(f"[ERROR] Failed to launch node on port {port}: {e}")
        return None

def shutdown_nodes():
    for proc in running_nodes:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"[WARN] Force-killing unresponsive node (PID={proc.pid} , ARGS={proc.args})")
            proc.kill()

        if proc.returncode not in (0, None):
            stderr = proc.stderr.read().encode()
            print(f"[ERROR] Node (PID={proc.pid} , ARGS={proc.args}) exited with code {proc.returncode}:\n{stderr}")


def run_test_case(test_case : typing.Tuple[str , typing.Callable , typing.Dict]) -> None:
    try:
        #Setup
        test_case_name = test_case[0]
        test_case_function = test_case[1]
        test_case_params = test_case[2]
        clean_logs()
        clean_inputs()
        time.sleep(1)
        #Launch Nodes
        for each_node_data in test_case_params.values():
            port_value = each_node_data.get("port")
            bootstrap_value = each_node_data.get("bootstrap")
            input_value = each_node_data.get("input")
            node_id = each_node_data.get("node-id" , None)
            launch_node(port_value , input_value , bootstrap_value , node_id)

        start_time = time.time()
        all_done = True
        print(f"Running {test_case_name}...")

        for proc in running_nodes:
            try:
                proc.wait(timeout=max(0, max_run_time - (time.time() - start_time)))
            except subprocess.TimeoutExpired:
                print(f"[TIMEOUT] Node PID {proc.pid} did not exit in time.")
                all_done = False
                break

        if not all_done:
            shutdown_nodes()
            print("[FAILSAFE] Nodes were forcefully shut down due to timeout.")
            reports.append(
                {"test_name" : test_case_name, "result" : "failed" , "reason" : "exceeded_max_run_time"}
            )
        else:
            time.sleep(5)
            print(f"Loading logs for {test_case_name}...")
            output = test_case_function()

            passed = output.get("passed" , False)
            fail_reason = output.get("fail_reason" , "None")

            if passed:
                reports.append(
                    {"test_name" : test_case_name, "result" : "passed"}
                )
            else:
                reports.append(
                    {"test_name" : test_case_name, "result" : "failed", "reason" : fail_reason}
                )

            print(f"Finished {test_case_name}, Passed: {passed}.")

    except Exception as e:
        print(f"Error running test case: {e}")
        import traceback
        traceback.print_exc()

# Example usage
def main():
    parser = argparse.ArgumentParser(description="Intergration Test Runner")
    parser.add_argument("--test-name" , type=str, default=None , help="Optional argument to indicate a specific test to run, if not indicated all tests will run.")
    args = parser.parse_args()
    test_name = args.test_name

    if test_name:
        for each_test_case in testcases:
            test_case_name = each_test_case[0]
            if test_case_name == test_name:
                run_test_case(each_test_case)
                return
        print("Couldn't find test case.")
    else:
        for each_test_case in testcases:
            run_test_case(each_test_case)
   

def show_report():
    print("REPORT".center(36 , "-"))
    for each_report in reports:
        output = f"Case: {each_report.get("test_name")}, Result: {each_report.get("result")}, Reason: {each_report.get("reason" , "N/A")}"
        print(output)

if __name__ == "__main__":
    main()
    show_report()
    print("Program finished.")