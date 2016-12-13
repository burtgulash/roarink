#!/usr/bin/env python3

import collections


class _RoaringArray(list):
    pass

class _RoaringBits:

    def __init__(self, xs):
        self.bitmap = []
        for x in sorted(xs):
            field, pos = divmod(x, 64)
            while len(self.bitmap) < field + 1:
                self.bitmap.append(0)
            self.bitmap[field] |= (1 << pos)

    def __contains__(self, x):
        field, pos = divmod(x, 64)
        return field < len(self.bitmap) and bool((self.bitmap[field] >> pos) & 1)

    def print(self):
        for field in self.bitmap:
            print(bin(field))


class RoaringBitmap:
    
    def __init__(self, d):
        self._d = d

    def __contains__(self, x):
        chunk, rem = divmod(x, 1 << 16)
        return chunk in self._d and rem in self._d[chunk]


class RoaringBuilder:

    def __init__(self):
        self.chunks = collections.defaultdict(list)
    
    def insert(self, x):
        chunk, rem = divmod(x, 1 << 16)
        self.chunks[chunk].append(rem)

    def fossilize(self):
        # Threshold is a solution to equation describing when size of list with
        # 16bit integers (x * 16) equals size of bitmap with (1 << 16) possible
        # elements  # (1 << 16) == x * 16
        threshold = (1 << 16) // 16
        return RoaringBitmap({
            x: (_RoaringArray(xs) if len(xs) < threshold else _RoaringBits(xs)) 
            for x, xs in self.chunks.items()
        })
        

if __name__ == "__main__":
    xs = [4, 8, 23, 35, 2, 128, 200, 31, 32, 33, 1, 0]
    bm = _RoaringBits(xs)
    bm.print()

    r = RoaringBuilder()
    for x in range(0, 10000, 2):
        r.insert(x)
    for x in xs:
        r.insert(x * 10000)

    roaring = r.fossilize()
    for x in xs:
        print(x in roaring)
