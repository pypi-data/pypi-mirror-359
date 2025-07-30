import polars as pl
from gocharts.GoChartClass import Chart

class Facet:
    def __init__(self, gochart: Chart):
        self._verify_gochart(gochart)
        self.gochart = gochart

    