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

function download(content, fileName, contentType) {
    const a = document.createElement("a");
    const file = new Blob([content], { type: contentType });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}

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

function openVerifySignModal() {
    document.getElementById("fileInput").value = ""
    var sign_verify_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById("verificationModal"));
    sign_verify_modal.show();
}

document.getElementById("downloadSignedFileButton").addEventListener("click", function() {
    const plainText = document.getElementById('textToSign').value;
    const partyOne = document.getElementById('partyOneEmail').value;
    const partyTwo = document.getElementById('partyTwoEmail').value;
    const signature = document.getElementById('outputTextArea').value;

    const parties = [partyOne, partyTwo]

    const signedJSON = {
        payload: {
            data: plainText,
            parties: parties
        },
        signature: signature
    }

    download(JSON.stringify(signedJSON, null, 2), "signed_file.json", "text/plain");
});

document.getElementById('fileInput').addEventListener('change', (event) => {
    const file_list = event.target.files;

    if (file_list.length > 1) {
        console.log('Could not process multiple files. Upload single file');
        return;
    }

    const file = file_list[0];

    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        fileContent = reader.result;
        const verification_request = JSON.parse(fileContent);

        fetch("/verify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(verification_request)
        })
        .then(response => {
            if (response.ok) {
                return response.text();
            } else {
                response.text()
                .then(text => {
                    console.log(text);
                })
                throw new Error(`/verify: ${response.status} ${response.statusText}`);
            }
        })
        .then(response_text => {
            const result = JSON.parse(response_text);
            if (result == 0) {
                alert('The signature is valid and matches with the payload');
            } else {
                alert('The signature does not match the payload. The payload is not signed by us or is possibly tampered.');
            }
        })
        .catch(error => {
            alert('Error: ' + error);
        });
    });
    
    reader.readAsText(file);
});
