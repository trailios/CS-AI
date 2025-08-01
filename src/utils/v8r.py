import os
import time
from dataclasses import dataclass
from typing import List

CACHE_SIZE = 64 

@dataclass
class State:
    s0: int = 0
    s1: int = 0


class MathRandomV8:
    def __init__(self, seed: int = 0):
        self.cache: List[float] = [0.0] * CACHE_SIZE
        self.index: int = 0
        self.state = State()
        self.seed = seed or self._get_entropy_seed()
        self.reset_context()

    def reset_context(self):
        self.index = 0
        self.state = State()
        self.refill_cache()

    def refill_cache(self):
        if self.state.s0 == 0 and self.state.s1 == 0:
            s = self.seed
            self.state.s0 = self._murmur_hash3(s)
            self.state.s1 = self._murmur_hash3(~s & 0xFFFFFFFFFFFFFFFF)
            assert self.state.s0 != 0 or self.state.s1 != 0

        for i in range(CACHE_SIZE):
            self.state.s0, self.state.s1 = self._xorshift128plus(self.state.s0, self.state.s1)
            self.cache[i] = self._to_double(self.state.s0)

        self.index = CACHE_SIZE

    def next(self) -> float:
        if self.index == 0:
            self.refill_cache()
        self.index -= 1
        return self.cache[self.index]

    @staticmethod
    def _xorshift128plus(s0: int, s1: int):
        s1 ^= (s1 << 23) & 0xFFFFFFFFFFFFFFFF
        s1 ^= (s1 >> 17)
        s1 ^= s0
        s1 ^= (s0 >> 26)
        return s1, (s0 + s1) & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def _to_double(v: int) -> float:
        return (v >> 11) * (1.0 / (1 << 53))

    @staticmethod
    def _murmur_hash3(key: int) -> int:
        key ^= key >> 33
        key = (key * 0xff51afd7ed558ccd) & 0xFFFFFFFFFFFFFFFF
        key ^= key >> 33
        key = (key * 0xc4ceb9fe1a85ec53) & 0xFFFFFFFFFFFFFFFF
        key ^= key >> 33
        return key

    @staticmethod
    def _get_entropy_seed() -> int:
        try:
            return int.from_bytes(os.urandom(8), 'little')
        
        except Exception:
            now = int(time.time() * 1e9)
            perf = int(time.perf_counter() * 1e9)
            return now ^ perf

