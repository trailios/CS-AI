import time

class Tools:
    def __init__(self) -> None:
        pass

    @staticmethod
    def x_ark_esync() -> str:
        current_time = time.time()
        timestamp_str = str(int(current_time * 1000))
        timestamp_str = timestamp_str.zfill(13)
        return f"{timestamp_str[:7]}00{timestamp_str[7:]}" # IMPORTANT: NOT THE SAME AS NEWERLIC TIMESTAMP!!
    
    @staticmethod
    def short_esync() -> str:
        current_time = time.time()
        return str(int(current_time - (current_time % 21600)))

    @staticmethod
    def x_newrelic_timestamp() -> str:
        return str(int(time.time() * 100000))