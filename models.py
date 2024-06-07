from pydantic import BaseModel
from typing import Union

class Parties(BaseModel):
    one: str
    two: Union[str, None] = None

class PayloadToSign(BaseModel):
    data_to_sign: Union[str, None] = None
    parties: Parties

class SignedPayload(BaseModel):
    data_to_verify: PayloadToSign
    signature: str
