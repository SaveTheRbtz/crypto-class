#!/usr/bin/env python

from hashlib import sha256
from struct import unpack, pack
from multiprocessing import Pool

CACHE = {}
MASK = ~(2**14-1) # 50 bits

def compute_sha50(number):
    """
    Compute LSB50(SHA256(packed_bytes))
    Return truncated hash along with input

    >>> compute_sha50(0)
    (18175939719907508224L, 0)
    >>> compute_sha50(2147483648)
    (15347183072311246848L, 2147483648L)
    >>> compute_sha50(4294967296L)
    (11344223799538089984L, 4294967296L)
    >>> compute_sha50(4294967297)
    (17657647642429095936L, 4294967297L)

    FIXME: Not safe for big-endian
    """
    sha50 = unpack("Q", sha256(pack("Q", number)).digest()[-8:])[0] & MASK
    return sha50, number

if __name__ == '__main__':
    pool = Pool()
    for i, output in enumerate(pool.imap_unordered(compute_sha50, xrange(2147483647), 2**14)):
        sha50, packed_bytes = output
        if sha50 not in CACHE:
            CACHE[sha50] = packed_bytes
        else:
            print "Found: {1}={0}; {2}={0}".format(sha50, CACHE[sha50], packed_bytes)
            print "Iteration number: {0}".format(i)
