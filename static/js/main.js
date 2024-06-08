var timeouts = {}
var auth_tokens = []

document.getElementById("signForm").addEventListener("submit", function(event) {
    event.preventDefault();
    document.getElementById("partyOneOTP").setAttribute("placeholder", "OTP for " + document.getElementById("partyOneEmail").value);
    document.getElementById("partyTwoOTP").setAttribute("placeholder", "OTP for " + document.getElementById("partyTwoEmail").value);
    sendOTP("partyOne");
    sendOTP("partyTwo");
    document.getElementById("generateSignButton").disabled = true;
    auth_tokens = [];
    var otp_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById("otpModal"));
    otp_modal.show();
});

document.getElementById("generateSignButton").addEventListener("click", function(event) {
    const plainText = document.getElementById('textToSign').value;
    const partyOne = document.getElementById('partyOneEmail').value;
    const partyTwo = document.getElementById('partyTwoEmail').value;

    const parties = [partyOne, partyTwo]

    const signature_request = {
        payload: {
            data: plainText,
            parties: parties
        },
        auth_tokens: auth_tokens
    }

    fetch("/sign", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(signature_request)
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            response.text()
            .then(text => {
                console.log(text);
            })
            throw new Error(`/sign: ${response.status} ${response.statusText}`);
        }
    })
    .then(signature => {
        var otp_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById("otpModal"));
        otp_modal.hide();

        document.getElementById('outputTextArea').value = JSON.parse(signature);
        var output_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById("signatureOutputModal"));
        output_modal.show();
    })
    .catch(error => {
        alert('Error: ' + error);
    });
});

document.getElementById("copySignatureButton").addEventListener("click", function(event) {
    var text_element = document.getElementById("outputTextArea");
    text_element.select();
    navigator.clipboard.writeText(text_element.value);
    alert("Copied the signature hex to clipboard");
});

function sendOTP(party_prefix) {
    let email_element_id = party_prefix + "Email";
    let email = document.getElementById(email_element_id).value;

    const otp_request = {
        email: email
    }

    fetch("/send_otp", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(otp_request)
    })
    .then(response => {
        if (response.ok) {
            let otp_field_id = party_prefix + "OTP";
            document.getElementById(otp_field_id).disabled = false;
            document.getElementById(otp_field_id).value = "";

            let reset_button_id = party_prefix + "ResendButton";
            document.getElementById(reset_button_id).style.display = "block";
            document.getElementById(reset_button_id).disabled = true;

            let verify_button_id = party_prefix + "VerifyButton";
            let verify_button_element = document.getElementById(verify_button_id);
            verify_button_element.setAttribute("class", "btn btn-outline-primary");
            verify_button_element.disabled = false;
            verify_button_element.innerHTML = "Verify";

            let prev_timeout = timeouts[party_prefix + "_reset_disabled_timeout"];

            if (prev_timeout) {
                clearTimeout(prev_timeout);
            }

            timeouts[party_prefix + "_reset_disabled_timeout"] = setTimeout((reset_button_id) => {
                document.getElementById(reset_button_id).removeAttribute("disabled");
            }, 30000, reset_button_id);

            return response.text();
        } else {
            throw new Error(`/send_otp: ${response.status} ${response.statusText}`);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}

function update_generate_button_state() {
    if (auth_tokens.length >= 2) {
        document.getElementById("generateSignButton").disabled = false;
    }
}

function verifyOTP(party_prefix) {
    let email_element_id = party_prefix + "Email";
    let otp_element_id = party_prefix + "OTP";

    let email = document.getElementById(email_element_id).value;
    let otp = document.getElementById(otp_element_id).value;

    const otp_verification_request = {
        email: email,
        otp: otp
    }

    fetch("/verify_otp", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(otp_verification_request)
    })
    .then(response => {
        if (response.ok) {
            let otp_field_id = party_prefix + "OTP";
            document.getElementById(otp_field_id).disabled = true;

            let reset_button_id = party_prefix + "ResendButton";
            document.getElementById(reset_button_id).style.display = "none";

            let verify_button_id = party_prefix + "VerifyButton";
            let verify_button_element = document.getElementById(verify_button_id);
            verify_button_element.setAttribute("class", "btn btn-success");
            verify_button_element.disabled = true;
            verify_button_element.innerHTML = "Verified";

            return response.text();
        } else {
            throw new Error(`/verify_otp: ${response.status} ${response.statusText}`);
        }
    })
    .then(token => {
        auth_tokens.push(JSON.parse(token));
        update_generate_button_state();
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}
