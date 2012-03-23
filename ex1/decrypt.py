#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
from collections import defaultdict, Counter

def read_file(filename):
    with open(filename) as lines:
        for line in lines:
            yield line.strip().decode('hex')

def xor_combinations(data):
    """
    Returns all posible combinations of XORs between data entries

    >>> list(xor_combinations(["AAA","AAA"]))
    [('AAA', 'AAA', '\x00\x00\x00')]
    >>> list(xor_combinations(["AAA","BBB", "CCCC"]))
    [('AAA', 'BBB', '\x03\x03\x03'), ('AAA', 'CCCC', '\x02\x02\x02'), ('BBB', 'CCCC', '\x01\x01\x01')]
    """
    import itertools
    for ct1, ct2 in itertools.combinations(data,2):
        xorred = []
        for char1, char2 in zip(ct1, ct2):
            xorred.append(chr(ord(char1) ^ ord(char2))) 
        yield ct1, ct2, "".join(xorred)

def statistics(data):
    """Returns list of possible values for each byte of key"""
    possibilities = defaultdict(list)
    for ct1, ct2, xorred in data:
        for (i, char) in enumerate(xorred):
            # The unlimate hint was given at Question itself:
            # Hint: XOR the ciphertexts together, and consider what happens when a space is XORed with a character in [a-zA-Z]. 
            if char in string.letters:
                possibilities[i].extend([ord(ct1[i])^32, ord(ct2[i])^32])
    return possibilities

def guess_key(possibilities):
    """
    Simplest heuristics ever - just return most common value for each dict key
    XXX: sic! Because of that output is not 100% correct. We should take into
    an account english letter distribution.
    """
    return "".join(chr(Counter(item).most_common(1)[0][0]) for item in possibilities.values())

if __name__ == '__main__':
    import logging
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", type="string", dest="file", default="many-times-pad.txt")
    (options, args) = parser.parse_args()

    data = list(read_file(options.file))
    possibilities = statistics(xor_combinations(data))

    key = guess_key(possibilities)
    logging.warn("Possible key: {0}".format(key.encode('hex')))

    from encrypt import strxor 
    for target in data:
        logging.warning("Partially recovered data: {0}".format(strxor(target, key)))
