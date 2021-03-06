# Desc: This py script will override the default python_closure_container.py in clipper mmdet model container.
# Author: Zhou Shengsheng
# Date: 15-02-19

from __future__ import print_function
import rpc
import os
import sys
import cloudpickle
import pickle
import base64
from models.object.pretrained_imagenet import Img2Vec


IMPORT_ERROR_RETURN_CODE = 3

imagenet_model = Img2Vec(cuda=True)
print('imagenet_model:', imagenet_model)


def predict(serialized_image_bytes):
    global imagenet_model
    deserialized_image = pickle.loads(serialized_image_bytes)
    q_vec = imagenet_model.extract_vec(deserialized_image, True)
    serialized_pred = pickle.dumps(q_vec)
    base64_pred = base64.b64encode(serialized_pred).decode()
    return [base64_pred]

def load_predict_func(file_path):
    if sys.version_info < (3, 0):
        with open(file_path, 'r') as serialized_func_file:
            return cloudpickle.load(serialized_func_file)
    else:
        with open(file_path, 'rb') as serialized_func_file:
            return cloudpickle.load(serialized_func_file)


class PythonContainer(rpc.ModelContainerBase):
    def __init__(self, path, input_type):
        self.input_type = rpc.string_to_input_type(input_type)
        modules_folder_path = "{dir}/modules/".format(dir=path)
        sys.path.append(os.path.abspath(modules_folder_path))
        predict_fname = "func.pkl"
        predict_path = "{dir}/{predict_fname}".format(
            dir=path, predict_fname=predict_fname)
        # self.predict_func = load_predict_func(predict_path)
        self.predict_func = predict

    def predict_ints(self, inputs):
        preds = self.predict_func(inputs)
        return [str(p) for p in preds]

    def predict_floats(self, inputs):
        preds = self.predict_func(inputs)
        return [str(p) for p in preds]

    def predict_doubles(self, inputs):
        preds = self.predict_func(inputs)
        return [str(p) for p in preds]

    def predict_bytes(self, inputs):
        preds = self.predict_func(inputs)
        return [str(p) for p in preds]

    def predict_strings(self, inputs):
        preds = self.predict_func(inputs)
        return [str(p) for p in preds]


if __name__ == "__main__":
    print("Starting Python Closure container")
    rpc_service = rpc.RPCService()
    try:
        model = PythonContainer(rpc_service.get_model_path(),
                                rpc_service.get_input_type())
        sys.stdout.flush()
        sys.stderr.flush()
    except ImportError:
        sys.exit(IMPORT_ERROR_RETURN_CODE)
    rpc_service.start(model)
