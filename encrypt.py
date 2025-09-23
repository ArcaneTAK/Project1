import rsa
import json
from typing import Literal, Any, Tuple

def encrypt(data: bytes, method: Literal['rsa'], encrypt_key) -> Tuple[bytes, Any]:
    match method:
        case 'rsa':
            # https://en.wikipedia.org/wiki/RSA_cryptosystem
            if type(encrypt_key) is not rsa.PublicKey:
                encrypt_key, decrypt_key = rsa.newkeys(128)
            return (rsa.encrypt(data, encrypt_key), decrypt_key)
        case _:
            raise SyntaxError("Unsupported")
    
def decrypt(data: bytes, method: Literal['rsa'], decrypt_key):
    match method:
        case 'rsa':
            if type(decrypt_key) is not rsa.PrivateKey:
                raise SyntaxError("Missing Key")
            return rsa.decrypt(data, decrypt_key)
        case _:
            raise SyntaxError("Unsupported")