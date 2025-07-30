import numpy as np
from numpy.typing import NDArray
from rafael_nn.common import FloatArr

from rafael_nn.layer import Layer
from rafael_nn.lossfn import LossFunction
from rafael_nn.optimizer import Optimizer

np.random.seed(42)

class NeuralNetwork:
    # I like adding types. Its easier to know that what im doing will work, also easier to debug
    # want to update this to use functional programming
    layers: list[Layer]
    optimizer:Optimizer
    layers_output: list[NDArray[np.float64]]
    loss_fn:LossFunction

    def __init__(self, layers:list[Layer], optimizer:Optimizer, loss_fn:LossFunction):
        self.layers = layers
        self.optimizer = optimizer
        self.loss_fn = loss_fn

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self._forward(x)[0]

    def train(self, x_full: FloatArr, y_full:FloatArr, epochs = 1000, err = 1e-4):
        cur_err = np.inf
        self.optimizer.load_data(x_full,y_full)

        while epochs > 0 and cur_err > err:
            x, y = self.optimizer.get_batch()

            final = self(x)
            cur_err = self.loss_fn(final,y)
            all_dl_bias,all_dl_weights = self._backward(final, y)

            for i in range(len(self.layers)):
                layer = self.layers[i]
                layer.biases = self.optimizer(layer.biases,all_dl_bias[i])
                layer.weights = self.optimizer(layer.weights,all_dl_weights[i])
            epochs-=1

    def backward(self, prediction:FloatArr, target:FloatArr) -> tuple[list[FloatArr],list[FloatArr]]:
        return self._backward(prediction,target)

    # this is almos the same implementation as the 7_2 notebook
    def _forward(self, x: FloatArr) -> tuple[FloatArr, list[FloatArr], list[FloatArr]]:
        all_h, all_f = [], []
        # all layers but the last one apply activation fn
        for i in range(len(self.layers) - 1):
            layer = self.layers[i]
            h, f = layer(x if i == 0 else all_h[i-1])

            all_h.append(h)
            all_f.append(f)

        # last layer outputs result y
        _,res = self.layers[-1](all_h[-1])
        all_f.append(res)

        return res, all_h, all_f

    # THIS IS AN IMPLEMENTATION OF GRADIENT DESCEND
    def _backward(self, prediction:FloatArr, target:FloatArr) -> tuple[list[FloatArr],list[FloatArr]]:
        layers_n = len(self.layers)
        all_dl_bias, all_dl_weights = [np.array([])] * layers_n, [np.array([])] * layers_n

        dl_b, prev_dl_f, dl_w = self.layers[-1].backward(prev_dl_f=self.loss_fn.backward(prediction,target))
        all_dl_bias[-1] = dl_b
        all_dl_weights[-1] = dl_w

        for lay in range(layers_n - 2,-1,-1):
            # here had an anoying error because prev_w was already transposed on this line
            prev_w = self.layers[lay+1].weights
            dl_b, prev_dl_f, dl_w = self.layers[lay].backward(weights_dl_f=prev_w.T @ prev_dl_f)

            all_dl_bias[lay] = dl_b
            all_dl_weights[lay] = dl_w

        return all_dl_bias, all_dl_weights

