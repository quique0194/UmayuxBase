import math
import theano
import theano.tensor as T
from theano import function
from theano import shared

s = shared(10.0)
inc = T.dscalar('inc')

f = function([inc], s, updates=[(s, s+inc)])

print f(5)
print s.get_value()