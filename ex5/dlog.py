#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from gmpy import invert, mpz

import logging as log
if __debug__:
    log.basicConfig(level=log.DEBUG)
else:
    log.basicConfig()

p = mpz(13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084171)
g = mpz(11717829880366207009516117596335367088558084999998952205599979459063929499736583746670572176471460312928594829675428279466566527115212748467589894601965568)
h = mpz(3239475104050450443565264378728065788649097520952449527834792452971981976143292558073856937958553180532878928001494706097394108577585732452307673444020333)

B = mpz(2**20)

def dlog(p, g, h, B):
    """
    Meet in the middle for descrete log problem

    >>> x=13; g=2; p=23; h=(g**x)%p; B=8
    >>> dlog(p, g, h, B)
    (1, 5)
    >>> x=11; g=3; p=23; h=(g**x)%p; B=8
    >>> dlog(p, g, h, B)
    (1, 3)
    >>> x=2; g=3; p=5; h=(g**x)%p; B=4
    >>> dlog(p, g, h, B)
    (1, 2)
    """
    log.warning("Computing left side")
    left = { (h*invert(pow(g, x1, p), p)) % p : x1 for x1 in xrange(B) }
    log.warning("Computing right side")
    g_b = pow(g, B, p)
    for x0 in xrange(B):
        value = pow(g_b, x0, p)
        if value in left:
            return x0, left[value]
    return None

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    (options, args) = parser.parse_args()

    x0,x1 = dlog(p, g, h, B)
    log.warning("x0 = {0}, x1 = {1}".format(x0, x1))

    x = (x0*B + x1) % p
    log.critical("x = {0}".format(x))
    assert(pow(g, x, p)  == h)
