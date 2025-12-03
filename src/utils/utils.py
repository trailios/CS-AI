from typing         import Union, Dict, Any
from mmh3           import hash_bytes
from struct         import unpack
from urllib.parse   import quote
from hashlib        import md5
from time           import time

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
        """USED FOR TIEMSTAMP IN COOKIE"""
        current_time = time()
        timestamp_str = str(int(current_time * 1000))

        return f"{timestamp_str[:7]}00{timestamp_str[7:]}"

    @staticmethod
    def short_esync() -> str:
        current_time = time() * 1000
        
        return int(round(int(current_time), -2))

    @staticmethod
    def x_newrelic_timestamp() -> str:
        return str(int(time() * 100000))

    @staticmethod
    def construct_form_data(data: Dict[str, Any]) -> str:
        filtered_data: Dict[str, Any] = {
            key: value for key, value in data.items() if value is not None
        }
        encoded_data: list[str] = [
            f"{key}={quote(str(value), safe='()')}"
            for key, value in filtered_data.items()
        ]
        form_data: str = "&".join(encoded_data)
        return form_data
    
    @staticmethod
    def encode(input_str: str) -> str:
        safe_chars = set(
            b"!'()*-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~"
        )

        hex_table = [f"%{i:02X}" for i in range(256)]

        result = []
        for ch in input_str:
            b = ord(ch)
            if b in safe_chars:
                result.append(chr(b))
            else:
                result.append(hex_table[b])

        return "".join(result)
