document.getElementById("signForm").addEventListener("submit", function(event) {
    event.preventDefault();
    
    const plainText = document.getElementById('textToSign').value;
    const partyOne = document.getElementById('partyOneEmail').value;
    const partyTwo = document.getElementById('partyTwoEmail').value;

    const data = {
        data_to_sign: plainText,
        first_party: partyOne,
        second_party: partyTwo
    };

    fetch('/sign', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error(`${response.status} ${response.statusText}`);
        }
    })
    .then(responseText => {
        document.getElementById('outputTextArea').value = responseText.replace(/\"/g, "");
        var output_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('signatureOutputModal'));
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
