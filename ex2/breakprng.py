#!/usr/bin/env python

from weakprng import WeakPrng, P
from common import setup_signals

NEEDED_SEQ = [210205973, 22795300, 58776750, 121262470, 264731963, 140842553, 242590528, 195244728, 86752752]
PROGRESS_BAR = {}

class SeedPrng(WeakPrng):
    def __init__(self, x, y, p):
        """Redefined it to be able to manually set seed"""
        self.p = p
        self.x = x
        self.y = y

if __name__ == '__main__':
    setup_signals(PROGRESS_BAR) 
    for x in xrange(P):
        if not (x % 10**5):
            PROGRESS_BAR.update({'completed': float(x)/P})
        y = NEEDED_SEQ[0] ^ x
        initial = SeedPrng(x, y, P)
        for random_num in NEEDED_SEQ[1:]:
            if initial.next() != random_num:
                break
        else:
            print initial.next()
            break
