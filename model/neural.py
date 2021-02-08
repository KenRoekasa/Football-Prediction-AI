import time

import numpy as np
import tensorflow as tf

from data_preparation.dataloader import load_premier_league_data

gpus = tf.config.experimental.list_physical_devices('GPU')

try:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
except RuntimeError as e:
    print(e)
NAME = 'model-%d' % int(time.time())
tensorboard = tf.keras.callbacks.TensorBoard(log_dir="logs/{}".format(NAME))


def prepare_data():
    training_data = load_premier_league_data()  # Get premier league data
    # random.shuffle(training_data)
    x = []  # features set
    y = []  # label set
    for features, label in training_data:
        x.append(features)
        y.append(label)
    X = np.array(x)
    X = X / X.max(axis=0)
    # print(X[0])
    y = np.array(y)
    # X = tf.keras.utils.normalize(X, axis=1)
    return X, y


x_train, y_train = prepare_data()
# x_test, y_test = prepare_data()

model = tf.keras.models.Sequential()

model.add(tf.keras.layers.Dense(64, activation=tf.nn.relu, input_dim=46))
model.add(tf.keras.layers.Dense(128, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(256, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(256, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(128, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(64, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(16, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(3, activation=tf.nn.softmax))


# plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
opt = tf.keras.optimizers.SGD(lr=0.001)
# opt = tf.keras.optimizers.Adam(lr=0.05)
model.compile(optimizer=opt, loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=100, batch_size=10, shuffle=True, callbacks=[tensorboard])

# val_loss, val_acc = model.evaluate(x_test, y_test)
# print(val_loss, val_acc)
#
# random_game = get_random_game("../data/whoscored/premierleague-20182019.csv")
# print(random_game)
# test_game = np.array(random_game[4])
# print(test_game)
# predictions = model.predict(np.array([test_game]))
# print(predictions)