from helpers import *
from gsheetstools import gSheet
import pandas as pd
import sys

# home_team = "CLE"
# date_ = '2022/01/17'
# time_ = '08:10'

# year = '2018'
year = sys.argv[-1]

g = gSheet("1_N8EcUpiwhHnl43BDY3p3jeVUFkNtcbZCMUlpusGuEY", suffix="af412")

game_df = g.loadDataFromSheet(f"games {year}!A:I")
game_df.columns = [
    'home_team', 'away_team', 'date_', 'time_', 
    'arena', 'location', 'lat_', 'lon_', 'home_win'
    ]

c = chart_class()

out_ = []
for game in game_df.to_dict('records'):
    c.loadChart(game)
    data = c.readChart()
    out_.append(data)

df_out = pd.DataFrame(out_)

g.writeDataToSheet(df_out, f"{year} predictions")
