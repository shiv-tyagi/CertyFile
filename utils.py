from OpenSSL import crypto
from enum import Enum
import binascii
import os
import re
import jwt
from datetime import datetime, timezone, timedelta

secret = os.urandom(32).hex()

class VerificationResult(Enum):
    GOOD_MATCH = 0
    BAD_MATCH = 1


def sign_data(data: str):
    try:
        with open(os.getenv("KEY_PEM_PATH"), "rb") as f:
            key_buff = f.read()
    except FileNotFoundError:
        print(f"key.pem file not found, path:{os.getenv('KEY_PEM_PATH')}")
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


def verify(data_to_verify: str, sign: str):
    sign = binascii.unhexlify(sign.encode())
    try:
        with open(os.getenv("CERT_PEM_PATH"), "rb") as f:
            cert_buff = f.read()
    except FileNotFoundError:
        print(f"cert.pem file not found, path:{os.getenv('CERT_PEM_PATH')}")
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


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if(re.fullmatch(regex, email)):
        return True
    
    return False


def generate_token(email: str):
    return jwt.encode(
        payload={"email": email, "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=3)},
        key=secret,
        algorithm="HS256"
    )

def validate_tokens(tokens: list[str], parties: list[str]):
    parties_valid_tokens = set()
    all_parties = set(parties)

    invalid_token_count = 0
    expired_token_count = 0
    
    for token in tokens:
        try:
            token_payload = jwt.decode(token, key=secret, algorithms=["HS256"])
            parties_valid_tokens.add(token_payload["email"])
        except jwt.ExpiredSignatureError:
            expired_token_count += 1
        except jwt.DecodeError:
            invalid_token_count += 1

    parties_token_missing = all_parties - parties_valid_tokens
    if len(parties_token_missing) > 0:
        message = "Token validation failed \n\n" \
                  "Validation failed for:\n" \
                  f"{str(parties_token_missing)} \n\n" \
                  f"Invalid token count: {invalid_token_count}\n" \
                  f"Expired token count: {expired_token_count}\n"

        raise Exception(message)
