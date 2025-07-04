from mmh3       import hash_bytes
from struct     import unpack
from typing     import Union
from hashlib    import md5
from time       import time

class Utils:
    @staticmethod
    def md5hash(data: str) -> str:
        try:
            return md5(data.encode()).hexdigest()
        
        except Exception as e:
            raise Exception("Failed to MD5 hash data.") from e

    @staticmethod
    def x64hash128(data: Union[str, bytes], seed: int = 0) -> str:
        if isinstance(data, str):
            data = data.encode()

        hashed_bytes: bytes = hash_bytes(data, seed=seed, x64arch=True)
        hash_parts: tuple[int, int] = unpack("<QQ", hashed_bytes)

        return "{:016x}{:016x}".format(*hash_parts)

    @staticmethod
    def x_ark_esync() -> str:
        current_time = time()
        timestamp_str = str(int(current_time * 1000)).zfill(13)

        return f"{timestamp_str[:7]}00{timestamp_str[7:]}"

    @staticmethod
    def short_esync() -> str:
        current_time = time()
        
        return str(int(current_time - (current_time % 21600)))

    @staticmethod
    def x_newrelic_timestamp() -> str:
        return str(int(time() * 100000))
