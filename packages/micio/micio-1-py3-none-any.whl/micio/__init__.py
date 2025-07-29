from micio.__about__ import *

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

__PKG_DIR = os.path.dirname(__file__)

def derive_key(password: bytes, salt: bytes) -> bytes:
    """Derives a key from the password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

def encrypt_string(plain_text: str, password: str) -> bytes:
    """Encrypts a string with a password."""
    salt = os.urandom(16)
    key = derive_key(password.encode(), salt)
    f = Fernet(key)
    encrypted_data = f.encrypt(plain_text.encode())
    return salt + encrypted_data

def decrypt_string(encrypted_data: bytes, password: str) -> str:
    """Decrypts a string with a password."""
    salt = encrypted_data[:16]
    encrypted_message = encrypted_data[16:]
    key = derive_key(password.encode(), salt)
    f = Fernet(key)
    try:
        decrypted_data = f.decrypt(encrypted_message)
        return decrypted_data.decode()
    except Exception as e:
        # print(f"Decryption failed: {e}")
        return ""


if os.environ.get('GTH_CDSP'):
    pwd = ''
else:
    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk()
    root.withdraw()

    top = tk.Toplevel()
    top.withdraw()
    top.attributes('-topmost', True)
    top.after(0, top.destroy)  # Destroy it immediately after use

    pwd = simpledialog.askstring("", "Your hero:").upper().strip().replace(' ', '')

if False:
    string = ""
    pwd = ""

    encrptd_string = encrypt_string(string, pwd)
    decrypted_string = decrypt_string(encrptd_string, pwd)

    with open('./micio/res/poke', 'wb') as f:
        f.write(encrptd_string)
    with open('./micio/res/poke', 'rb') as f:
        poke = f.read()

    with open('./micio/res/wlcm', 'wb') as f:
        f.write(encrptd_string)
    with open('./micio/res/wlcm', 'rb') as f:
        wlcm = f.read()


def poke():
    with open(f'{__PKG_DIR}/res/poke', 'rb') as f:
        poke = f.read()
    print(decrypt_string(poke, pwd))


with open(f'{__PKG_DIR}/res/wlcm', 'rb') as f:
    wlcm = f.read()
print(decrypt_string(wlcm, pwd))




