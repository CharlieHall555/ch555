import typing
import os
import sys
import re
import datetime

project_root_dir = os.path.join(os.path.dirname(__file__) , ".." , "..")

class LogEntry:
    timestamp : float
    operation : str
    tag : str
    data : tuple
    def __init__(self , timestamp , tag , operation , data):
        self.timestamp = timestamp
        self.operation = operation
        self.tag = tag
        self.data = data

class Log:
    entries : typing.List[LogEntry]
    def __init__(self):
        self.entries = []
    def append(self , next_entry : LogEntry)->None:
        self.entries.append(next_entry)

def parse_log_line(log_line : str) -> LogEntry | None:
    pattern = r"\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(?P<tag>\w+)\] (?P<log_event>.*?)(\((?P<params>.*)\))?$"
    match = re.match(pattern, log_line)

    if match:
        timestamp_str = match.group("timestamp")
        tag = match.group("tag")
        log_event = match.group("log_event").strip()
        params_str = match.group("params")

        try:
            timestamp_datetime = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamp_float = timestamp_datetime.timestamp()
        except ValueError:
            return None

        if params_str:
            # Parse parameters string into a tuple.
            params = tuple(param.strip() for param in params_str.split(","))
        else:
            params = tuple()

        return LogEntry(timestamp_float , tag , log_event, params)
    else:
        return None

def process_line(line : str)-> str:
    line = line.rstrip("\n")
    line = line.strip(" ")
    return line

def generate_log(host , port)-> Log | None:
    new_log = Log() #root dir should be the project root dir, <this allow the module to access the logs folder.

    target_file = f"{host}_{port}_log.txt"
    target_file = os.path.join(os.path.dirname(__file__) , "logs" , target_file)
    try:
        if os.path.isfile(target_file) is None: raise FileNotFoundError
        log_file = open(target_file , "r")

        each_line : str 
        for each_line in log_file:
             each_line = process_line(each_line)
             log_entry = parse_log_line(each_line)
             if log_entry is None: continue
             new_log.append(log_entry)

    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(f"Error generating logs, {e}")

    return new_log