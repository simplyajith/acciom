import base64

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from index import app

BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s: s[0:-ord(s[-1:])]


def get_private_key(password):
    """
    Method to generate the private key for the provided Encryption key .

    Args:
        password(str): DB Encryption key.

    Returns:
          Returns a private key which is used to generate encrypted password.

    """
    salt = b"this is a salt"
    kdf = PBKDF2(password, salt, 64, 1000)
    key = kdf[:32]
    return key


def encrypt(raw):
    """
    Method to generate encrypted password for the user given password.

    Args(str):
        raw: Password provided by the user.

    Returns:
         Returns Encrypted password.
    """
    private_key = get_private_key(
        app.config.get('DB_ENCRYPTION_KEY'))
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    base64_encoded = base64.b64encode(iv + cipher.encrypt(raw))
    return str(base64_encoded, 'utf-8')


def decrypt(enc):
    """
    Method will convert encrypted text from bytes to string format
    Args:
        enc(bytes): Recieves encrypted text in bytes.

    Returns: Returns a string format of text from encrypted text

    """
    private_key = get_private_key(
        app.config.get('DB_ENCRYPTION_KEY'))
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))
