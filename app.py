import sys
sys.path.append ("./nba-astrology/")

from flask import Flask, request, render_template
from helpers import *
import json
import pandas as pd


app = Flask(__name__)

c = chart_class(arenas=False)

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('chart.html')

@app.route("/chart", methods=['GET', 'POST'])
def chart():
    game = {
        k: request.args.get(k) for k in ['lat_', 'lon_', 'date_', 'time_']
        }

    c.loadChart(game)
    df = pd.DataFrame({f'House {k}':formatHouse(v) for k, v in c.houses.items()})
    return render_template(
        'chart.html',  
        tables=[
            pd.DataFrame(c.angles).to_html(),
            df.to_html(classes='data')
            ], 
        titles=df.columns.values
        )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
