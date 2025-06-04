import datetime
import queue
import copy
import os
import traceback
import sys


from testing.intergration.logevents import LOG_EVENTS

LoggingTags = {"error": "[ERROR]", "warn": "[WARN]", "info": "[INFO]" , "message" : "[TEXT-MESSAGE]"}

class Logger:
    debug_mode : bool
    filename : str
    printmode : bool
    log_cache : queue.Queue
    """Logger class used to store debug info to file and in some cases print to screen, will generate a log file."""
    def __init__(self, filename:str, printmode:bool=True):
        os.makedirs("logs", exist_ok=True)  # Create 'logs' if it doesn't exist
        self.debug_mode = False
        self.filename = os.path.join("logs", filename)
        self.printmode = printmode
        self.log_cache = queue.Queue()
        try:
            file = open(self.filename, "a")
            file.write("\n----------RESTART----------\n")
            file.close()
        except:
            print("[ERROR] logger failed writing to file")
            if self.debug_mode:
                sys.exit(1)
            

    def Log(self, text : str, tag:str="info", PrintOveride:bool=False) -> None:
        """Logs the given input string, depending on associated tag may print aswell."""
        if tag in LoggingTags == False:
            print("[ERROR] {tag} is not a valid logging tag.")
        try:
            file = open(self.filename, "a")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if (
                (self.printmode and PrintOveride == True)
                or PrintOveride
                or tag == "error"
                or tag == "message"
                or tag == "warn"
            ):
                print(f"[{timestamp}] {LoggingTags[tag]} {text}")
            self.log_cache.put(f"[{timestamp}] {LoggingTags[tag]} {text}")
            file.write(f"[{timestamp}] {LoggingTags[tag]} {text}\n")
            file.close()

            if self.debug_mode:
                sys.exit(1)

        except:
            print("[ERROR] logger failed writing to file")
            traceback.print_exc()

    def display_logs(self, n:int=10) -> None:
        """Displays the most recent n entries in the log."""
        print("Logs".center(36, "-"))
        log_copy = copy.copy(self.log_cache)
        print(log_copy.qsize())
        for i in range(1, n + 1):
            if log_copy.empty():
                return
            item = log_copy.get()
            print(item)
        print("-")
