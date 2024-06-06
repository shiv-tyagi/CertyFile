from pydantic import BaseModel
from typing import Union

class PayloadToSign(BaseModel):
    data_to_sign: Union[str, None] = None
    first_party: str
    second_party: Union[str, None] = None


class SignedPayload(BaseModel):
    data_to_verify: PayloadToSign
    signature: str
