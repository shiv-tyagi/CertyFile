from pydantic import BaseModel
from typing import Union

class Parties(BaseModel):
    one: str
    two: Union[str, None] = None

class Payload(BaseModel):
    data: Union[str, None] = None
    parties: Parties

class SignatureRequest(BaseModel):
    payload:Payload
    auth_token: str

class SignedPayload(BaseModel):
    payload_to_verify: Payload
    signature: str

class TokenRequest(BaseModel):
    parties: Parties
