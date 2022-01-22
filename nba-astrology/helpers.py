from constants import *
from flatlib import const
from flatlib import aspects
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from gsheetstools import gSheet
import dateparser
import pandas as pd
import pytz

class chart_class:
    def __init__(self):
        g = gSheet("1_N8EcUpiwhHnl43BDY3p3jeVUFkNtcbZCMUlpusGuEY", suffix='af412')
        self.arenas = g.loadDataFromSheet("arenas").set_index('Arena').to_dict('index')

    def loadChart(self, game):
        """
        Add non-utc support back in if needed
        """
        if game['lat_'] == '--':
            game['lat_'], game['lon_'] = self.latLon(game['arena'])

        game['date_'], game['time_'] = self.formatDate(game['date_'], game['time_'])

        self.game = game
        self.chart = self.makeChart(self.game)
        self.houses = self.getHouses()
        self.angles = self.getAngles()

    def readChart(self):
        answers = self.allAnswers(self.houses)
        conjunctions = self.allConjunctions()
        moons = self.moonHouse(self.houses)

        answers.update(conjunctions)
        answers.update(moons)
        answers.update(self.game)
        return answers

    def latLon(self, arena):
        return self.arenas[arena]['Latitude'], self.arenas[arena]['Longitude']

    def formatDate(self, date_, time_, tz=None):
        dt = dateparser.parse(' '.join([date_, time_]))
        
        if tz:
            tz = pytz.timezone(tz)
            dt = tz.localize(dt)
            dt = dt.astimezone(pytz.timezone('UTC'))
        try:
            date_clean = dt.strftime("%Y/%m/%d")
            time_clean = dt.strftime("%H:%M")
            return date_clean, time_clean
        except AttributeError:
            print(date_, time_)
            return None, None

    def makeChart(self, game):
        date = Datetime(game['date_'], game['time_'], '+00:00')
        pos = GeoPos(float(game['lat_']), float(game['lon_']))
        chart_ = Chart(date, pos)
        return chart_

    def getHouses(self):
        houses = {
            int(h.id.replace("House", "")):{
                'object': h,
                'lord': lords_table[h.sign],
                'lord_sign': self.chart.getObject(getattr(const, lords_table[h.sign].upper())).sign,
                'condition': h.condition(),
                'north_node': h.hasObject(self.chart.getObject(const.NORTH_NODE)),
                'south_node': h.hasObject(self.chart.getObject(const.SOUTH_NODE)),
                'pars_fortuna': h.hasObject(self.chart.getObject(const.PARS_FORTUNA)),
                'planets_in_house': self.planetsInHouse(h),
                'aspects': self.getAspects(lords_table[h.sign])
            } for h in self.chart.houses
        }
        return houses

    def getAngles(self):
        angles = {
            a.id: {
                "sign": a.sign,
                "antiscia": a.antiscia().sign
            }
            for a in self.chart.angles
        }
        return angles

    def getAspects(self, p0):
        lords_aspects = {
            p1: aspects._aspectDict(
                self.chart.getObject(p0), self.chart.getObject(p1), [0, 60, 90, 120, 180]) 
            for p1 in planet_table
            }
        return lords_aspects

    def getConjunction(self, p, a, query):
        if isinstance(p, int):
            return self.houses[p]['lord_sign'] == self.angles[a][query]
        
        elif p in ['PARS_FORTUNA', 'NORTH_NODE', 'SOUTH_NODE']:
            return self.chart.getObject(getattr(const, p)).sign == self.angles[a][query]
        
        else:
            return None
   
    def planetsInHouse(self, h):
        planets_in_house = [
            p for p in planet_table if h.hasObject(self.chart.getObject(p))
        ]
        return planets_in_house

    def lordInHouse(self, l, h, houses):
        return houses[l]['lord'] in houses[h]['planets_in_house']

    def moonHouse(self, houses):
        return {
            f"M_in_{str(h)}":('Moon' in houses[h]['planets_in_house']) for h in houses}

    def allConjunctions(self):
        conjunctions = {}
        for p in [1, 4, 7, 10, 'PARS_FORTUNA', 'NORTH_NODE', 'SOUTH_NODE']:
            for a in ['Asc', 'MC', 'Desc', 'IC']:
                for q in ['sign', 'antiscia']:
                    conjunctions["_".join([str(p), a, q[0].upper()])] = self.getConjunction(p, a, q)

        return conjunctions

    def allAnswers(self, houses):
        answers = {
            "N1": houses[1]['north_node'],
            "S7": houses[7]['south_node'],
            "N10": houses[10]['north_node'],
            "S4": houses[4]['south_node'],
            "PoF1": houses[1]['pars_fortuna'],
            "PoF7": houses[7]['pars_fortuna'],
            "L7_1": self.lordInHouse(7, 1, houses),
            "L1_7": self.lordInHouse(1, 7, houses),
            "L1_1": self.lordInHouse(1, 1, houses),
            "L7_7": self.lordInHouse(7, 7, houses),
            "L1_10": self.lordInHouse(1, 10, houses),
            "L7_4": self.lordInHouse(7, 4, houses)
        }
        return answers


        