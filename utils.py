from OpenSSL import crypto
from enum import Enum
import binascii
import os

class VerificationResult(Enum):
    GOOD_MATCH = 0
    BAD_MATCH = 1

def sign_data(data):
    try:
        with open(os.getenv("KEY_PEM_PATH"), "rb") as f:
            key_buff = f.read()
    except FileNotFoundError:
        print(f"key.pem file not found, path:{os.getenv("KEY_PEM_PATH")}")
        return None
    except PermissionError:
        print("key.pem file can't be opened. Permissions missing.")
        return None

    key_passphrase = os.getenv("KEY_PASS")
    if key_passphrase is not None:
        # convert to byte buffer
        key_passphrase = key_passphrase.encode('utf-8')

    try:
        sign = crypto.sign(
            crypto.load_privatekey(
                type=crypto.FILETYPE_PEM,
                buffer=key_buff,
                passphrase=key_passphrase
            ),
            data=data,
            digest="sha512"
        )
    
        sign = binascii.hexlify(sign).decode()
        return sign
    except crypto.Error as e:
        print(e)
        print("Error signing the file")
        return None


def verify(data_to_verify, sign):
    sign = binascii.unhexlify(sign.encode())
    try:
        with open(os.getenv("CERT_PEM_PATH"), "rb") as f:
            cert_buff = f.read()
    except FileNotFoundError:
        print(f"cert.pem file not found, path:{os.getenv("CERT_PEM_PATH")}")
        return None
    except PermissionError:
        print("cert.pem file can't be opened. Permissions missing.")
        return None

    try:
        crypto.verify(
            cert=crypto.load_certificate(
                type=crypto.FILETYPE_PEM,
                buffer=cert_buff
            ),
            signature=sign,
            data=data_to_verify,
            digest="sha512"
        )

        return VerificationResult.GOOD_MATCH
    except crypto.Error:
        return VerificationResult.BAD_MATCH
