"""This is an independent python script used to generate an electors file for the given number of electors"""

#standard lib imports
import os
import sys
import time
import typing
import json
import random

# Cryptography imports
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import utilities.authentication as auth

output_dict : dict[str , dict] = {}
n = 1



password = b"strong_password"

def generate_elector(i):
    each = {}
    password = str(random.randint(1000 , 9999))
    private_key , public_key = auth.generate_ecdsa_key_pair()
    private_key_str = auth.compress_ecdsa_key(private_key)
    public_key_str = auth.compress_ecdsa_key(public_key)
    password_private_key = auth.compress_ecdsa_private_key_encrypted(private_key , password )

    each["elector_id"] = public_key_str[:4].lower()
    each["public_key"] = public_key_str
    each["private_key"] = private_key_str

    output_dict[i] = each



def override_message():
    print("[WARN] electors.txt already exists in current directory")
    print("Do you wish to overide [Y/n]")   
    choice = input()
    choice = choice.strip()
    choice = choice.lower()
    if choice != "y": 
        print("closing program...")
        time.sleep(1)
        sys.exit(0)
    print("please confirm choice [Y/n]")
    choice = input()
    choice = choice.strip()
    choice = choice.lower()
    if choice != "y": 
        print("closing program...")
        time.sleep(1)
        sys.exit(0)

def get_file():
    if os.path.exists("electors.json"):
        override_message()
    else:
        print("[Info] Electors.txt does not exist creating...")

    
    file = open("electors.json" , "w")
    return file

def main():

    file = get_file()

    number = None
    while number is None or (str.isdigit(number) == False):
        print("Please enter number of electors to generate")
        number = input()
        number = number.strip()
    
    n = int(number)
    print(f"Generating {n} electors")

    for i in range(0 , n):
        generate_elector(i)

    json.dump(output_dict, file, indent=4)
    file.close()
    print("Program completed.")
    input()


if __name__ == "__main__":
    main()