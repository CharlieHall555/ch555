import time

import subprocess
import sys
import time
import os


def send_command(process, command, expect_output=False):
    """Send a command to the process and optionally read output"""

    if process.poll() is not None:
        print("Process exited early:", process.returncode)
        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return

    process.stdin.write(command)
    process.stdin.flush()
    
    # Allow time for the command to be processed
    time.sleep(1)
    print("hi")

    if expect_output:
        # Read available output but avoid blocking if the process exits
        output = process.stdout.read(1024)  # Capture up to 1024 bytes
        return output
    return None

def check_log_for_entry(log_file, keyword):
    """Check if a specific keyword exists in the log file"""
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found!")
        return False

    with open(log_file, "r") as file:
        logs = file.readlines()

    for line in logs:
        if keyword in line:
            return True
    return False