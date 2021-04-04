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
    return render_template("show2017.html")

@app.route('/show2017')
def get_show2017():
    return render_template("show2017.html")

@app.route('/show2018')
def get_show2018():
    return render_template("show2018.html")

@app.route('/show2019')
def get_show2019():
    return render_template("show2019.html")

@app.route('/show2020')
def get_show2020():
    return render_template("show2020.html")

@app.route('/all')
def get_all():
    return render_template("ldamodelviz.html")

@app.route('/2017')
def get_2017():
    return render_template("topic/ldamodelviz_2017.html")

@app.route('/2018')
def get_2018():
    return render_template("topic/ldamodelviz_2018.html")

@app.route('/2019')
def get_2019():
    return render_template("topic/ldamodelviz_2019.html")

@app.route('/2020')
def get_2020():
    return render_template("topic/ldamodelviz_2020.html")


@app.route('/submit_data_choosed',methods=['post'])
def get_data_choosed():
    print(request.form['date'])
    date = request.form['date']
    # res = getDataFromDB.selectComment(request.form['data'])
    score, number = get_score_from_DB(date)
    flag, ratio, res, close_price, number, tread = getPridictPrice(date, score, number)
    data = []
    data.append(res)
    data.append(close_price)
    data.append(flag)
    data.append(ratio)
    data.append(number)
    data.append(tread)
    data.append(date)
    print(data)
    return render_template("trading1.html", data=data)

if __name__ == '__main__':
    app.run()
