"""File to handle encrypt operations."""
import base64

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from index import app

pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
BS = 16


def get_private_key(password):
    """
    Method to generate private key.

    Args:
        password(str): DB Encryption key.

    Returns:
          Returns a private key.

    """
    salt = b"this is a salt"
    kdf = PBKDF2(password, salt, 64, 1000)
    key = kdf[:32]
    return key


def encrypt(raw):
    """
    Method to generate encrypted password.

    Args:
        raw: Password provided by user.

    Returns:
         Returns Encrypted password.
    """
    print("raw", raw)
    private_key = get_private_key(
        app.config.get('DB_ENCRYPTION_KEY'))
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))
