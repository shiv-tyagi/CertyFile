from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import dotenv
import json
import utils
import models

dotenv.load_dotenv()

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
            200: {
                "model": str
            },
            400: {
                "model": str
            },
            500: {
                "model": str
            }
        }
)
def generate_sign(payload_to_sign: models.PayloadToSign, response: Response):
    to_sign = json.dumps(payload_to_sign.model_dump())
    sign = utils.sign_data(to_sign)

    if not sign:
        response.status_code = 500
        return "Couldn't generate signature. Internal error."

    return sign


@app.post(
    "/verify",
    response_description=f"Return {utils.VerificationResult.GOOD_MATCH.value}"
                         "if the signature is valid,"
                         f"{utils.VerificationResult.BAD_MATCH.value} otherwise",
    responses={
        200: {
            "model": utils.VerificationResult
        },
        400: {
            "model": str
        },
        500: {
            "model": str
        }
    }
)
def verify_sign(verification_pair: models.SignedPayload, response: Response):
    v_pair_dict = verification_pair.model_dump()

    # we generate 512 byte signature, we expect the same as input
    # 512 bytes = 512*2 hex chars
    if len(v_pair_dict["signature"]) != 512*2:
        response.status_code = 400
        return "Check signature string length"

    data_to_verify = json.dumps(v_pair_dict["data_to_verify"])
    result = utils.verify(data_to_verify, v_pair_dict["signature"])

    if not result:
        response.status_code = 500
        return "Couldn't verify signature. Internal error."

    return result
