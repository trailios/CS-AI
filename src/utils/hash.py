from mmh3    import hash_bytes
from struct  import unpack
from typing  import Union
from hashlib import md5

def md5hash(data: str):
    try:
        return md5(data.encode()).hexdigest()
    except Exception:
        raise Exception("Failed to MD5 hash data.")


def x64hash128(data: Union[str, bytes], seed: int = 0) -> str:
    if isinstance(data, str):
        data = data.encode()

    Hb: bytes = hash_bytes(data, seed=seed, x64arch=True)
    Hp: tuple[int, int] = unpack("<QQ", Hb)
    Hhs: str = "{:016x}{:016x}".format(*Hp)

    return Hhs
