import base64
import os

ENCRYPTION_KEY = base64.b64encode(os.urandom(32)).decode()

class SimpleCipher:
    def __init__(self, encryption_key):
        self.encryption_key = encryption_key

    def encrypt(self, text):
        text = text.encode()
        xor_bytes = [text[i] ^ self.encryption_key[i % len(self.encryption_key)] for i in range(len(text))]
        return base64.b64encode(bytes(xor_bytes)).decode()

    def decrypt(self, encrypted):
        xor_bytes = base64.b64decode(encrypted.encode())
        return bytes([xor_bytes[i] ^ self.encryption_key[i % len(self.encryption_key)] for i in range(len(xor_bytes))]).decode()
