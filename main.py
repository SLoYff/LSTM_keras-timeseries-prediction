import numpy
import pandas
import matplotlib.pyplot as plt

from keras.layers import Dense, LSTM, Dropout,SimpleRNN
from keras.models import Sequential
from sklearn.metrics import mean_squared_error
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from tqdm import trange
from keras import optimizers

# fix random seed for reproducibility
#https://blog.csdn.net/aliceyangxi1987/article/details/73420583   对程序的说明
numpy.random.seed(4)

sgd = optimizers.SGD(lr = 0.001,clipnorm = 1.0, momentum=0.0, decay=0.0, nesterov=False)
adam1 = optimizers.Adam(lr=0.0001, clipvalue=0.5,beta_1=0.9, beta_2=0.999, epsilon=1e-08)
lr=0.001
def load_dataset(datasource: str) -> (numpy.ndarray, MinMaxScaler):
    """
    The function loads dataset from given `file name and uses MinMaxScaler to transform data
    :param datasource: file name of data source
    :return: tuple of dataset and the used MinMaxScaler
    该函数从给定的文件名称加载数据集，并使用MinMaxScaler来转换数据
     ：param datasource：数据源的文件名
     ：return：数据集的元组和使用的MinMaxScaler
    """
    # load the dataset
    dataframe = pandas.read_csv(datasource, usecols=[0])
    dataframe = dataframe.fillna(method='pad')
    dataset = dataframe.values
    dataset = dataset.astype('float64')

    #plt.plot(dataset)
    #plt.show()

    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    return dataset, scaler


def create_dataset(dataset: numpy.ndarray, look_back: int=1) -> (numpy.ndarray, numpy.ndarray):
    """
    The function takes two arguments: the `dataset`, which is a NumPy array that we want to convert into a dataset,
    and the `look_back`, which is the number of previous time steps to use as input variables
    to predict the next time period — in this case defaulted to 1.
    :param dataset: numpy dataset
    :param look_back: number of previous time steps as int
    :return: tuple of input and output dataset
    该函数有两个参数：`dataset`，它是一个我们想要转换成数据集的NumPy数组，
     和`look_back`，这是以前用作输入变量的时间步数
     预测下一个时间段 - 在这种情况下默认为1。
     ：param dataset参数数据集：numpy数据集
     ：param look_back：以前的时间步数为int
     ：return：输入和输出数据集的元组
    """
    data_x, data_y = [], []
    for i in range(len(dataset)-look_back):
        a = dataset[i:(i+look_back), 0]
        data_x.append(a)
        data_y.append(dataset[i + look_back, 0])
    return numpy.array(data_x), numpy.array(data_y)


def split_dataset(dataset: numpy.ndarray, train_size, look_back) -> (numpy.ndarray, numpy.ndarray):
    """
    Splits dataset into training and test datasets. The last `look_back` rows in train dataset
    will be used as `look_back` for the test dataset.
    :param dataset: source dataset
    :param train_size: specifies the train data size
    :param look_back: number of previous time steps as int
    :return: tuple of training data and test dataset
    将数据集分成训练和测试数据集。 列车数据集中的最后一个`look_back`行
     将用作测试数据集的`look_back`。
     ：参数数据集：源数据集
     ：param train_size：指定列车数据大小
     ：param look_back：以前的时间步数为int
     ：返回：训练数据和测试数据集的元组
    """
    if not train_size > look_back:
        raise ValueError('train_size must be lager than look_back')
    train, test = dataset[0:train_size, :], dataset[train_size - look_back:len(dataset), :]
    print('train_dataset: {}, test_dataset: {}'.format(len(train), len(test)))
    return train, test


def build_model(look_back: int, batch_size: int=10) -> Sequential:
    """
    The function builds a keras Sequential model
    :param look_back: number of previous time steps as int
    :param batch_size: batch_size as int, defaults to 1
    :return: keras Sequential model
    该函数构建了一个keras Sequential模型
     ：param look_back：以前的时间步数为int
     ：参数batch_size：batch_size为int，默认值为1
     ：return：keras连续模型
    """
    model = Sequential()
    model.add(LSTM(256,
                   activation='relu',
                   batch_input_shape=(batch_size, look_back, 1),
                   stateful=True,
                   return_sequences=True))
    model.add(Dropout(0.7))
    model.add(LSTM(128,stateful=True,return_sequences=True))
    #model.add(Dropout(0.7))
    model.add(LSTM(64,stateful=True))
    #model.add(LSTM(128,activation='relu',stateful=True,return_sequences=True))
    #model.add(LSTM(128,activation='relu',stateful=True,return_sequences=False))
    #model.add(LSTM(32,activation='relu',stateful=True,return_sequences=False))
    #model.add(Dropout(0.5))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer=adam1)
    return model


def plot_data(dataset: numpy.ndarray,
              look_back: int,
              train_predict: numpy.ndarray,
              test_predict: numpy.ndarray,
              forecast_predict: numpy.ndarray):
    """
    Plots baseline and predictions.

    blue: baseline
    green: prediction with training data
    red: prediction with test data
    cyan: prediction based on predictions

    :param dataset: dataset used for predictions
    :param look_back: number of previous time steps as int
    :param train_predict: predicted values based on training data
    :param test_predict: predicted values based on test data
    :param forecast_predict: predicted values based on previous predictions
    :return: None
    绘制基线和预测。

     蓝色：基准线
     绿色：用训练数据进行预测
     红色：用测试数据预测
     青色：基于预测的预测

     ：参数数据集：用于预测的数据集
     ：param look_back：以前的时间步数为int
     ：param train_predict：基于训练数据的预测值
     ：param test_predict：基于测试数据的预测值
     ：param forecast_predict：基于之前预测的预测值
     ：返回：无
    """
    plt.plot(dataset)
    plt.plot([None for _ in range(look_back)] +
             [x for x in train_predict])
    plt.plot([None for _ in range(look_back)] +
             [None for _ in train_predict] +
             [x for x in test_predict])
    plt.plot([None for _ in range(look_back)] +
             [None for _ in train_predict] +
             [None for _ in test_predict] +
             [x for x in forecast_predict])
    plt.show()


def make_forecast(model: Sequential, look_back_buffer: numpy.ndarray, timesteps: int=1, batch_size: int=1):
    forecast_predict = numpy.empty((0, 1), dtype=numpy.float64)
    for _ in trange(timesteps, desc='predicting data\t'):
#        look_back_buffer = numpy.reshape(look_back_buffer, (1,look_back_buffer.shape[0], look_back_buffer.shape[1]))
        # make prediction with current lookback buffer
        # 使用当前的回溯缓冲区进行预测         , mininterval=1
        cur_predict = model.predict(look_back_buffer, batch_size)
        # add prediction to result
        # 添加预测结果
        forecast_predict = numpy.concatenate([forecast_predict,cur_predict[-2:-1,:]], axis=0)
#        for x in range(99):
#            forecast_predict = numpy.delete(forecast_predict,-2,axis=0)

        # add new axis to prediction to make it suitable as input
        # 为预测添加新轴以使其适合作为输入
        cur_predict = numpy.reshape(cur_predict, (cur_predict.shape[0], cur_predict.shape[1], 1))
        # remove oldest prediction from buffer
        # 从缓冲区中移除最老的预测
        look_back_buffer = numpy.delete(look_back_buffer,0, axis=1)
        # concat buffer with newest prediction
        # 用最新预测连接缓冲器
        look_back_buffer = numpy.concatenate([look_back_buffer, cur_predict], axis=1)
    return forecast_predict


#def main():
datasource = 'test_5000_F_1000.csv'
#datasource = 'international-airline-passengers.csv'
dataset, scaler = load_dataset(datasource)

# split into train and test sets
# 分成训练集和测试集
look_back = int(len(dataset) * 0.20)
#look_back = 200
train_size = int(len(dataset) * 0.70)
train, test = split_dataset(dataset, train_size, look_back)

# reshape into X=t and Y=t+1
# 重塑为X = t和Y = t + 1
train_x, train_y = create_dataset(train, look_back)
test_x, test_y = create_dataset(test, look_back)

# reshape input to be [samples, time steps, features]
# 重塑输入为[样本，时间步骤，特征]
train_x = numpy.reshape(train_x, (train_x.shape[0], train_x.shape[1], 1))
test_x = numpy.reshape(test_x, (test_x.shape[0], test_x.shape[1], 1))

# create and fit Multilayer Perceptron model
# 创建并装配多层Perceptron模型
batch_size = 500
#batch_size = 1

model = load_model('temporary')   
#model = build_model(look_back, batch_size=batch_size)
#for _ in trange(100, desc='fitting model\t'):
#     model.fit(train_x, train_y, nb_epoch=1, batch_size=batch_size, verbose=2, shuffle=False)
#     model.reset_states()              # , mininterval=1.0

#history=model.fit(train_x, train_y, nb_epoch=30, batch_size=batch_size, verbose=2, shuffle=False) 
#model.reset_states()


# generate predictions for training
# 生成训练预测
train_predict = model.predict(train_x, batch_size)
test_predict = model.predict(test_x, batch_size)

# generate forecast predictions
# 生成预测预测

#forecast_predict = make_forecast(model, test_x[-1::], timesteps=100, batch_size=batch_size)
forecast_predict = make_forecast(model, test_x[-501:-1,:,:], timesteps=1000, batch_size=batch_size)

# invert dataset and predictions
# 反演数据集和预测
dataset = scaler.inverse_transform(dataset)
train_predict = scaler.inverse_transform(train_predict)
train_y = scaler.inverse_transform([train_y])
test_predict = scaler.inverse_transform(test_predict)
test_y = scaler.inverse_transform([test_y])
forecast_predict = scaler.inverse_transform(forecast_predict)

#保存临时模型
model.save('temporary')
# calculate root mean squared error
 # 计算均方根误差
train_score = numpy.sqrt(mean_squared_error(train_y[0], train_predict[:, 0]))
print('Train Score: %.2f RMSE' % train_score)
test_score = numpy.sqrt(mean_squared_error(test_y[0], test_predict[:, 0]))
print('Test Score: %.2f RMSE' % test_score)

plot_data(dataset, look_back, train_predict, test_predict, forecast_predict)

#if __name__ == '__main__':
#    main()
    #model = load_model('my_model.h5')