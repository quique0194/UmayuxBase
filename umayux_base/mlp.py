import sys
import numpy as np
import theano
import theano.tensor as T
from theano import shared
from theano import function
import six.moves.cPickle as pickle

# theano.config.optimizer="None"


class MLP(object):
    def __init__(self, n_input, n_hidden, n_out, learning_rate=0.1):
        rng = np.random.RandomState(1234)
        self.W0 = shared(np.asarray(rng.uniform(0,1,(n_input, n_hidden)), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.W0")
        self.W1 = shared(np.asarray(rng.uniform(0,1,(n_hidden, n_out)), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.W1")
        self.b0 = shared(np.asarray(rng.uniform(0,1,n_hidden), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.b0")
        self.b1 = shared(np.asarray(rng.uniform(0,1,n_out), dtype=theano.config.floatX),
                    borrow=True,
                    name="self.b1")

        l0 = T.dmatrix("l0")
        l1 = T.nnet.sigmoid(T.dot(l0,self.W0) + self.b0)
        l2 = T.nnet.sigmoid(T.dot(l1,self.W1) + self.b1)

        x = l0
        y = T.dmatrix("y")
        err = T.sum((l2-y.T)**2)

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





if __name__ == "__main__":

    train_x = np.array([
        [0,0],
        [0,1],
        [1,0],
        [1,1],
    ], dtype=theano.config.floatX)

    train_y = np.array([[0,1,1,0]], dtype=theano.config.floatX)

    if len(sys.argv) == 2:
        print "... Loading model from file ", sys.argv[1]
        with open(sys.argv[1] , "rb") as f:
            mlp = pickle.load(f)
    else:
        print "... Creating model"
        mlp = MLP(2, 2, 1)

        print "... Training model"

        for i in xrange(50000):
            err = mlp.train(train_x, train_y)

        print "... Saving model"

        with open("xor_mlp.pkl", "wb") as f:
            pickle.dump(mlp, f)

    print "... Testing model"

    for i in zip(train_x, mlp.predict(train_x)):
        print i
