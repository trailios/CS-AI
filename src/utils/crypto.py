import base64
from os                     import urandom
from json                   import loads, dumps
from base64                 import b64decode, b64encode
from hashlib                import md5
from string                 import ascii_lowercase
from random                 import choice
from Crypto.Cipher          import AES
from Crypto.Util.Padding    import pad, unpad
from typing                 import Dict, Any


from cryptography.hazmat.backends                       import default_backend
from cryptography.hazmat.primitives.ciphers             import Cipher, algorithms, modes
from cryptography.hazmat.primitives                     import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.padding  import OAEP, MGF1

def rsa_encrypt(data: str, public_key_b64: str) -> str:
    aes_key = urandom(32)
    iv = urandom(12)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
    tag = encryptor.tag
    pubkey_bytes = base64.b64decode(public_key_b64)
    rsa_pubkey = serialization.load_der_public_key(pubkey_bytes, backend=default_backend())
    encrypted_key = rsa_pubkey.encrypt(
        aes_key,
        OAEP(
            mgf=MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    parts = {
        "iv": base64.b64encode(iv).decode(),
        "tag": base64.b64encode(tag).decode(),
        "key": base64.b64encode(encrypted_key).decode(),
        "cipher": base64.b64encode(ciphertext).decode(),
    }
    return f"{parts['iv']}{parts['tag']}{parts['key']}{parts['cipher']}"

class AES_Crypto:
    def __init__(self):
        pass

    @staticmethod
    def _generate_salted_key(key: str, salt: str) -> str:
        salted = ""
        dx = b""

        for _ in range(3):
            dx = md5(dx + key.encode("utf-8") + salt.encode("utf-8")).digest()
            salted += dx.hex()

        return salted

    @staticmethod
    def decrypt_data(raw_data: str, key: str) -> str:
        data: Dict[str, str] = loads(raw_data)

        salt: bytes = bytes.fromhex(data["s"])
        salted_key: str = AES_Crypto._generate_salted_key(key, salt.decode("utf-8"))

        aes_key: bytes = bytes.fromhex(salted_key[:64])
        iv: bytes = bytes.fromhex(data["iv"])

        aes = AES.new(aes_key, AES.MODE_CBC, iv)

        cipher_text: bytes = b64decode(data["ct"])
        decrypted_data: bytes = unpad(aes.decrypt(cipher_text), AES.block_size)

        return decrypted_data.decode("utf-8")

    @staticmethod
    def encrypt_data(data: str, key: str, switch_order: bool = False) -> str:
        salt: str = "".join(choice(ascii_lowercase) for _ in range(8))
        salted_key: str = AES_Crypto._generate_salted_key(key, salt)

        aes_key: bytes = bytes.fromhex(salted_key[:64])
        iv: bytes = bytes.fromhex(salted_key[64:96])

        aes = AES.new(aes_key, AES.MODE_CBC, iv)

        padded_data: bytes = pad(data.encode("utf-8"), AES.block_size)
        cipher_text: bytes = aes.encrypt(padded_data)

        encrypted_data: Dict[str, Any] = {
            "ct": b64encode(cipher_text).decode("utf-8"),
            "iv": iv.hex(),
            "s": salt.encode("utf-8").hex(),
        }

        if switch_order:
            encrypted_data = {
                "ct": b64encode(cipher_text).decode("utf-8"),
                "s": salt.encode("utf-8").hex(),
                "iv": iv.hex(),
            }

        return dumps(encrypted_data)
    
    