import random

P = 295075153L   # about 2^28

class WeakPrng(object):
    def __init__(self, p):   # generate seed with 56 bits of entropy
        self.p = p
        self.x = random.randint(0, p)
        self.y = random.randint(0, p)
   
    def next(self):
        # x_{i+1} = 2*x_{i}+5  (mod p)
        self.x = (2*self.x + 5) % self.p

        # y_{i+1} = 3*y_{i}+7 (mod p)
        self.y = (3*self.y + 7) % self.p

        # z_{i+1} = x_{i+1} xor y_{i+1}
        return (self.x ^ self.y) 


prng = WeakPrng(P)
for i in range(1, 10):
  print "output #%d: %d" % (i, prng.next())
