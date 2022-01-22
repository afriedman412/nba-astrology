from gsheetstools import gSheet
import pandas as pd
import requests
from geopy.geocoders import Nominatim
import sys

i = 110
# year = '2018'
year = sys.argv[-1]

geolocator = Nominatim(user_agent="nba_test")
gs = gSheet('1_N8EcUpiwhHnl43BDY3p3jeVUFkNtcbZCMUlpusGuEY', suffix="af412")

arenas = gs.loadDataFromSheet("stadium info")['Stadium'].str.lower().to_list()

print(year)
def latLon(p):
    print(p)
    loc = geolocator.geocode(p)
    if loc:
        return p, loc.longitude, loc.latitude
    else:
        return p, None, None

r = requests.get(f'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{year}/league/00_full_schedule.json')

new_arenas = []
for l in r.json()['lscd']:
    for g in l['mscd']['g']:
        if g['an'].lower() not in arenas and g['an'] not in new_arenas:
            new_arenas.append(g['an'])
            
new_arenas =  [latLon(p) for p in new_arenas]

j = i + 2 + len(new_arenas)
gs.writeDataToSheet(pd.DataFrame(new_arenas), f"stadium info!A{str(i)}:C{str(j)}")

print(j)