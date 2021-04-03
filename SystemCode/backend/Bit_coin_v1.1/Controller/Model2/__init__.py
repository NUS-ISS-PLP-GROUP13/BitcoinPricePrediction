import torch

# If there's a GPU available...
if torch.cuda.is_available():

    # Tell PyTorch to use the GPU.
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use the GPU:', torch.cuda.get_device_name(0))

# If not...
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")


from sklearn.preprocessing import normalize, MinMaxScaler
from sklearn.metrics import mean_squared_error

import torch
import torch.nn as nn
from torch.autograd import Variable

# Build model
input_dim = 4
hidden_dim_1 = 32
hidden_dim_2 = 64
hidden_dim_3 = 512
num_layers = 1
output_dim = 1


class BitcoinPrediction(nn.Module):
    def __init__(self, input_dim, hidden_dim_1, hidden_dim_2, hidden_dim_3, num_layers, output_dim):
        super(BitcoinPrediction, self).__init__()
        # neurons
        self.input_dim = input_dim

        self.hidden_dim_1 = hidden_dim_1

        self.hidden_dim_2 = hidden_dim_2

        self.hidden_dim_3 = hidden_dim_3

        self.num_layers = num_layers

        self.outpu_dim = output_dim

        self.lstm1 = nn.LSTM(input_dim, hidden_dim_1, num_layers, batch_first=True)

        self.lstm2 = nn.LSTM(hidden_dim_1, hidden_dim_2, num_layers, batch_first=True)

        self.dense = nn.Linear(hidden_dim_2, hidden_dim_3)

        self.fc = nn.Linear(hidden_dim_3, output_dim)

    def forward(self, X):
        # Initialize hidden state with zeros
        h1 = torch.zeros(self.num_layers, X.size(0), self.hidden_dim_1).requires_grad_()

        # Initialize cell state
        c1 = torch.zeros(self.num_layers, X.size(0), self.hidden_dim_1).requires_grad_()

        # Initialize hidden state with zeros
        h2 = torch.zeros(self.num_layers, X.size(0), self.hidden_dim_2).requires_grad_()

        # Initialize cell state
        c2 = torch.zeros(self.num_layers, X.size(0), self.hidden_dim_2).requires_grad_()

        output1, (h1, c1) = self.lstm1(X, (h1.detach(), c1.detach()))

        ouput2, (h2, c2) = self.lstm2(output1, (h2.detach(), c2.detach()))

        # just want last time step hidden states
        out = self.dense(ouput2[:, -1, :])

        out = self.fc(out)

        return out

model = BitcoinPrediction(input_dim=input_dim, hidden_dim_1=hidden_dim_1,hidden_dim_2 = hidden_dim_2,hidden_dim_3 = hidden_dim_3,output_dim=output_dim, num_layers=num_layers)

optimizer = torch.optim.Adam(model.parameters(), lr=0.01)


output_file = "D:\workspace\python\Bit_coin\Controller\Model2\.model_bitcoinprice_prediction.pth"

checkpoint = torch.load(output_file, map_location='cpu')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

import pandas as pd
import numpy as np
import math

from pickle import load
scaler = load(open('D:\workspace\python\Bit_coin\Controller\Model2\scaler.pkl', 'rb'))

predictionScalar = MinMaxScaler()
predictionScalar.min_ = scaler.min_[0]
predictionScalar.scale_ = scaler.scale_[0]

# need to dimension (1,1,4)
testD = [1021.750000, 1.018706, 27.000000, 351]

def reformat(input):
    testD = np.reshape(input,(1, 4))
    testD_scaled = scaler.transform(testD)
    testD = testD_scaled.reshape(1,1,4)
    x_test = torch.from_numpy(testD).type(torch.Tensor)
    return x_test

def predict(model,x):
    y = model(x)
    y = predictionScalar.inverse_transform(y.detach().numpy().reshape(1,-1))
    return y[0][0]


def price(model, x):
    x_ = reformat(x)
    y_ = predict(model, x_)
    return y_


# p_ = price(model, testD)

# print(p_)