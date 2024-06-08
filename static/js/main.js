document.getElementById("signForm").addEventListener("submit", function(event) {
    event.preventDefault();

    document.getElementById("partyOneOTP").setAttribute("placeholder", "OTP for " + document.getElementById("partyOneEmail").value);
    document.getElementById("partyTwoOTP").setAttribute("placeholder", "OTP for " + document.getElementById("partyTwoEmail").value);
    var otp_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById("otpModal"));
    otp_modal.show();
});

document.getElementById("generateSignButton").addEventListener("click", function(event) {
    const plainText = document.getElementById('textToSign').value;
    const partyOne = document.getElementById('partyOneEmail').value;
    const partyTwo = document.getElementById('partyTwoEmail').value;

    const parties = {
        one: partyOne,
        two: partyTwo
    }

    const token_request = {
        parties: parties,
    };

    fetch("/auth_token", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(token_request)
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error(`/auth_token: ${response.status} ${response.statusText}`);
        }
    })
    .then(token => {
        const signature_request = {
            payload: {
                parties: parties,
                data: plainText
            },
            auth_token: JSON.parse(token)
        }

        return fetch("/sign", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(signature_request)
        });
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error(`/sign: ${response.status} ${response.statusText}`);
        }
    })
    .then(signature => {
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
