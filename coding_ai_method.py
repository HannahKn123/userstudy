#Improtiere die relevanten Bibliotheken
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense , Dropout , Activation , Flatten , Conv2D , MaxPooling2D , BatchNormalization , GlobalAveragePooling2D
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.models import Sequential
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import MobileNetV2 , Xception , NASNetMobile , InceptionResNetV2
from keras.layers import Dense , Input , Dropout
from keras.models import Model
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import Adam , Nadam , Adagrad
from sklearn.metrics import classification_report , confusion_matrix
from sklearn.metrics import accuracy_score
from tensorboard.plugins.hparams import api as hp
import sklearn.metrics as metrics


