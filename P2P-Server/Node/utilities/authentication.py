from __future__ import annotations  # Type checking

# Standard library imports
import base64
import os
import traceback
import typing
from hashlib import sha256

# Type checking imports
from typing import TYPE_CHECKING

# Cryptography imports
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey , RSAPublicKey


def encrypt_with_public_key_rsa(public_key_str: str, message_str: str) -> str:
    """Takes a public key as a string and a message string and returns the matching encrypted string."""
    public_key_bytes = public_key_str.encode("utf-8")
    public_key = serialization.load_pem_public_key(public_key_bytes)
    aes_key = os.urandom(32)
    iv = os.urandom(12)  # AES-GCM standard IV size is 12 bytes
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message_str.encode()) + encryptor.finalize()
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    encrypted_package = base64.b64encode(
        iv + encryptor.tag + ciphertext + encrypted_aes_key
    ).decode()
    return encrypted_package


def decrypt_with_private_key_rsa(private_key_str: str, encrypted_package: str):
    """Takes a private key as a string and an encrypted string and attempts to decrypt it"""
    private_key_bytes = private_key_str.encode("utf-8")
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    encrypted_data = base64.b64decode(encrypted_package)
    iv = encrypted_data[:12]
    tag = encrypted_data[12:28]
    encrypted_aes_key = encrypted_data[-256:]
    ciphertext = encrypted_data[28:-256]
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext.decode()

def generate_node_id(public_key : rsa.RSAPublicKey):
    public_key_str = serialize_public_key(public_key)
    output = generate_sha256_hash(public_key_str)[:16]
    return output

def generate_signature_ecdsa(private_key: Ed25519PrivateKey, message: str) -> str:
    try:
        bytes = message.encode('utf-8')
        signature = private_key.sign(bytes)
        return base64.b64encode(signature).decode('utf-8')
    except:
        print("something when wrong generating signature for ecdsa key.")
        return ""

def verify_signature_ecdsa(public_key: Ed25519PublicKey, message: str, signature_b64: str) -> bool:
    message_bytes = message.encode('utf-8')
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(signature, message_bytes)
        return True
    except Exception:
        return False

def generate_sha256_hash(data: str) -> str:
    "Takes data as a string and returns the matching sha256 hash."
    encoded_data = data.encode("utf-8")
    hash_object = sha256(encoded_data)
    hash_hex = hash_object.hexdigest()
    return hash_hex

def generate_ecdsa_key_pair() -> tuple[Ed25519PrivateKey , Ed25519PublicKey]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key , public_key

def compress_ecdsa_private_key_encrypted(key : Ed25519PrivateKey , password: str) -> str:
    encrypted_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )
    return base64.b64encode(encrypted_bytes).decode("utf-8")

def compress_ecdsa_key(key: Ed25519PrivateKey | Ed25519PublicKey) -> str:
    if isinstance(key, Ed25519PrivateKey):
        key_bytes = key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
    elif isinstance(key, Ed25519PublicKey):
        key_bytes = key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    else:
        raise TypeError("Key must be Ed25519PrivateKey or Ed25519PublicKey")

    return base64.b64encode(key_bytes).decode('utf-8')

def decompress_ecdsa_key(b64_key: str, is_private: bool) -> Ed25519PrivateKey | Ed25519PublicKey:
    key_bytes = base64.b64decode(b64_key)

    if is_private:
        return Ed25519PrivateKey.from_private_bytes(key_bytes)
    else:
        return Ed25519PublicKey.from_public_bytes(key_bytes)

def generate_rsa_key_pair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    "Generates an rsa key pair"
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key : rsa.RSAPublicKey) -> str:
    "Takes a rsa public key and converts into a readable string"
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    key_content = public_key_pem.decode("utf-8")
    return key_content

def load_rsa_private_key(pem_key_str: str):
    """convert a PEM private key string into an RSA private key."""
    try:
        private_key = serialization.load_pem_private_key(
            pem_key_str.encode(),  # Convert string to bytes
            password=None,  # Set password if the key is encrypted
            backend=default_backend()
        )
        return private_key
    except:
        print("Failed to load RSA private key.")

def generate_signature_str_rsa(private_key : rsa.RSAPrivateKey, message_string: str) -> str:
    "takes a private key as an rsa private key and a message string and returns the sigature as a string"
    message_bytes = message_string.encode("utf-8")  # Convert to bytes
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_signature_rsa(public_key_str : str, message_str : str, signature_str : str) -> bool:
    """Verifies the message_str was signed with the given signature matching the public key"""
    try:
        message_str = message_str.strip(" ")
        public_key_bytes : bytes = public_key_str.encode("utf-8")
        public_key : rsa.RSAPublicKey = serialization.load_pem_public_key(public_key_bytes)
        message_bytes = message_str.encode("utf-8")
        signature_bytes = base64.b64decode(signature_str)
        public_key.verify(
            signature_bytes,
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
