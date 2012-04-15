#!/usr/bin/env python
import logging as log
import re

if __debug__:
    log.basicConfig(level=log.DEBUG)
else:
    log.basicConfig()

def strxor(a, b):
    """xor two strings of same lengths"""
    return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])

def main(filename):
    ciphertext = ''
    oracles = []
    plaintexts = []

    # Very dumb access log parsing
    payload = re.compile(r'.* "GET /([0-9a-z]+) .*"')

    with open(filename) as lines:
        for line in lines:
            try:
                line = line.strip()
                if line.endswith(' 200'):
                    ciphertext, = payload.findall(line)
                elif line.endswith(' 404') and '/20' not in line:
                    oracles.append(payload.findall(line)[0])
            except Exception as e:
                log.debug("Line processing failed: %(line)s", dict(line=line), exc_info=True)

    log.info("ciphertext: %(ciphertext)s", dict(ciphertext=ciphertext))
    log.info("oracles: %(oracles)s", dict(oracles=oracles))

    # XXX: UGLY!!
    padding = ('10' * 16).decode('hex')
    for i in range(1, len(oracles)):
        xorred_guess = oracles[i][:32].decode('hex')
        ciphertext = oracles[i - 1][32:].decode('hex')
        plaintexts.append(strxor(strxor(ciphertext, padding), xorred_guess))

    log.warning("plaintext: %(plaintext)s", dict(plaintext="".join(plaintexts)))


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", type="string", dest="file", default="proj4-log.txt")
    (options, args) = parser.parse_args()

    main(options.file)
