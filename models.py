from pydantic import BaseModel
from typing import Union

class Parties(BaseModel):
    one: str
    two: Union[str, None] = None

class Payload(BaseModel):
    data: Union[str, None] = None
    parties: Parties

class SignedPayload(BaseModel):
    payload_to_verify: Payload
    signature: str
