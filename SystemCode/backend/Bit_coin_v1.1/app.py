from flask import Flask, render_template, request
import Controller.SpiderByData.getDataFromDB as getDataFromDB
import Controller.Model1
import Controller.Model2
from Controller.Model1.getScore import get_score_from_DB
from Controller.Model2.getPredictPrice import getPridictPrice

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

# previews
@app.route('/form')
def get_form():
    return render_template("form.html")

@app.route('/exchange')
def get_exchange():
    return render_template("exchange.html")

@app.route('/show')
def get_show():
    return render_template("show.html")

@app.route('/submit_data_choosed',methods=['post'])
def get_data_choosed():
    print(request.form['date'])
    # res = getDataFromDB.selectComment(request.form['data'])
    score, number = get_score_from_DB(request.form['date'])
    flag, ratio, res, close_price, number, tread = getPridictPrice(request.form['date'], score, number)
    data = []
    data.append(res)
    data.append(close_price)
    data.append(flag)
    data.append(ratio)
    data.append(number)
    data.append(tread)
    print(data)
    return render_template("trading1.html", data=data)

if __name__ == '__main__':
    app.run()
