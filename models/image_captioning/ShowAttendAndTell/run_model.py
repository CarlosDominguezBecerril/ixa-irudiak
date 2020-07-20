from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import tensorflow as tf

# You'll generate plots of attention in order to see which parts of an image
# our model focuses on during captioning
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Scikit-learn includes many helpful utilities
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

import nltk.translate.bleu_score as bs

# añadido
from keras.preprocessing.text import tokenizer_from_json

import re
import numpy as np
import os
import time
import json
from glob import glob
from PIL import Image
import pickle
import random


def run_model(image_path: str, model_values: dict):
    ################################################
    # IMAGE FEATURE EXTRACTOR
    ################################################

    # Next, you will use InceptionV3 (which is pretrained on Imagenet) to classify each image.
    # You will extract features from the last convolutional layer.
    # First, you will convert the images into InceptionV3's expected format by: * Resizing the image to 299px by 299px *
    # Preprocess the images using the preprocess_input method to normalize the image so that it contains pixels in the range of -1 to 1,
    # which matches the format of the images used to train InceptionV3.
    def load_image(image_path):
        img = tf.io.read_file(image_path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, (299, 299))
        img = tf.keras.applications.inception_v3.preprocess_input(img)
        return img, image_path

    # Now you'll create a tf.keras model where the output layer is the last convolutional layer in the InceptionV3 architecture.
    # The shape of the output of this layer is 8x8x2048. You use the last convolutional layer because you are using attention in this example.
    # You don't perform this initialization during training because it could become a bottleneck.

    # You forward each image through the network and store the resulting vector in a dictionary (image_name --> feature_vector).
    # After all the images are passed through the network, you pickle the dictionary and save it to disk.
    image_model = tf.keras.applications.InceptionV3(include_top=False,
                                                    weights='imagenet')
    new_input = image_model.input
    hidden_layer = image_model.layers[-1].output

    image_features_extract_model = tf.keras.Model(new_input, hidden_layer)

    ################################################
    # TOKENIZER
    ################################################
    with open(model_values['tokenizer']) as f:
        data = json.load(f)
        tokenizer = tokenizer_from_json(data)

    ################################################
    # INFORMACION DEL MODELO
    ################################################

    # Esto lo he puesto yo
    max_length = model_values['max_length']
    vocab_size = model_values['num_words']
    units = model_values['units']
    embedding_dim = model_values['embedding_dim']
    attention_features_shape = model_values['attention_features_shape']
    checkpoint_dir = model_values['checkpoint_dir']

    ################################################
    # MODEL
    ################################################

    # Model
    # Fun fact: the decoder below is identical to the one in the example for Neural Machine Translation with Attention.

    # The model architecture is inspired by the Show, Attend and Tell paper.

    # In this example, you extract the features from the lower convolutional layer of InceptionV3 giving us a vector of shape (8, 8, 2048).
    # You squash that to a shape of (64, 2048).
    # This vector is then passed through the CNN Encoder (which consists of a single Fully connected layer).
    # The RNN (here GRU) attends over the image to predict the next word.

    # BahdanauAttention -> TODO: Understand the context_vector size
    class BahdanauAttention(tf.keras.Model):
        def __init__(self, units):
            super(BahdanauAttention, self).__init__()
            self.W1 = tf.keras.layers.Dense(units)
            self.W2 = tf.keras.layers.Dense(units)
            self.V = tf.keras.layers.Dense(1)

        def call(self, features, hidden):
            # features(CNN_encoder output) shape == (batch_size, 64, embedding_dim) -> embedding_dim = 256

            # hidden shape == (batch_size, hidden_size) -> hidden_size = 512
            # hidden_with_time_axis shape == (batch_size, 1, hidden_size)
            hidden_with_time_axis = tf.expand_dims(hidden, 1)

            # score shape == (batch_size, 64, hidden_size)
            score = tf.nn.tanh(self.W1(features) +
                               self.W2(hidden_with_time_axis))

            # attention_weights shape == (batch_size, 64, 1)
            # you get 1 at the last axis because you are applying score to self.V
            attention_weights = tf.nn.softmax(self.V(score), axis=1)

            # context_vector shape after sum == (batch_size, hidden_size) -> This is not correct! Its shape is (batch_size, 256)
            # This should be shape == (batch_size, 64, 256)
            context_vector = attention_weights * features
            context_vector = tf.reduce_sum(context_vector, axis=1)

            return context_vector, attention_weights

    # CNN_encoder -> NOTE: Take into account that if a Dense layer is applied to a tensor of shape (batch, n, m)
    # it is applied on the third dimension, thus the output would be (batch, n, units(Dense))
    class CNN_Encoder(tf.keras.Model):
        # Since you have already extracted the features and dumped it using pickle
        # This encoder passes those features through a Fully connected layer
        def __init__(self, embedding_dim):
            super(CNN_Encoder, self).__init__()
            # shape after fc == (batch_size, 64, embedding_dim)
            self.fc = tf.keras.layers.Dense(embedding_dim)

        def call(self, x):
            x = self.fc(x)
            x = tf.nn.relu(x)
            x = tf.keras.layers.Dropout(0.5)(x)  # NOTE: Test dropout
            return x

    # RNN_Decoder
    class RNN_Decoder(tf.keras.Model):
        def __init__(self, embedding_dim, units, vocab_size):
            super(RNN_Decoder, self).__init__()
            self.units = units

            self.embedding = tf.keras.layers.Embedding(
                vocab_size, embedding_dim)
            self.gru = tf.keras.layers.GRU(self.units,
                                           return_sequences=True,
                                           return_state=True,
                                           recurrent_initializer='glorot_uniform')
            self.fc1 = tf.keras.layers.Dense(self.units)
            self.fc2 = tf.keras.layers.Dense(vocab_size)

            self.attention = BahdanauAttention(self.units)

        def call(self, x, features, hidden):
            # defining attention as a separate model
            context_vector, attention_weights = self.attention(
                features, hidden)

            # x shape after passing through embedding == (batch_size, 1, embedding_dim)
            x = self.embedding(x)

            # x shape after concatenation == (batch_size, 1, embedding_dim + hidden_size)
            # x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)
            x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)
            # passing the concatenated vector to the GRU
            output, state = self.gru(x)

            # shape == (batch_size, max_length, hidden_size)
            x = self.fc1(output)
            x = tf.keras.layers.Dropout(0.5)(x)  # NOTE: Test dropout

            # x shape == (batch_size * max_length, hidden_size)
            x = tf.reshape(x, (-1, x.shape[2]))

            # output shape == (batch_size * max_length, vocab)
            x = self.fc2(x)

            return x, state, attention_weights

        def reset_state(self, batch_size):
            return tf.zeros((batch_size, self.units))

    # Instantiate the model
    print("Building the encoder-decoder model")
    encoder = CNN_Encoder(embedding_dim)
    decoder = RNN_Decoder(embedding_dim, units, vocab_size)
    optimizer = tf.keras.optimizers.Adam()
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
    checkpoint = tf.train.Checkpoint(optimizer=optimizer, encoder=encoder, decoder=decoder)
    status = checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))

    def plot_attention(image, result, attention_plot):
        temp_image = np.array(Image.open(image))

        fig = plt.figure(figsize=(10, 10))

        len_result = len(result)
        for l in range(len_result):
            temp_att = np.resize(attention_plot[l], (8, 8))
            ax = fig.add_subplot(len_result//2, len_result//2, l+1)
            ax.set_title(result[l])
            img = ax.imshow(temp_image)
            ax.imshow(temp_att, cmap='gray', alpha=0.6, extent=img.get_extent())

        plt.tight_layout()
        img = image.split("/")[-1].split(".")
        path =  model_values["attention_dir"] + "/" + img[0] + "img_plot." +img[1]
        plt.savefig(path)
        return path


    # Evaluation function
    def evaluate(image):
        attention_plot = np.zeros((max_length, attention_features_shape))

        hidden = decoder.reset_state(batch_size=1)

        temp_input = tf.expand_dims(load_image(image)[0], 0)
        img_tensor_val = image_features_extract_model(temp_input)
        img_tensor_val = tf.reshape(
            img_tensor_val, (img_tensor_val.shape[0], -1, img_tensor_val.shape[3]))

        features = encoder(img_tensor_val)

        dec_input = tf.expand_dims([tokenizer.word_index['<start>']], 0)
        result = []

        for i in range(max_length):
            predictions, hidden, attention_weights = decoder(
                dec_input, features, hidden)

            attention_plot[i] = tf.reshape(attention_weights, (-1, )).numpy()

            predicted_id = tf.argmax(predictions[0]).numpy()
            result.append(tokenizer.index_word[predicted_id])

            if tokenizer.index_word[predicted_id] == '<end>':
                return result, attention_plot

            dec_input = tf.expand_dims([predicted_id], 0)

        attention_plot = attention_plot[:len(result), :]
        return result, attention_plot

    output = evaluate(image_path)
    real_output = [" ".join(output[0][:-1]), "../" + plot_attention(image_path, output[0], output[1])]
    return real_output
