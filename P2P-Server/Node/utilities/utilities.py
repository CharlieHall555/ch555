import re
import socket

IP_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

def is_valid_ip(ip: str) -> bool:
    if not IP_REGEX.match(ip):
        return False
    return all(0 <= int(part) <= 255 for part in ip.split("."))

def is_valid_port(port: str) -> bool:
    return port.isdigit() and 0 < int(port) <= 65535

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def get_local_ipv4():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip