# FFenc - File Encryption Tool

A secure file encryption and decryption tool with password protection.

## Features

- **Secure Encryption**: Uses Fernet (AES-128-CBC) for content encryption
- **Password Protection**: Encrypts the encryption key with PBKDF2 key derivation
- **CLI Interface**: Easy-to-use command-line interface
- **Hidden Passwords**: Secure password input that doesn't display on screen
- **File and Text Support**: Encrypt both files and text content
- **Binary Safe**: Handles both text and binary files

## Installation

```bash
pip install -e .
```

## Usage

### Command Line Interface

The tool provides several commands for different use cases:

#### Encrypt a File

```bash
# Encrypt a file (password will be prompted)
ffenc encrypt-file input.txt output.enc

# Encrypt with password provided
ffenc encrypt-file input.txt output.enc --password "mysecret"

# Encrypt with password flag
ffenc encrypt-file input.txt output.enc -p "mysecret"
```

#### Decrypt a File

```bash
# Decrypt to a new file (password will be prompted)
ffenc decrypt-file output.enc decrypted.txt

# Decrypt to stdout
ffenc decrypt-file output.enc --stdout

# Decrypt with password provided
ffenc decrypt-file output.enc decrypted.txt -p "mysecret"
```

#### Encrypt Text Content

```bash
# Encrypt text from command line
ffenc encrypt-text "Hello, secret message!" output.enc

# Encrypt text from file
ffenc encrypt-text --file input.txt output.enc

# Encrypt text from stdin
echo "Secret message" | ffenc encrypt-text output.enc
```

### Python API

You can also use the functions directly in Python:

```python
from ffenc import encrypt, decrypt

# Encrypt content
encrypt("my_password", "Hello, secret message!", "output.enc")

# Decrypt content
decrypted = decrypt("my_password", "output.enc")
print(decrypted.decode('utf-8'))  # Hello, secret message!
```

## Security Features

- **Key Generation**: Each encryption generates a unique random key
- **Key Derivation**: Uses PBKDF2 with 100,000 iterations for password-based key derivation
- **Salt**: Each encryption uses a unique salt for additional security
- **Secure Storage**: The encryption key is encrypted with the password before storage

## File Format

Encrypted files are stored in JSON format containing:
- Encrypted encryption key (encrypted with password)
- Salt used for key derivation
- Encrypted content (base64 encoded)

## Examples

### Encrypting a sensitive document

```bash
ffenc encrypt-file secret_document.txt secret_document.enc
# Enter password when prompted
```

### Decrypting and viewing content

```bash
ffenc decrypt-file secret_document.enc --stdout
# Enter password when prompted
```

### Encrypting a configuration file

```bash
ffenc encrypt-text --file config.json config.enc
# Enter password when prompted
```

## Development

### Running Tests

```bash
pytest tests/
```

### Building

```bash
pip install build
python -m build
```

## License

MIT License - see LICENSE.txt for details.
