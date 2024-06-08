from pydantic import BaseModel
from typing import Union

class Parties(BaseModel):
    one: str
    two: Union[str, None] = None

class Payload(BaseModel):
    data: Union[str, None] = None
    parties: list[str]

class SignatureRequest(BaseModel):
    payload:Payload
    auth_tokens: list[str]

class VerificationRequest(BaseModel):
    payload: Payload
    signature: str

class OTPVerificationRequest(BaseModel):
    email: str
    otp: str

class OTPRequest(BaseModel):
    email: str
