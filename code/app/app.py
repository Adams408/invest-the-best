import os
import pickle
import threading

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def meta_data():
    data = []
    if os.path.exists(os.path.join(DATA_DIR, "symbols.pkl")):
        with open(os.path.join(DATA_DIR, "symbols.pkl"), "rb") as f:
            symbols = pickle.load(f)

    for symbol in symbols:
        if os.path.exists(os.path.join(DATA_DIR, 'stock_data/{}'.format(symbol))) and not os.path.isfile(os.path.join(DATA_DIR, 'stock_data/{}'.format(symbol))):
            if os.listdir(os.path.join(DATA_DIR, 'stock_data/{}'.format(symbol))):
                with open(os.path.join(DATA_DIR, 'stock_data/{}/meta.pkl'.format(symbol)), "rb") as f:
                    meta = pickle.load(f)
                data.append(meta)

    return data


def names():
    _names = []
    for meta in meta_data():
        _names.append(meta.get('name'))
    return _names


@app.route('/')
def home():
    return render_template('home.html', names=names())


@app.route('/industry')
def industry():
    return render_template('industry.html', names=names())


@app.route('/company')
def company():
    return render_template('company.html', names=names())


@app.route('/select', methods=['POST'])
def select():
    for meta in meta_data():
        if meta.get('name') == request.form['name']:
            return jsonify(meta)


@app.route('/graph', methods=['POST'])
def graph():
    data_symbol = ''
    for meta in meta_data():
        if meta.get('name') == request.form['name']:
            data_symbol = meta.get('ticker')
    with open(os.path.join(DATA_DIR, 'stock_data/{}/{}.pkl'.format(data_symbol, data_symbol)), "rb") as f:
        data = pickle.load(f)
    with open(os.path.join(DATA_DIR, 'prediction_data/{}.pkl'.format(data_symbol)), "rb") as f:
        prediction = pickle.load(f)

    x = [['Date', 'Stock Price']]
    for day in data:
        x.append([day.get('date')[:day.get('date').index('T')], day.get('close')])
    for day in prediction:
        x.append([day.get('date')[:day.get('date').index('T')], day.get('close')])

    return jsonify({'x': x})


# class Scheduler(threading.Thread):
#
#     def __init__(self):
#         threading.Thread.__init__(self)
#
#     def run(self):
#         exec(open('data/data.py').read())


if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.141')
