from detector.layers import Layer
import numpy as np

class Processor:
    def __init__(self):
        self.layers : list[Layer] = []

    def addLayer(self, layer : Layer):
        self.layers.append(layer)

    def check(self, chunk : np.ndarray, offset : float):
        data = chunk
        result = False
        data_dict = {"offset" : offset}
        for layer in self.layers:
            result, data, props = layer.process(data)
            data_dict.update(props)
            if not result:
                break
        return result, data_dict