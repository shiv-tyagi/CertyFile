from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone, timedelta
import dotenv
import json
import utils
import models
import jwt
import os

dotenv.load_dotenv()
secret = os.urandom(32).hex()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post(
        "/sign",
        response_description="Return signature for the input data in hex",
        responses={
            status.HTTP_200_OK: {
                "model": str
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": str
            },
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": str
            }
        }
)
def generate_sign(signature_request: models.SignatureRequest, response: Response):
    to_sign = signature_request.payload.model_dump()

    try:
        token_payload = jwt.decode(signature_request.auth_token, key=secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Token expired! Try again!"
    except jwt.DecodeError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Invalid token! Try again!"
    print(type(token_payload))


    if not utils.validate_parties_in_token(token_payload, to_sign):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Auth token was generated for different parties. Provide Valid Token"

    sign = utils.sign_data(json.dumps(to_sign))

    if not sign:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return "Couldn't generate signature. Internal error."

    return sign


@app.post(
    "/verify",
    response_description=f"Return {utils.VerificationResult.GOOD_MATCH.value}"
                         "if the signature is valid,"
                         f"{utils.VerificationResult.BAD_MATCH.value}"
                         "otherwise",
    responses={
        status.HTTP_200_OK: {
            "model": utils.VerificationResult
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": str
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": str
        }
    }
)
def verify_sign(verification_request: models.VerificationRequest, response: Response):
    # we generate 512 byte signature, we expect the same as input
    # 512 bytes = 512*2 hex chars
    if len(verification_request.signature) != 512*2:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "Check signature string length"

    data_to_verify = json.dumps(verification_request.payload.model_dump())
    result = utils.verify(data_to_verify, verification_request.signature)

    if not result:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return "Couldn't verify signature. Internal error."

    return result


@app.post(
    "/auth_token"
)
def auth_token(token_request: models.TokenRequest, response: Response):
    token = jwt.encode({"parties": token_request.parties.model_dump(), "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=3)}, key=secret, algorithm="HS256")
    return token
