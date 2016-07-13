import sys
import numpy as np
import theano
import theano.tensor as T
from theano import shared
from theano import function
import six.moves.cPickle as pickle

# theano.config.optimizer="None"


class MLP(object):
    def __init__(self, n_input, n_hidden, n_out, learning_rate=0.25):
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_out = n_out
        self.learning_rate = learning_rate

        rng = np.random.RandomState(1234)
        self.W0 = shared(np.asarray(rng.uniform(-1,1,(n_input, n_hidden)), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.W0")
        self.W1 = shared(np.asarray(rng.uniform(-1,1,(n_hidden, n_out)), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.W1")
        self.b0 = shared(np.asarray(rng.uniform(-1,1,n_hidden), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.b0")
        self.b1 = shared(np.asarray(rng.uniform(-1,1,n_out), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.b1")

        l0 = T.dmatrix("l0")
        # l1 = T.tanh(T.dot(l0,self.W0) + self.b0)
        l1 = T.dot(l0,self.W0) + self.b0
        l2 = T.tanh(T.dot(l1,self.W1) + self.b1)

        x = l0
        y = T.dmatrix("y")
        err = T.sum((l2-y)**2) + 0.01*(abs(self.W0).sum() + abs(self.W1).sum())

        g_W0 = T.grad(err, self.W0)
        g_W1 = T.grad(err, self.W1)
        g_b0 = T.grad(err, self.b0)
        g_b1 = T.grad(err, self.b1)
        self.train = function([x,y], err, updates=[
            (self.W0, self.W0-learning_rate*g_W0),
            (self.W1, self.W1-learning_rate*g_W1),
            (self.b0, self.b0-learning_rate*g_b0),
            (self.b1, self.b1-learning_rate*g_b1),
        ])
        self.predict = function([x], l2)

    def clone(self):
        clon = MLP(self.n_input, self.n_hidden, self.n_out, self.learning_rate)
        clon.W0.set_value(self.W0.get_value())
        clon.W1.set_value(self.W1.get_value())
        clon.b0.set_value(self.b0.get_value())
        clon.b1.set_value(self.b1.get_value())
        return clon




if __name__ == "__main__":

    train_x = np.array([
        [0,0],
        [0,1],
        [1,0],
        [1,1],
    ], dtype=theano.config.floatX)

    train_y = np.array([
        [0,0],
        [1,0],
        [1,0],
        [0,1]
    ], dtype=theano.config.floatX)

    if len(sys.argv) == 2:
        print "... Loading model from file ", sys.argv[1]
        with open(sys.argv[1] , "rb") as f:
            mlp = pickle.load(f)
    else:
        print "... Creating model"
        mlp = MLP(2, 4, 2)

        print "... Training model"

        for i in xrange(10000):
            err = mlp.train(train_x, train_y)

        print "... Saving model"

        with open("xor_mlp.pkl", "wb") as f:
            pickle.dump(mlp, f)

    print "... Testing model"

    for i in zip(train_x, mlp.predict(train_x)):
        print i
