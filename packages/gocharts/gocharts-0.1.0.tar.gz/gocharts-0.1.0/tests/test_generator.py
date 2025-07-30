import polars as pl
import pytest
import sys
import os
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gocharts as goc
from gocharts.Generator import Generator
from gocharts.GoChartClass import Chart
from gocharts.utils import percent_value

class DummyTheme:
    class grid:
        margin = type('Margin', (), {'left': 7.0, 'right': 7.0, 'top': 7.0, 'bottom': 7.0})()
        spacing = type('Spacing', (), {'cols': 7.0, 'rows': 7.0})()

def make_dummy_chart(facet=None, geom_list=None, core_data=None):
    df = pd.DataFrame({
        'Category': ['A', 'A', 'B', 'B', 'C', 'C'],
        'Subgroup': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
        'Value': [10, 15, 20, 25, 30, 35]
    })

    gochart = (goc.GoChart(df)
        .map(x='Category',y='Value')
        .geom('bar')
        .facet(col = 'Subgroup', row = 'Category')
    )
    return gochart.chart

def test_percent_value():
    assert percent_value(10, True) == '10%'
    assert percent_value(10, False) == 10

def test_facet_text_style():
    title = Generator._facet_text_style('title')
    axis = Generator._facet_text_style('axis')
    assert 'textStyle' in title
    assert 'nameTextStyle' in axis

def test_get_grid_cols_rows():
    chart = make_dummy_chart(facet={'col': 'A', 'row': 'B', 'scales': 'fixed'})
    gen = Generator(chart)
    grid = gen._get_grid()
    assert isinstance(grid, list)
    assert 'id' in grid[0]

def test_get_axis():
    chart = make_dummy_chart()
    gen = Generator(chart)
    axis = gen._get_axis('x')
    assert 'type' in axis

def test_get_grid_options():
    chart = make_dummy_chart(facet={'col': 'A', 'row': None, 'scales': 'fixed'})
    gen = Generator(chart)
    grid = gen._get_grid()
    opts = gen._get_grid_options(grid)
    assert isinstance(opts, list)
    assert '%' in list(opts[0].values())[0]

if __name__ == "__main__":
    pytest.main()
