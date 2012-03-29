#!/usr/bin/env python

from hashlib import sha256
from struct import unpack, pack
from itertools import combinations
from multiprocessing import Pool

CACHE = {}
MAX_CACHE_SIZE = 1024*1024*1024*5 # 25 Gb
MASK = ~(2**14-1) # 50 bits

def compute_sha50(bytes_):
    """
    Compute LSB50(SHA256(bytes_))
    Return truncated hash along with input

    >>> compute_sha50((0, 1, 2, 3, 4, 5, 6, 69))
    (1036915800318164992L, (0, 1, 2, 3, 4, 5, 6, 69))
    >>> compute_sha50([0, 1, 2, 3, 4, 5, 7, 189])
    (1036763512738545664L, [0, 1, 2, 3, 4, 5, 7, 189])

    TODO: conserve memory
    FIXME: Not safe for big-endian
    """
    sha50 = unpack("Q", sha256(pack('B'*len(bytes_), *bytes_)).digest()[-8:])[0] & MASK
    return sha50, bytes_

if __name__ == '__main__':
    pool = Pool()
    for i, output in enumerate(pool.imap_unordered(compute_sha50, combinations(range(256), 4)), 2**14):
        sha50, bytes_ = output
        if sha50 not in CACHE:
            if len(CACHE) < MAX_CACHE_SIZE:
                CACHE[sha50] = bytes_
        else:
            print "Found: {1}={0}; {2}={0}".format(sha50, CACHE[sha50], bytes_)
            print "Iteration number: {0}".format(i)
