#!/usr/bin/env python3
"""
Secure Credential Input - Never expose secrets in chat
Password is entered in terminal (not visible), encrypted, stored safely
"""

import getpass
import json
import os
from datetime import datetime
from cryptography.fernet import Fernet
from pathlib import Path
import hashlib

CREDS_DIR = Path(".secrets/credentials")
CREDS_DIR.mkdir(parents=True, exist_ok=True)

def generate_encryption_key(password_hint="blotato"):
    """Generate a key based on system + hint"""
    # This key is NOT the password itself, just used to encrypt it
    seed = f"{os.uname()[1]}{password_hint}"  # Machine name + hint
    key = hashlib.sha256(seed.encode()).digest()[:32]
    return Fernet(Fernet.generate_key())  # Fresh key each time

def store_credential_securely(service, username, password):
    """
    Store credential encrypted in .secrets/
    Never logs password to console or chat
    """
    print(f"\n🔒 Encrypting and storing {service} credentials...")
    
    # Generate encryption key (random, not password-based)
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # Encrypt password
    encrypted_password = cipher.encrypt(password.encode()).decode()
    
    # Store encrypted password + key separately
    cred_data = {
        "service": service,
        "username": username,
        "encrypted_password": encrypted_password,
        "stored_at": datetime.now().isoformat()
    }
    
    # Write encrypted data
    cred_file = CREDS_DIR / f"{service}-credentials.json"
    with open(cred_file, 'w') as f:
        json.dump(cred_data, f)
    os.chmod(cred_file, 0o600)  # Owner read/write only
    
    # Write encryption key (separate file)
    key_file = CREDS_DIR / f"{service}-key.bin"
    with open(key_file, 'wb') as f:
        f.write(key)
    os.chmod(key_file, 0o600)
    
    print(f"✅ Credentials stored securely")
    print(f"   Location: {cred_file}")
    print(f"   Key: {key_file}")
    print(f"   Permissions: 600 (owner only)")
    
    return cred_file, key_file

def load_credential_securely(service):
    """Load encrypted credential"""
    cred_file = CREDS_DIR / f"{service}-credentials.json"
    key_file = CREDS_DIR / f"{service}-key.bin"
    
    if not cred_file.exists() or not key_file.exists():
        return None
    
    # Load key
    with open(key_file, 'rb') as f:
        key = f.read()
    cipher = Fernet(key)
    
    # Load and decrypt data
    with open(cred_file, 'r') as f:
        cred_data = json.load(f)
    
    password = cipher.decrypt(cred_data['encrypted_password'].encode()).decode()
    
    return {
        "username": cred_data['username'],
        "password": password
    }

def input_credential_securely(service, username=None):
    """
    Prompt for credential WITHOUT displaying password
    Uses getpass.getpass() - password input is hidden
    """
    print(f"\n🔐 SECURE CREDENTIAL INPUT FOR {service.upper()}")
    print("=" * 60)
    
    if username is None:
        username = input(f"Email/Username for {service}: ").strip()
    else:
        print(f"Using username: {username}")
    
    # Get password without displaying it
    print(f"Enter password (will not be displayed): ")
    password = getpass.getpass("Password: ")
    
    # Confirm password (re-enter)
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("❌ Passwords don't match. Try again.")
        return None
    
    # Store securely
    store_credential_securely(service, username, password)
    
    print(f"\n✅ {service.upper()} credentials stored securely")
    print(f"   Ready to use: load_credential_securely('{service}')")
    
    return username, password

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║         SECURE CREDENTIAL STORAGE                              ║
║                                                                 ║
║  This tool allows you to enter passwords in terminal           ║
║  WITHOUT displaying them on screen or in chat.                 ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    service = input("What service? (e.g., 'blotato', 'youtube', 'gumroad'): ").strip().lower()
    username = input(f"Username/Email for {service}: ").strip()
    
    print(f"\n📝 Enter password for {service}")
    print("   (Your password will NOT be visible as you type)")
    print("   (It will be encrypted and stored securely)\n")
    
    password = getpass.getpass(f"Password for {username}: ")
    
    # Confirm
    print("\nConfirming password...")
    password_confirm = getpass.getpass("Re-enter password: ")
    
    if password != password_confirm:
        print("❌ Passwords don't match!")
        return
    
    # Store
    store_credential_securely(service, username, password)
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE: {service.upper()} credentials stored")
    print(f"{'='*60}")
    print(f"\nTo use these credentials:")
    print(f"  creds = load_credential_securely('{service}')")
    print(f"  username = creds['username']")
    print(f"  password = creds['password']")

if __name__ == "__main__":
    main()
