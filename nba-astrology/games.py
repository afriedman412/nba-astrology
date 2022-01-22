from gsheetstools import gSheet
import pandas as pd
import requests
from geopy.geocoders import Nominatim
import sys

# year = '2020'
year = sys.argv[-1]


gs = gSheet('1_N8EcUpiwhHnl43BDY3p3jeVUFkNtcbZCMUlpusGuEY', suffix="af412")
arenas = gs.loadDataFromSheet("arenas")[
    ['Arena', 'Longitude', 'Latitude']]

arenas['Arena'] = arenas['Arena'].str.lower()

arenas = arenas.set_index('Arena').to_dict('index')

# geolocator = Nominatim(user_agent="nba_test")

# def latLon(p):
#     print(p)
#     loc = geolocator.geocode(p)
#     if loc:
#         return p, loc.latitude, loc.longitude
#     else:
#         return p, None, None

r = requests.get(f'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{year}/league/00_full_schedule.json')


all_games = []
for l in r.json()['lscd']:
    
    games = [
        {
            'home_team': g['h']['ta'],
            'away_team': g['v']['ta'],
            'date_utc': g['gdtutc'],
            'time_utc': g['utctm'],
            'arena': g['an'],
            'location': g['ac'],
            'arena_lat': arenas[g['an'].lower()]['Latitude'],
            'arena_lon': arenas[g['an'].lower()]['Longitude'],
            'home_win': g['h']['s'] > g['v']['s']
        } for g in l['mscd']['g']
    ]
    all_games += games

df = pd.DataFrame(all_games)



gs.writeDataToSheet(df, f"games {year}")