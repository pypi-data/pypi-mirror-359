"""
Tests for the crypto module.
"""

import tempfile
import os
from pathlib import Path
import pytest
from ffenc.crypto import encrypt, decrypt


def test_encrypt_decrypt_text():
    """Test encrypting and decrypting text content."""
    password = "test_password_123"
    content = "Hello, this is a test message!"
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.enc')
    temp_file.close()
    
    try:
        # Encrypt
        encrypt(password, content, temp_file.name)
        
        # Decrypt
        decrypted_content = decrypt(password, temp_file.name)
        
        # Verify
        assert decrypted_content.decode('utf-8') == content
        
    finally:
        # Cleanup
        os.unlink(temp_file.name)


def test_encrypt_decrypt_binary():
    """Test encrypting and decrypting binary content."""
    password = "test_password_456"
    content = b"Binary data: \x00\x01\x02\x03\xff\xfe\xfd"
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.enc')
    temp_file.close()
    
    try:
        # Encrypt
        encrypt(password, content, temp_file.name)
        
        # Decrypt
        decrypted_content = decrypt(password, temp_file.name)
        
        # Verify
        assert decrypted_content == content
        
    finally:
        # Cleanup
        os.unlink(temp_file.name)


def test_wrong_password():
    """Test that wrong password fails decryption."""
    password = "correct_password"
    wrong_password = "wrong_password"
    content = "Test content"
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.enc')
    temp_file.close()
    
    try:
        # Encrypt with correct password
        encrypt(password, content, temp_file.name)
        
        # Try to decrypt with wrong password
        with pytest.raises(Exception):
            decrypt(wrong_password, temp_file.name)
            
    finally:
        # Cleanup
        os.unlink(temp_file.name) 