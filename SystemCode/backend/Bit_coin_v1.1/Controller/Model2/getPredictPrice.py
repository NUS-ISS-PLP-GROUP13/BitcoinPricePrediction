
from Controller.Model2 import model as model, price
from Controller.close_price.getPrice import getPrice
from Controller.trends.getTrendByDate import getTrend


def do_model2(score, close_price, number, trend):
    testD= [close_price, score, trend, number]
    p = price(model, testD)
    return p

def get_radio(predict_price, close_price):
    flag = True
    close_price = float(close_price)
    if predict_price < close_price:
        flag = False
        ratio = str(round(predict_price/close_price, 2)) + "%"
    else:
        ratio = str(round(close_price/predict_price, 2)) + "%"
    print(flag)
    print(ratio)
    return flag, ratio


def getPridictPrice(date_input, score, number):
    tr = getTrend(date_input)
    trend = tr[0][0]
    close = getPrice(date_input)
    close_price = close[0][0]
    res = do_model2(score, close_price, number, trend)
    res_new = float(res)
    print(res_new)
    flag, ratio = get_radio(res_new, close_price)
    return res_new, close_price, flag, ratio, number, trend

# getPridictPrice('2020-09-09', -0.8115406632423401, 101)