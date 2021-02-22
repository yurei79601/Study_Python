import os
import numpy as np
import tensorflow as tf
from model_utils import weight_variable, bias_variable, fc_layer
from data_manager import load_data, get_next_batch, randomize


class NeuralNetworkModel(object):
    def __init__(self, model_path, n_classes):
        self.epochs = 10  # Total number of training epochs
        self.batch_size = 100  # Training batch size
        self.display_freq = 100  # Frequency of displaying the training results
        self.learning_rate = 0.001  # The optimization initial learning rate
        self.h1 = 200  # number of nodes in the 1st hidden layer
        self.img_h, self.img_w = 28, 28
        self.img_size_flat = self.img_h * self.img_w
        self.n_classes = n_classes
        self.save_path = os.path.join(model_path, "twolayernetwork")
        self.session = tf.InteractiveSession()

        with self.session.as_default():
            (
                self.x,
                self.y,
                self.loss,
                self.optimizer,
                self.accuracy,
                self.cls_prediction,
                self.init,
            ) = self.model()
            self.init.run()

    def model(self):
        x = tf.placeholder(
            tf.float32, shape=[None, self.img_size_flat], name="X"
        )
        y = tf.placeholder(tf.float32, shape=[None, self.n_classes], name="Y")
        # Create a fully-connected layer with h1 nodes as hidden layer
        fc1 = fc_layer(x, self.h1, "FC1", use_relu=True)
        # Create a fully-connected layer with n_classes nodes as output layer
        output_logits = fc_layer(fc1, self.n_classes, "OUT", use_relu=False)
        # Define the loss function, optimizer, and accuracy
        loss = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(
                labels=y, logits=output_logits
            ),
            name="loss",
        )
        optimizer = tf.train.AdamOptimizer(
            learning_rate=self.learning_rate, name="Adam-op"
        ).minimize(loss)
        correct_prediction = tf.equal(
            tf.argmax(output_logits, 1), tf.argmax(y, 1), name="correct_pred"
        )
        accuracy = tf.reduce_mean(
            tf.cast(correct_prediction, tf.float32), name="accuracy"
        )

        # Network predictions
        cls_prediction = tf.argmax(output_logits, axis=1, name="predictions")
        init = tf.global_variables_initializer()
        return x, y, loss, optimizer, accuracy, cls_prediction, init

    def train(self):
        x_data, y_data, x_valid, y_valid = load_data("train")
        with self.session.as_default():
            print("Training")
            self.session.run(self.init)
            # Number of training iterations in each epoch
            num_tr_iter = int(len(y_data) / self.batch_size)
            for epoch in range(self.epochs):
                print("Training epoch: {}".format(epoch + 1))
                # Randomly shuffle the training data at the beginning of each epoch
                x_train, y_train = randomize(x_data, y_data)
                for iteration in range(num_tr_iter):
                    start = iteration * self.batch_size
                    end = (iteration + 1) * self.batch_size
                    x_batch, y_batch = get_next_batch(
                        x_train, y_train, start, end
                    )

                    # Run optimization op (backprop)
                    feed_dict_batch = {self.x: x_batch, self.y: y_batch}
                    self.session.run(self.optimizer, feed_dict=feed_dict_batch)

                    if iteration % self.display_freq == 0:
                        # Calculate and display the batch loss and accuracy
                        loss_batch, acc_batch = self.session.run(
                            [self.loss, self.accuracy],
                            feed_dict=feed_dict_batch,
                        )

                        print(
                            "iter {0:3d}:\t Loss={1:.2f},\tTraining Accuracy={2:.01%}".format(
                                iteration, loss_batch, acc_batch
                            )
                        )
                # Run validation after every epoch
                feed_dict_valid = {
                    self.x: x_valid[:1000],
                    self.y: y_valid[:1000],
                }
                loss_valid, acc_valid = self.session.run(
                    [self.loss, self.accuracy], feed_dict=feed_dict_valid
                )
                print(
                    "---------------------------------------------------------"
                )
                print(
                    "Epoch: {0}, validation loss: {1:.2f}, validation accuracy: {2:.01%}".format(
                        epoch + 1, loss_valid, acc_valid
                    )
                )
                print(
                    "---------------------------------------------------------"
                )

        saver = tf.train.Saver()
        saver.save(self.session, self.save_path, global_step=self.epochs)


if __name__ == "__main__":
    NN_Model = NeuralNetworkModel("./", 10)
    NN_Model.train()
