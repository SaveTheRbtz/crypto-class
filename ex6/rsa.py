#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from multiprocessing import Process, cpu_count
from gmpy import mpz, sqrt, fsqrt, ceil, set_minprec

import zmq
import logging as log

# Avoid race on CPU hotplug
NCPU = cpu_count()

if __debug__:
    log.basicConfig(level=log.DEBUG)
else:
    log.basicConfig()

#
# Subroutines
#

def create_ranges(start, end, size):
    """Yields tuples(chunk_start, chunk_end) of size `size`"""
    while start < end:
        yield (start, start + size)
        start += size + 1

#
# Compute part
#
def _func1(N, A):
    """Computes p and q based on N and A"""
    x = sqrt(A**2 - N)
    p = A - x
    q = A + x
    return p,q

def func1(N):
    """Computes p and q based on N and the fact that  |p−q| < 2*N**(1/4)"""
    A = mpz(ceil(fsqrt(N)))
    return _func1(N, A)

def func2(N, A):
    """Safe compute of _func1"""
    try:
        return _func1(N, A)
    except Exception:
        return 0, 0

#
# Concurrent part
#

def _producer(ranges):
    """Produces jobs for worker"""
    ctx = zmq.Context()
    # Socket to send messages to workers
    worker = ctx.socket(zmq.PUSH)
    worker.bind("tcp://127.0.0.1:5557")
    for _range in ranges:
        # Send job to worker
        log.debug("Sending data to worker: {0}".format(_range))
        worker.send('RANGE:{0}-{1}'.format(*_range))

    log.info("No more data. Stopping workers.")
    for _ in xrange(NCPU):
        worker.send('FINISH')

def _worker(func, N):
    """Computes some function on specified range"""
    ctx = zmq.Context()

    # Socket to receive messages on
    producer = ctx.socket(zmq.PULL)
    producer.connect("tcp://127.0.0.1:5557")

    # Socket to send messages to
    consumer = ctx.socket(zmq.PUSH)
    consumer.connect("tcp://127.0.0.1:5558")

    # Process tasks forever
    while True:
        s = producer.recv()
        if s.startswith('RANGE:'):
            log.info("Worker recv'd RANGE from producer: {0}".format(s))
            _range = s.split(':', 1)[1]
            start, stop = [int(data) for data in _range.split('-', 1)]
            log.debug("Worker dataset: {0}-{1}, size: {2}".format(start, stop, stop - start))
            A = start
            while A <= stop:
                p,q = func(N, A)
                #print '|{0} - {1}| = {2}'.format(p*q, N, abs(p*q - N))
                if p*q == N:
                    # Send results to sink
                    consumer.send('DONE:{0},{1}'.format(p, q))
                    break
                A += 1
        elif s.startswith('FINISH'):
            consumer.send('FINISH')
            break
        else:
            log.debug("Worker recv'd UNKNOWN from producer: {0}".format(s))

def _consumer():
    ctx = zmq.Context()
    finished = 0

    # Sink socket for worker's data
    worker = ctx.socket(zmq.PULL)
    worker.bind("tcp://127.0.0.1:5558")
    while True:
        s = worker.recv()
        log.debug("Consumer recvied data from worker: {0}".format(s))
        if s.startswith('DONE:'):
            log.warning("One of workers finished with result: {0}".format(s))
            break
        elif s.startswith('FINISH'):
            finished += 1
            if finished == NCPU:
                log.critical("All workers exited without producing an result")
                break
        else:
            log.error("Consumer recv'd UNKNOWN data from worker : {0}".format(s))

def main():
    #
    # First part
    #

    N1 = mpz(179769313486231590772930519078902473361797697894230657273430081157732675805505620686985379449212982959585501387537164015710139858647833778606925583497541085196591615128057575940752635007475935288710823649949940771895617054361149474865046711015101563940680527540071584560878577663743040086340742855278549092581)
    p,q = func1(N1)
    assert(p*q == N1)
    log.warning("Smallest factor: {0}".format(min([p,q])))

    #
    # Second part
    #
    N2 = mpz(648455842808071669662824265346772278726343720706976263060439070378797308618081116462714015276061417569195587321840254520655424906719892428844841839353281972988531310511738648965962582821502504990264452100885281673303711142296421027840289307657458645233683357077834689715838646088239640236866252211790085787877)

    # Setup
    ranges = create_ranges(sqrt(N2), sqrt(N2) + 2**20, 10000)
    producer = Process(target=_producer, args=(ranges,))
    consumer = Process(target=_consumer)
    pool = [Process(target=_worker, args=(func2, N2)) for _ in range(NCPU)]
    # Compute
    for p in [producer, consumer] + pool:
        p.start()
    consumer.join()
    # Teardown
    producer.terminate()
    for p in pool:
        p.terminate()

    #
    # Third part
    #
    # TODO(SaveTheRbtz@): Do the math

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    (options, args) = parser.parse_args()

    main()
