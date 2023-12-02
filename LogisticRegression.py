import pandas as pd
import math
import numpy as np

ITER = 1000
lineIndex = 425

df = pd.read_csv("spotify_data.csv")
df = df.drop(['name'], axis=1)
X_train = df.drop(["followers"], axis=1)[:lineIndex]
y_train = df.get("followers")[:lineIndex]
X_test = df.drop(["followers"], axis=1)[lineIndex:]
y_test = df.get("followers")[lineIndex:]

def logistic_regression(X, y):
    numberOfSamples = X.shape[0]
    X = X.to_numpy()
    y = y.squeeze().to_numpy()
    w = np.zeros(X_train.shape[1] + 1)

    w = np.zeros(X.shape[1] + 1)

    for iter in range(ITER):
        pred = []

        for i in range(X.shape[0]):
            wTx = np.dot(X[i], w[1:]) + w[0]
            sig = 1.0/(1.0 + math.pow(math.e, -wTx))
            pred += [sig]

        pred = np.array(pred)
        dw = []
        for i in range(X.T.shape[0]):
            dw += [(1/numberOfSamples) * np.dot(X.T[i], (pred-y))]
        
        dw = np.array(dw)
        db = (1/X.shape[0]) * np.sum(pred-y)

        w[1:] = w[1:] - (0.001 * dw)
        w[0] = w[0] - (0.001 * db)
    
    return w


def predict(X, w):
    y_predict=[]
    pred = []
    for i in range(X.shape[0]):
        wTx = np.dot(X.iloc[i], w[1:]) + w[0]
        sig = 1.0/(1.0 + math.pow(math.e, -wTx))
        pred += [sig]
    
    for sig in pred:
        if(sig <= 0.5):
            y_predict += [0]
        else:
            y_predict += [1] 

    return y_predict

w = logistic_regression(X_train, y_train)

y_pred = predict(X_test, w)

print(y_pred)
y_testL = list(y_test.squeeze().to_numpy())
print(y_testL)

sum = 0
for i in range(len(y_pred)):
    if(y_pred[i] == y_testL[i]):
        sum += 1

print("Accuracy")
print(f"{sum/(len(y_pred) * 1.0)}%")