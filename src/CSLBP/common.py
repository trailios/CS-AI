from itertools import cycle
from typing import Union


def xor_cipher(
    data: Union[bytes, bytearray], key: Union[str, bytes, bytearray]
) -> bytes:
    if isinstance(key, str):
        key_bytes = key.encode("utf-8")

    elif isinstance(key, (bytes, bytearray)):
        key_bytes = bytes(key)

    else:
        raise TypeError("Key must be str, bytes, or bytearray")

    if not key_bytes:
        raise ValueError("Key must not be empty")

    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Data must be bytes or bytearray")

    result = bytearray(len(data))
    for i, (byte, k) in enumerate(zip(data, cycle(key_bytes))):
        result[i] = byte ^ k

    return bytes(result)


encrypt = xor_cipher
decrypt = xor_cipher
