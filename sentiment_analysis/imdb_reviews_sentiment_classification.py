import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
from tflearn.datasets import imdb

#Load IMDB review dataset, split into train, test, and validation sets
#load_data downloads data from the web, path defines where we want to save it
#pkl is a bytestream
#10% of training set for validation
train, test, _ = imdb.load_data(path='imdb.pkl', n_words=10000, valid_portion=0.1)

#split into reviews and labels
trainX, trainY = train
testX, testY = train

#Preprocess the data
#need to convert to numerical data
#not sure why need to pad_sequences or how it works
trainX = pad_sequences(trainX, maxlen=100, value=0.)
testX = pad_sequences(testX, maxlen=100, value=0.)

#convert labels to binary vectors
trainY = to_categorical(trainY, nb_classes=2)
testY = to_categorical(testY, nb_classes=2)

#build the network
net = tflearn.input_data([None, 100]) #specify the input's shape: batch size is None, length is 100 (because that is what we specified our max sequence length to be)
net = tflearn.embedding(net, input_dim=10000, output_dim=128) #10000 is number of words loaded from data, 128 is number of dimmensions of our resulting embeddings
net = tflearn.lstm(net, 128, dropout=0.8) #feed to lstm layer which will be able to remember since the beginning, dropout 0.8 helps prevent overfitting by randomly turning on and off layers in out network (layers or nodes?)
net = tflearn.fully_connected(net, 2, activation='softmax') #fully connects every neuron in the last layer to this layer. helps to learn nonlinear combinations. 2 units, softmax turns vector into vector of output properties that sum to 1
net = tflearn.regression(net, optimizer='adam', learning_rate=0.0001) #adam performs gradient descent, categorical_crossentropy helps to find the difference between predicted output and actual output

#training
model = tflearn.DNN(net, tensorboard_verbose=0)
model.fit(trainX, trainY, validation_set(testX, testY), show_metric=True, batch_size=32) #show metric True allows us to see the accuracy metric overtime