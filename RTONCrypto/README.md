# RTONCrypto
- decrypt.py: a tool to decrypt RTON files
- encrypt.py: a tool to encrypt RTON files
- fail.txt: file with the last errors
- options.json: settings for decrypting (see below)
- README.md: this file

# options.json
key | purpose
--- | ---
confirmPath | Confirm or change parsed path before conversion
DEBUG_MODE | Show full error traceback
enteredPath | Don't use hybrid paths that can be escaped
|
encryption_key | Key used for encrypting, the default is not right, search it if you want to decrypt