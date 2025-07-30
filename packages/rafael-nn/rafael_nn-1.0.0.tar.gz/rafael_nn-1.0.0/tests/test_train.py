import unittest
import numpy as np
from rafael_nn.common import FloatArr

from rafael_nn.layer import Linear
from rafael_nn.lossfn import MeanSquaredError
from rafael_nn.nn import NeuralNetwork
from rafael_nn.optimizer import GradientDescent, StochasticGradientDescend

# This is the same toy function used in the example of backprop in understanding deep learning
def teaching_function(beta: np.ndarray, omega: np.ndarray):
    def fn_x_only(x:FloatArr) -> FloatArr:
        return beta[3] + omega[3] * np.cos(
            beta[2] + omega[2] * np.exp(
                beta[1] + omega[1] * np.sin(
                    beta[0] + omega[0] * x
                )
            )
        )
    return fn_x_only

def create_dataset(size:int, fn):
    np.random.seed(42)

    x = np.linspace(-5, 5, size)
    y_clean = fn(x)
    y_noisy = y_clean + np.random.normal(0, 0.1, size=x.shape)  # add small noise

    return x.reshape((1,size)), y_noisy.reshape((1,size))

class TestNNTrain(unittest.TestCase):
    def setUp(self):
        beta = np.random.uniform(-1, 1, size=4)
        omega = np.random.uniform(-1, 1, size=4)

        np.random.seed(42)
        n_layers = 2
        n_by_layer = 6
        layers= [Linear(1,n_by_layer)] + [Linear(n_by_layer,n_by_layer) for _ in range(n_layers-1)] + [Linear(n_by_layer,1)]

        self.teaching_fn = teaching_function(beta,omega)
        self.loss_fn = MeanSquaredError()
        self.nn = NeuralNetwork(layers, optimizer=StochasticGradientDescend(), loss_fn=self.loss_fn)

    def test_train_correct_descend(self):
        x_train, y_train = create_dataset(10, self.teaching_fn)
        self.nn.train(x_train,y_train)
