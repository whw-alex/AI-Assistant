import shutil
import sys
import os


sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(__file__)+"\LeNet_PyTorch_initial")
sys.path.append(os.path.dirname(__file__)+"/LeNet_PyTorch_initial")

from inference import *


def image_classification(file):
    print('here')
    if not os.path.exists(file):
        raise ValueError(f'image_path is invalid: {file}')
    shutil.copy(file, r'mnist.png')
    label = predict(r'mnist.png')
    print(label)
    return label

if __name__ == '__main__':
    label = predict(r'mnist.png')
    print(label)