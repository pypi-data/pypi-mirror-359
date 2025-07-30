import polars as pl
from gocharts.GoChartClass import Chart
from gocharts.utils import percent_value, calculate_distance

class Generator:
    def __init__(self, gochart: Chart):
        self._verify_gochart(gochart)
        self.gochart = gochart

    def _verify_gochart(self, gochart):
        # This method currently does nothing meaningful
        isinstance(gochart, dict)

    def _get_types(self, map_item):
        types = set([g['map_types'][map_item] for g in self.gochart.geom_list])
        # possible echarts types are "value", "category", "time"
        polars_types = self.gochart.valid_polar_types
        check_subset = {k: types.issubset(v) for k, v in polars_types.items()}
        map_item_type = [k for k, v in check_subset.items() if v]
        if map_item_type == []:
            raise ValueError('Mixed types provided in mapping for ' + map_item + ': ' + ','.join(types))
        return map_item_type[0]

    def _get_geom_data(self, geom):
        if geom['data'] == 'core_data':
            return self.gochart.core_data
        else:
            return geom['data']

    def _get_unique_values(self, map_item, value_type='unique'):
        value_series = []
        for dict_i in self.gochart.geom_list:
            column_name = dict_i['map'][map_item]
            df = self._get_geom_data(dict_i)
            value_series.append(df.select(column_name).to_series())
        if value_type == 'unique':
            return pl.concat(value_series).unique().to_list()
        elif value_type == 'range':
            concat_series = pl.concat(value_series)
            return [concat_series.min(), concat_series.max()]
        else:
            raise ValueError("value_type must be 'unique' or 'range'")

    def _get_grid_values(self, param: dict):
        """
        Get unique values for facet columns or rows.
        If there are two or more of the cols or rows it creates a permutations 
        of the values and combines them into a list of lists.
        """
        facet = self.gochart.facet
        if param in facet.keys() and facet[param] is not None:
            values = set()
            for geom in self.gochart.geom_list:
                df = self._get_geom_data(geom)
                if facet[param] not in df.columns:
                    continue
                else:
                    values_add = df[facet[param]].unique().to_list()
                    values.update(values_add)
            if len(values) > 0:
                return values
            else:
                return None
        return None

    def _get_grid(self) -> list[dict]:
        margins = self.gochart.theme.grid.margin
        TITLE_MARGIN_ADJUSTMENT = 11  # Extra top margin to accommodate chart title
        if self.gochart.title is not None:
            margins.top += TITLE_MARGIN_ADJUSTMENT
        spacing = self.gochart.theme.grid.spacing
        cols = self._get_grid_values('col')
        rows = self._get_grid_values('row')

        if cols is None and rows is None:
            raise ValueError('No columns or rows provided for facet in the data')

        if cols is not None and rows is not None:
            width = calculate_distance(margins.left, margins.right, spacing.cols, len(cols))
            height = calculate_distance(margins.top, margins.bottom, spacing.rows, len(rows))
            grids = [{'facet_col': c, 'facet_row': r} for c in cols for r in rows]
            position = []
            for c in range(len(cols)):
                for r in range(len(rows)):
                    position.append({
                        'x_axis_id': c,
                        'y_axis_id': r,
                        'left': margins.left + c * (width + spacing.cols),
                        'top': margins.top + r * (height + spacing.rows),
                        'width': width,
                        'height': height
                    })
            merged = [{**g, **p} for g, p in zip(grids, position)]
            merged = [{'id': i, **v} for i, v in enumerate(merged)]

        elif cols is not None:
            width = calculate_distance(margins.left, margins.right, spacing.cols, len(cols))
            grids = [{'facet_col': c} for c in cols]
            position = [{
                'x_axis_id': i,
                'left': margins.left + i * (width + spacing.cols),
                'width': width
            } for i in range(len(cols))]
            merged = [{**g, **p} for g, p in zip(grids, position)]
            merged = [{'id': i, **v} for i, v in enumerate(merged)]

        elif rows is not None:
            height = calculate_distance(margins.top, margins.bottom, spacing.rows, len(rows))
            grids = [{'facet_row': r} for r in rows]
            position = [{
                'y_axis_id': i,
                'top': margins.top + i * (height + spacing.rows),
                'height': height
            } for i in range(len(rows))]
            merged = [{**g, **p} for g, p in zip(grids, position)]
            merged = [{'id': i, **v} for i, v in enumerate(merged)]
        return merged

    @staticmethod
    def _facet_text_style(style_type):
        """Return style dictionary for facet text based on type."""
        common_style = {
            'fontSize': 16,
            'fontWeight': 'bold',
            'padding': 5,
            'color': '#909090',
        }
        border_style = {
            'borderColor': '#909090',
            'borderWidth': 0,
            'borderRadius': 3
        }
        if style_type == 'title':
            return {'textStyle': {**common_style}, **border_style}
        elif style_type == 'axis':
            return {'nameTextStyle': {**common_style, **border_style}}

    def _get_facet_col_titles(self, grid: list[dict], percent=True) -> list[str]:
        """
        Get facet titles for facet columns.
        Returns a list of strings with facet titles and locations corresponding to the grid.
        """
        if 'facet_col' in grid[0] and 'top' in grid[0]:
            cols = [
                {
                    'text': facet_col,
                    'left': percent_value(max(g['left'] for g in grid if g['facet_col'] == facet_col), percent),
                    'bottom': percent_value(100-min(g['top'] for g in grid if g['facet_col'] == facet_col), percent),
                    **self._facet_text_style('title')
                }
                for facet_col in {g['facet_col'] for g in grid}
            ]
            print(cols)
            return cols
        if 'facet_col' in grid[0] and 'top' not in grid[0]:
            cols = [
                {
                    'text': g['facet_col'],
                    'left': percent_value(g['left'],percent),
                    'top': '50px',
                    'textVerticalAlign': 'bottom',
                    **self._facet_text_style('title')
                }
                for g in grid
            ]
            return cols
        else:
            return []

    def _get_facet_row_titles(self, grid: list[dict], percent=True) -> list[str]:
        """
        Get facet titles for facet rows.
        Returns a list of strings with facet titles and locations corresponding to the grid.
        """
        axis_param = {
            'position': 'right',
            'nameLocation': 'center',
            'nameGap': '0',
            'nameRotate': '270',
            'axisLabel': {'show': False},
            'axisLine': {'show': False},
            **self._facet_text_style('axis')
        }
        if 'facet_row' in grid[0] and 'left' in grid[0]:
            rows = [
                {
                    'name': facet_row,
                    'gridIndex': max(
                        (g for g in grid if g['facet_row'] == facet_row),
                        key=lambda x: x['left']
                    )['id'],
                    **axis_param,
                }
                for facet_row in {g['facet_row'] for g in grid}
            ]
            return rows
        elif 'facet_row' in grid[0] and 'left' not in grid[0]:
            rows = [
                {
                    'name': g['facet_row'],
                    'gridIndex': g['id'],
                    **axis_param
                }
                for g in grid
            ]
            return rows
        else:
            return []

    def _get_grid_options(self, grid, percent=True) -> list[dict]:
        """
        Get grid options for facet columns or rows.
        Returns a list of dictionaries with grid properties.
        """
        opts = ['left', 'bottom', 'right', 'top', 'width', 'height']
        if percent:
            return [{k: str(v) + '%' for k, v in g.items() if k in opts} for g in grid]
        else:
            return [{k: v for k, v in g.items() if k in opts} for g in grid]

    def _get_axis(self, axis, grid=None):
        """
        Get axis for facet columns or rows. Returns a list of dictionaries with axis properties.
        """
        if axis not in ['x', 'y']:
            raise ValueError('Axis needs to be x or y')
        type = self._get_types(axis)

        if grid is None:
            if type == 'value':
                axis = {'type': type}
            else:
                data = self._get_unique_values(axis)
                axis = {'type': type, 'data': data}
            return axis
        else:
            if self.gochart.facet['scales'] == 'fixed':
                if type == 'value':
                    range = self._get_unique_values(axis, value_type='range')
                    ax = {'type': type, 'min': min(0, range[0]), 'max': range[1]}
                else:
                    ax = {'type': type, 'data': self._get_unique_values(axis, value_type='unique')}
                axis = [{'gridIndex': i['id'], **ax} for i in grid]
            else:
                raise NotImplementedError('Only fixed scales are implemented for now')
            return axis

    def _get_facet_map(self):
        """
        Get facet map for facet columns or rows.
        Returns a list of dictionaries with facet properties.
        """
        facet = self.gochart.facet
        if facet is None:
            return None
        if facet['col'] is not None and facet['row'] is not None:
            return {'facet_col': facet['col'], 'facet_row': facet['row']}
        elif facet['col'] is not None:
            return {'facet_col': facet['col']}
        elif facet['row'] is not None:
            return {'facet_row': facet['row']}

    def _get_grid_for_series(self, grid: list[dict] = None):
        """
        Get grid DataFrame for facet columns or rows.
        Returns a Polars DataFrame with grid properties.
        """
        grid_df = pl.DataFrame({k: [d[k] for d in grid] for k in grid[0].keys()})
        grid_df = grid_df.with_columns(
            pl.col('id').alias('xAxisIndex'),
            pl.col('id').alias('yAxisIndex')
        )
        return {'grid_df': grid_df, 'facet_map': self._get_facet_map()}

    @staticmethod
    def _get_geom_grid(grid_dict: dict[pl.DataFrame, dict],
                       df: pl.DataFrame,
                       dict_map: dict,
                       groupings: list[str]) -> dict:
        """
        Get grid DataFrame for geom series.
        Returns a Polars DataFrame with grid properties.
        """
        grid_axis = ['xAxisIndex', 'yAxisIndex']
        geom_facet_map = {k: v for k, v in grid_dict['facet_map'].items() if v in df.columns}
        geom_grid_df = grid_dict['grid_df'].select(grid_axis + list(geom_facet_map.keys()))
        if len(geom_facet_map) > 0:
            dict_map.update(geom_facet_map)
        # Create new columns based on standard_names mapping, allowing duplicates
        df = df.select([pl.col(v).alias(k) for k, v in dict_map.items()])
        df = df.join(geom_grid_df, how='left', on=list(geom_facet_map.keys()))
        to_group = [k for k in dict_map.keys() if k in groupings] + grid_axis
        return df, to_group

    def _get_series(self, grid: dict = None):
        all_series = []
        for dict_i in self.gochart.geom_list:
            geom_type = dict_i['type']
            series_map = self.gochart.valid_types_mapping[geom_type]
            df = self._get_geom_data(dict_i)
            dict_map = dict_i['map']
            # if grid is not None
            if grid is not None:
                df, to_group = self._get_geom_grid(grid, df, dict_map, self.gochart.grouping_mappings)
            else:
                df = df.select([pl.col(v).alias(k) for k, v in dict_map.items()])
                to_group = [k for k in dict_map.keys() if k in self.gochart.grouping_mappings]
            series = (
                df
                .with_columns(pl.concat_list(series_map).alias('data'))
                .with_columns(pl.lit(geom_type).alias('type'))
                .group_by(to_group+['type'], maintain_order=True)
                .agg(pl.col('data'))
            )
            all_series.extend(series.to_dicts())
        return all_series
    
    def _get_title(self):
        """
        Get title and subtitle for the chart.
        Returns a dictionary with title and subtitle.
        """
        title = {}
        if self.gochart.title is not None:
            title['text'] = self.gochart.title
            if self.gochart.subtitle is not None:
                title['subtext'] = self.gochart.subtitle
        return title

    def _get_options(self):
        options = {}
        options['title'] = [self._get_title()]
        if self.gochart.facet is not None:
            grid = self._get_grid()
            options['grid'] = self._get_grid_options(grid)
            options['xAxis'] = self._get_axis('x', grid)
            options['yAxis'] = self._get_axis('y', grid)
            options['series'] = self._get_series(self._get_grid_for_series(grid))
            # add facet titles
            options['title'] = options['title'] + self._get_facet_col_titles(grid)
            options['yAxis'] = options['yAxis'] + self._get_facet_row_titles(grid)
        else:
            options['xAxis'] = self._get_axis('x')
            options['yAxis'] = self._get_axis('y')
            options['series'] = self._get_series()
        options['tooltip'] = {}
        options['legend'] = {}
        return options