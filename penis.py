import os
import struct
import time

class ChromeMathRandom:
    def __init__(self):
        # This is what V8 actually does: seeds from time + entropy
        seed = int.from_bytes(os.urandom(32), 'little') ^ int(time.time() * 1000000)
        self.s = [
            seed & 0xFFFFFFFFFFFFFFFF,
            (seed >> 64) ^ 0x6c33f7c36c33f7c3,
            0x123456789abcdef1,
            0xcafef00ddeadbeef
        ]

    def _rotl(self, x, k):
        return ((x << k) | (x >> (64 - k))) & 0xFFFFFFFFFFFFFFFF

    def next(self):
        s = self.s
        result = self._rotl(s[0] + s[3], 23) + s[0]

        t = s[1] << 17

        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]

        s[2] ^= t
        s[3] = self._rotl(s[3], 45)

        return result & 0xFFFFFFFFFFFFFFFF

    def random(self):
        # This is EXACTLY what Chrome/V8 does for Math.random()
        return (self.next() >> 11) * (1.0 / 9007199254740992.0)

# Now every run gives different numbers — just like real Chrome!
rnd = ChromeMathRandom()
for _ in range(10):
    print(rnd.random())

input()
print(rnd.random())