import math
import random


def liniarity_of_expectation(n, b):
    b = float(b)
    
    def x(t):
        if t == 0:
            return float(n)
        pred = x(t - 1)
        return pred * (1 - 1.0/n) ** (b * (n + 1 - pred))

    return x

def straight_formula(n, b):
    b = float(b)

    def x(t):
        return n * (n + 1) / (n + math.e ** (b/n * (n + 1) * t))
    return x

def simulation(n, b, rounds):
    infected = set([0])  # node 0 is infected
    uninfected = set(range(1, n + 1))  # 1 to n NOT infected
    print 'round 0: %d' % len(uninfected)
    for i in xrange(1, rounds):
        for _ in xrange(len(infected)):
            for _ in xrange(b):
                rnode = random.randint(0, n)
                if rnode in uninfected:
                    uninfected.remove(rnode)
                    infected.add(rnode)
        print 'round %d: %d' % (i, len(uninfected))


n = 10000
b = 2
rounds = 16

print 'n = %d;  b = %d' % (n, b)
print
print 'COURSE FORMULA'
print '------------------------'
    
x1 = straight_formula(n, b)
for t in xrange(0, rounds):
    print 'round %d: %.1f' % (t, x1(t))

print
print 'LINIARITY OF EXPECTATION'
print '------------------------'

x0 = liniarity_of_expectation(n, b)
for t in xrange(0, rounds):
    print 'round %d: %.1f' % (t, x0(t))
    
print
print 'SIMULATION'
print '------------'
simulation(n, b, rounds)
