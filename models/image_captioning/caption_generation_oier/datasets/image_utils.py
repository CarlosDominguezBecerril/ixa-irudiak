from os import listdir
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from pickle import load


# extract features from each photo in the directory
def extract_features(directory, target_size=(224, 224), model_name='vgg16'):
    # load the model
    model = None
    if model_name == 'vgg16':
        model = VGG16()
    else:
        model = VGG16()

    # re-structure the model
    model.layers.pop()
    model = Model(inputs=model.inputs, outputs=model.layers[-1].output)

    # summarize
    print(model.summary())

    # extract features from each photo
    features = dict()
    for name in listdir(directory):
        # load an image from file
        filename = directory + '/' + name
        image = load_img(filename, target_size=target_size)

        # convert the image pixels to a numpy array
        image = img_to_array(image)

        # reshape data for the model
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))

        # prepare the image for the VGG model
        image = preprocess_input(image)

        # get features
        feature = model.predict(image, verbose=0)

        # get image id
        image_id = name.split('.')[0]

        # store feature
        features[image_id] = feature
        print('>%s' % name)
    return features


def extract_features_single_photo(filename, target_size=(224, 224), model_name='vgg16'):
    """
    Extract features from a photo in the directory

    :param filename:
    :param target_size:
    :param model_name:
    :return:
    """
    # load model
    model = None
    if model_name == 'vgg16':
        model = VGG16()
    else:
        model = VGG16()

    # re-structure the model
    model.layers.pop()
    model = Model(inputs=model.inputs, outputs=model.layers[-1].output)
    # load the photo
    image = load_img(filename, target_size=target_size)
    # convert the image pixels to a numpy array
    image = img_to_array(image)
    # reshape data for the model
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    # prepare the image for the VGG model
    image = preprocess_input(image)
    # get features
    feature = model.predict(image, verbose=0)
    return feature


def load_photo_features(filename, dataset):
    """
    load photo features
    :param filename:
    :param dataset:
    :return:
    """
    # load all features
    all_features = load(open(filename, 'rb'))
    # filter features
    features = {k: all_features[k] for k in dataset}
    return features
