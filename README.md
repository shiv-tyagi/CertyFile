# CertyFile

This project demonstrates the use of digital signatures to verify agreements and declarations made by individuals. Users can visit the site, make a declaration, and have it certified by the backend using our cryptographic keys. In the future, anyone can verify these declarations using the provided signature and text.

## Getting Started

### Prerequisites

- Python 3.x
- OpenSSL
- FastAPI

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/shiv-tyagi/CertyFile.git
   cd CertyFile
   ```

2. **Create a virtual environment:**

   ```sh
   python -m venv .
   ```

3. **Activate the virtual environment:**

   - On Windows:
     ```sh
     .\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source bin/activate
     ```

4. **Install the required packages:**

   ```sh
   python -m pip install -r requirements.txt
   ```

### Generating Certificates and Keys

1. **Install OpenSSL** if not already installed. Follow the instructions [here](https://www.openssl.org/source/).

2. **Generate a certificate and private key pair:**

   ```sh
   openssl req -x509 -newkey rsa:4096 -keyout <key-file-name>.pem -out <cert-file-name>.pem -sha256 -days <days-to-expiry>
   ```

   - Follow the interactive prompts to fill in the required information.
   - Secure the private key with a passphrase for enhanced security.
   - Keep these files safe and never share the private key.

3. **Store the certificate and key files:**

   By default, store these files in `project-root-dir/cert`.

### Configuration

1. **Create a `.env` file** in the project root directory with the following content:

   ```env
   KEY_PEM_PATH=cert/key.pem
   CERT_PEM_PATH=cert/cert.pem
   KEY_PASS=some-strong-password
   ```

   - Replace `KEY_PEM_PATH` and `CERT_PEM_PATH` with the paths to your key and certificate files.
   - Set `KEY_PASS` to the passphrase you used when generating the key.

### Running the Server

1. **Run the FastAPI server:**

   ```sh
   fastapi run main.py
   ```

2. **Access the application:**

   - Homepage: [http://127.0.0.1/](http://127.0.0.1/)
   - API Documentation: [http://127.0.0.1/docs](http://127.0.0.1/docs)
