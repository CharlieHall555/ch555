import os
import unittest
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(project_root_dir)

import utilities.authentication as auth
from utilities.authentication import Ed25519PrivateKey , Ed25519PublicKey , serialization

class TestAuth(unittest.TestCase):
    def test_signature_ecdsa(self) -> None:
        private_key, public_key = auth.generate_ecdsa_key_pair()
        test_message : str = "This is a test message."
        signature = auth.generate_signature_ecdsa(private_key , test_message)
        self.assertGreater(len(signature) , 0)
        verified = auth.verify_signature_ecdsa(public_key , test_message , signature)
        self.assertTrue(verified)

    def test_edsca_compression(self) -> None:
        private_key, public_key = auth.generate_ecdsa_key_pair()  # should return Ed25519PrivateKey and Ed25519PublicKey
        self.assertIsInstance(private_key, Ed25519PrivateKey)

        compressed = auth.compress_ecdsa_key(private_key)
        decompressed : Ed25519PrivateKey = auth.decompress_ecdsa_key(compressed, is_private=True) #type: ignore
        self.assertIsInstance(decompressed, Ed25519PrivateKey)

        self.assertEqual(
            private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            ),
            decompressed.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            ),
            "Decompressed private key does not match original"
        )

if __name__ == '__main__':
    unittest.main()