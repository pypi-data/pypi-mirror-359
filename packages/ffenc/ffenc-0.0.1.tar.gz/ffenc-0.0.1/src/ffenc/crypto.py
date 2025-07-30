"""
Encryption and decryption utilities for ffenc.
"""

import os
import json
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64


def generate_encryption_key() -> bytes:
    """Generate a random encryption key."""
    return Fernet.generate_key()


def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Derive a key from password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_content(content: Union[str, bytes], key: bytes) -> bytes:
    """Encrypt content using the provided key."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    fernet = Fernet(key)
    return fernet.encrypt(content)


def decrypt_content(encrypted_content: bytes, key: bytes) -> bytes:
    """Decrypt content using the provided key."""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_content)


def encrypt_key_with_password(encryption_key: bytes, password: str) -> dict:
    """Encrypt the encryption key with the password."""
    key, salt = derive_key_from_password(password)
    fernet = Fernet(key)
    encrypted_key = fernet.encrypt(encryption_key)
    
    return {
        'encrypted_key': base64.b64encode(encrypted_key).decode('utf-8'),
        'salt': base64.b64encode(salt).decode('utf-8')
    }


def decrypt_key_with_password(encrypted_key_data: dict, password: str) -> bytes:
    """Decrypt the encryption key using the password."""
    encrypted_key = base64.b64decode(encrypted_key_data['encrypted_key'])
    salt = base64.b64decode(encrypted_key_data['salt'])
    
    key, _ = derive_key_from_password(password, salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_key)


def encrypt(password: str, content: Union[str, bytes], file_path: str) -> None:
    """
    Encrypt content and save to file.
    
    Args:
        password: Password to encrypt the key with
        content: Content to encrypt (string or bytes)
        file_path: Path to save the encrypted file
    """
    # 1. Generate encryption key
    encryption_key = generate_encryption_key()
    
    # 2. Encrypt content
    encrypted_content = encrypt_content(content, encryption_key)
    
    # 3. Encrypt key with password
    encrypted_key_data = encrypt_key_with_password(encryption_key, password)
    
    # 4. Save encrypted key and content to file
    data_to_save = {
        'encrypted_key_data': encrypted_key_data,
        'encrypted_content': base64.b64encode(encrypted_content).decode('utf-8')
    }
    
    with open(file_path, 'w') as f:
        json.dump(data_to_save, f)


def decrypt(password: str, file_path: str) -> bytes:
    """
    Decrypt content from file.
    
    Args:
        password: Password to decrypt the key with
        file_path: Path to the encrypted file
        
    Returns:
        Decrypted content as bytes
    """
    # Load encrypted data
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # 1. Decrypt encrypted key
    encryption_key = decrypt_key_with_password(data['encrypted_key_data'], password)
    
    # 2. Use the key to decrypt content
    encrypted_content = base64.b64decode(data['encrypted_content'])
    decrypted_content = decrypt_content(encrypted_content, encryption_key)
    
    return decrypted_content 