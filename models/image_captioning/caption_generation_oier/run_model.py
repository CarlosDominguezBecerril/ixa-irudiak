import numpy as np

from pickle import load

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model

from models.image_captioning.caption_generation_oier.datasets.image_utils import extract_features_single_photo

import keras.backend.tensorflow_backend as tb

TOKENIZER = "./models/image_captioning/caption_generation_oier/tokenizer.pkl"
MAX_LENGTH = 34
BEST_MODEL = "./models/image_captioning/caption_generation_oier/model-ep004-loss3.166-val_loss3.642.h5"

def word_for_id(integer, tokenizer):
    """
    map an integer to a word
    :param integer:
    :param tokenizer:
    :return:
    """
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None

def generate_desc(model, tokenizer, photo, max_length):
    """
    generate a description for an image
    :param model:
    :param tokenizer:
    :param photo:
    :param max_length:
    :return:
    """
    # seed the generation process
    in_text = 'startseq'
    # iterate over the whole length of the sequence
    for _ in range(max_length):
        # integer encode input sequence
        sequence = tokenizer.texts_to_sequences([in_text])[0]

        # pad input
        sequence = pad_sequences([sequence], maxlen=max_length)

        # predict next word
        yhat = model.predict([photo, sequence], verbose=0)
        # convert probability to integer
        yhat = np.argmax(yhat)
        # map integer to word
        word = word_for_id(yhat, tokenizer)

        # stop if we cannot map the word
        if word is None:
            break

        # append as input for generating the next word
        in_text += ' ' + word

        # stop if we predict the end of the sequence
        if word == 'endseq':
            break
    return in_text

def run_model(image_path: str, model_values: dict):

    # To fix keras error: AttributeError: ‘_thread._local’ object has no attribute ‘value’
    tb._SYMBOLIC_SCOPE.value = True
    
    if "tokenizer" not in model_values:
        return "Error, tokenizer not found"

    # Load tokenizer
    tokenizer = load(open(model_values["tokenizer"], 'rb'))

    if "max_length" not in model_values:
        return "Error, max_length not found"
    max_length = model_values["max_length"]

    # Load model
    if "best_model" not in model_values:
        return "Error, best_model not found"
    model = load_model(model_values["best_model"])

    # load and prepare the photograph
    photo = extract_features_single_photo(image_path)

    # generate description
    description = generate_desc(model, tokenizer, photo, max_length)

    # Remove "startseq" and "endseq" words
    return description[9:-7]