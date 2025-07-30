import numpy as np
import pandas as pd
import polars as pl
import json

# display related
import time # for unique id generation

from gocharts.Display import Display
from gocharts.ChartExporter import ChartExporter
from gocharts.Generator import Generator
from gocharts.GoChartClass import Chart
# main class for GoChart
__version__ = '0.1.0'
__author__ = 'Edvinas Drevinskas'
__license__ = 'MIT'
__all__ = ['GoChart']

class GoChart:
    def __init__(self, data = None, map: dict = None):
        if data is not None:
            self._verify_data(data)
            data = self._data_converter(data)
        self.chart = Chart(data, map)
    
    def _verify_data(self,data):
        if not isinstance(data, (pd.DataFrame, np.ndarray, pl.DataFrame)):
            raise TypeError("data must be a pandas, polars DataFrame or numpy ndarray")

    def _data_converter(self,df):
        if isinstance(df, pd.DataFrame):
            df = pl.from_pandas(df)
        if isinstance(df, np.ndarray):
            df = pl.from_numpy(df)
        return df
    
    def _convert_type(self,type: str):
        if type == 'point':
            type = 'scatter'
        elif type == 'tile':
            type = 'heatmap'
        self.chart._verify_type(type)
        return type

    def _convert_string_list(self, value: str | list[str]) -> list[str]:
        if value is not None:
            if isinstance(value, str):
                value = [value]
        return value
    
    def _verify_string(self, values: str):
        if not isinstance(values, str):
            raise TypeError(f"Expected a string, but got {type(values).__name__}")
        if len(values) == 0:
            raise ValueError("String cannot be empty")
        return values

    def map(self,**kwargs):
        # it might override map given in the parameter of the class
        self.chart._verify_mapping(mapping=kwargs)
        if self.chart.core_data is not None:
            self.chart._verify_data_mapping(self.chart.core_data,kwargs)
        self.chart.core_map = kwargs
        return self
    
    def title(self, title: str, subtitle: str = None):
        if not isinstance(title, str):
            raise TypeError("Title must be a string")
        if subtitle is not None and not isinstance(subtitle, str):
            raise TypeError("Subtitle must be a string")
        self.chart.title = title
        self.chart.subtitle = subtitle
        return self

    def geom(self,type: str,**kwargs):
        
        type = self._convert_type(type)

        if 'map' in kwargs.keys():
            map = kwargs['map']
        else:
            map = self.chart.core_map

        if 'data' in kwargs.keys():
            df = kwargs['data']
            self._verify_data(df)
            df = self._data_converter(df)
            map_types = self.chart._create_map_types(df,map)
        else:
            df = self.chart.core_data
            map_types = self.chart._create_map_types(df,map)
            data = 'core_data'

        self.chart._verify_type_mapping(type, map)

        self.chart.geom_list = self.chart.geom_list + [{'type':type, 'map':map, 'data':data, 'map_types':map_types}]
        return self
    
    def facet(self,
              col: str = None,
              row: str = None, 
              scales: str = 'fixed', space: float = 0.1):
        facet = {}
        if col is None and row is None:
            raise ValueError('At least one of col or row must be provided')
        
        if col is not None:
            self._verify_string(col)
        if row is not None:
            self._verify_string(row)
            
        facet['col'] = col
        facet['row'] = row

        if scales is not None:  
            if scales not in ['free', 'fixed', 'free_x', 'free_y']:
                raise ValueError('Scales must be either "free", "fixed", "free_x" or "free_y"')
            facet['scales'] = scales
        if space is not None:
            if not isinstance(space, (int, float)):
                raise TypeError('Space must be a number')
            if space < 0 or space > 1:
                raise ValueError('Space must be between 0 and 1')
            facet['space'] = space
        self.chart.facet = facet
        return self

    def theme(self, **kwargs):
        print('Theme is not implemented yet')
        print(self.chart.theme)
        return self
    
    def display(self, width='600px', height='400px'):
        id = 'chart_'+str(round(time.time()*100000))
        Display.display_nootbook(json.dumps(Generator(self.chart)._get_options()),
                                 id,
                                 width,
                                 height)

    def display_test(self):
        Display.display_nootbook_test()

    def save(self, type, file_name, width='600px', height='400px'):
        id = 'chart_'+str(round(time.time()*100000))
        options = json.dumps(Generator(self.chart)._get_options())
        if type == 'text':
            return ChartExporter.save_text(options)
        elif type == 'html':
            ChartExporter.save_html(options, file_name, height, width, id)
        else:
            raise ValueError('Type must be either "text" or "html"')

