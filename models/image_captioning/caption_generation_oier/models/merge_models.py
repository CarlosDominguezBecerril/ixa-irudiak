from keras.models import Model
from keras.layers import Input, Dropout, Dense, Embedding, LSTM, add
from keras.utils import plot_model
from keras.callbacks import ModelCheckpoint


class MergeModel(object):
    def __init__(self, vocab_size, max_length):
        # feature extractor model
        inputs1 = Input(shape=(4096,))
        fe1 = Dropout(0.5)(inputs1)
        fe2 = Dense(256, activation='relu')(fe1)

        # sequence model
        inputs2 = Input(shape=(max_length,))
        se1 = Embedding(vocab_size, 256, mask_zero=True)(inputs2)
        se2 = Dropout(0.5)(se1)
        se3 = LSTM(256)(se2)

        # decoder model
        decoder1 = add([fe2, se3])
        decoder2 = Dense(256, activation='relu')(decoder1)
        outputs = Dense(vocab_size, activation='softmax')(decoder2)

        # tie it together [image, seq] [word]
        self.model = Model(inputs=[inputs1, inputs2], outputs=outputs)

        self.model.compile(loss='categorical_crossentropy', optimizer='adam')

    def summarize_model(self, directory='./'):
        # summarize model
        print(self.model.summary())
        #plot_model(self.model, to_file=directory+'model.png', show_shapes=True)

    def train(self, x_train, y_train,
              x_test, y_test, filepath='model-ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5'):
        # define checkpoint callback
        checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')

        # fit model
        self.model.fit(x_train, y_train, batch_size=128, epochs=20, verbose=1, callbacks=[checkpoint],
                       validation_data=(x_test, y_test))
