"""
Expert tester for the vgg19_trainable
"""
import time
import tensorflow as tf
import utils
import os
from vgg import vgg19_trainable_skin as vgg19
from datasetTools import Dataset

# GLOBAL VARIABLES
path = '../data/ISB2016/'
path_dir_image = path + "images/"
path_list_labels = path + 'synset_skin.txt'
path_load_weight = 'weight/vgg19.npy'
path_save_weight = 'weight/save_1.npy'

# VARIABLES MODEL
path_data_train = path + 'ISB_Train.csv'
path_data_test = path + 'ISB_Test.csv'
mini_batch_train = 10
mini_batch_test = 10
epoch = 2
num_class = 2
learning_rate = 0.05
load_weight_fc = False

# VALIDATE INPUT DATA
# assert (total_images / mini_batch).is_integer(), 'El minibatch debe ser multiplo del total de datos de entrada'
assert os.path.exists(path), 'No existe el directorio de datos ' + path
assert os.path.exists(path_list_labels), 'No existe el archivo con la lista de labels ' + path_list_labels
assert os.path.exists(path_data_train), 'No existe el archivo con los datos de entrenamiento ' + path_data_train
assert os.path.exists(path_data_test), 'No existe el archivo con los datos de pruebas ' + path_data_test
# assert os.path.exists(path_load_weight), 'No existe el archivo con pesos ' + path_load_weight


def test_model(sess_test, objData):

    total = objData.total_images
    mbach = objData.minibatch
    itertotal = int(total/mbach)
    accuracy = 0

    print('\n# PHASE: Test classification')
    for i in range(itertotal):
        batch, label = objData.generate_batch()
        prob = sess_test.run(vgg.prob, feed_dict={vgg_batch: batch, train_mode: False})
        # utils.print_prob_all(prob, path_list_labels, top=0)
        accuracy = accuracy + utils.print_accuracy(label, prob)
        objData.next_batch()

    accuracy_final = accuracy/itertotal
    print('    Accuracy total: ', str(accuracy_final))

    return accuracy_final


def train_model(sess_train, objData):

    total = objData.total_images
    cost = tf.reduce_mean((vgg.prob - vgg_label) ** 2)
    train = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    print('\n# PHASE: Training model')
    t0 = time.time()
    for i in range(epoch):
        batch, label = objData.generate_batch()

        # Generate the 'one hot' or labels
        label = tf.one_hot([li for li in label], on_value=1, off_value=0, depth=num_class)
        label = list(sess_train.run(label))
        # Run training
        t_start = time.time()
        sess_train.run(train, feed_dict={vgg_batch: batch, vgg_label: label, train_mode: True})
        t_end = time.time()
        # Next slice batch
        objData.next_batch()
        print("    Iteration: %d train on batch time: %7.3f seg." % (i, (t_end - t_start)))

    t1 = time.time()
    print("    Batch size: %d" % total)
    print("    Iterations: %d" % epoch)
    print("    Time per iteration: %7.3f seg." % ((t1 - t0) / epoch))


if __name__ == '__main__':

    # GENERATE DATA
    data_train = Dataset(path_data=path_data_train, path_dir_images=path_dir_image, minibatch=mini_batch_train)
    data_test = Dataset(path_data=path_data_test, path_dir_images=path_dir_image, minibatch=mini_batch_test)
    accuracy = 0

    with tf.Session() as sess:

        # DEFINE MODEL
        vgg_batch = tf.placeholder(tf.float32, [None, 224, 224, 3])
        vgg_label = tf.placeholder(tf.float32, [None, num_class])
        train_mode = tf.placeholder(tf.bool)

        # Initialize of the model VGG19
        vgg = vgg19.Vgg19(path_load_weight, load_weight_fc=load_weight_fc)
        vgg.build(vgg_batch, train_mode)

        sess.run(tf.global_variables_initializer())
        test_model(sess_test=sess, objData=data_test)
        train_model(sess_train=sess, objData=data_train)
        accuracy = test_model(sess_test=sess, objData=data_test)

        # SAVE LOG:
        utils.write_log(total_data=data_train.total_images,epoch=epoch,m_batch=mini_batch_train,l_rate=learning_rate,accuracy=accuracy,file_npy=path_load_weight)

        # SAVE WEIGHTs
        vgg.save_npy(sess, path_save_weight)
