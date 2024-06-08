from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import dotenv
import json
import utils
import models
import os
import otp

dotenv.load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

otp_manager = otp.OTPManager(
    redis_host=os.getenv("REDIS_HOST"),
    redis_port=os.getenv("REDIS_PORT"),
    otp_attempts_limit_email=2,
    otp_rate_limit_window_email=50
)

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
    for party in signature_request.payload.parties:
        if not utils.validate_email(party):
                response.status_code = status.HTTP_400_BAD_REQUEST
                return f"{party} is not a valid email address"

    try:
        utils.validate_tokens(
            tokens=signature_request.auth_tokens,
            parties=signature_request.payload.parties
        )
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return str(e)

    to_sign = signature_request.payload.model_dump()
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
    "/send_otp"
)
def send_otp(otp_request: models.OTPRequest, response: Response):
    try:
        otp_manager.generate_otp(otp_request.email)
    except otp.OTPLimitExceededException as e:
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return e
    
    return "OTP Sent Successfully"


@app.post(
    "/verify_otp"
)
def verify_otp(otp_verification_request: models.OTPVerificationRequest, response: Response):
    if not utils.validate_email(otp_verification_request.email):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "Invalid email"

    if not otp_manager.verify_otp(
        otp=otp_verification_request.otp,
        email=otp_verification_request.email
    ):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Invalid OTP"

    token = utils.generate_token(email=otp_verification_request.email)
    return token
