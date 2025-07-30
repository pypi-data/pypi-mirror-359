import polars as pl
from gocharts.Theme import Theme

class Chart:

    def __init__(self, data: pl.DataFrame = None, map: dict = None):
        self.valid_mappings = ['x','y','z','colour','shape','group','fill','tooltip','hover','linewidth','size']
        self.grouping_mappings = ['colour','shape','group','fill','linewidth','size']
        self.valid_types = ['line','scatter', 'bar', 'area', 'heatmap','map','rect','circle']
        self.valid_types_mapping = {
            'line': ['x', 'y'],
            'scatter': ['x', 'y'],
            'bar': ['x', 'y'],
            'area': ['x', 'y'],
            'heatmap': ['x', 'y', 'z'],
            'map': ['x', 'y'],
            'rect': ['x', 'y'],
            'circle': ['x', 'y']
        }
        self.valid_polar_types = {'value':['Int64','Float64','Int32','Float32'],
                        'category': ['Boolean','Categorical','Utf8','String'],
                        'time': ['Datetime','Date','Time','Duration']}
        self.core_data = None
        if data is not None:
            self.core_data = data
        if map is not None:
            if len(map) > 0:
                self._verify_mapping(map)
                self.core_map = map
        self.geom_list = []
        self.facet = None # {'cols': None, 'rows': None, 'scales': None, 'space': None}'
        self.theme = Theme()
        self.title = None
        self.subtitle = None

    def _verify_type(self,type):
        if type not in self.valid_types:
            raise ValueError(f"Type must be one of {self.valid_types}, but got '{type}'")

    def _verify_type_mapping(self, type: str, mapping: dict):
        if not all(v in mapping.keys() for v in self.valid_types_mapping[type]):
            message = f"Mapping for type '{type}' must have {self.valid_types_mapping[type]}, but got {mapping.keys()}"
            raise ValueError(message)

    def _verify_mapping(self, mapping: dict):
        if not all(key in self.valid_mappings for key in mapping.keys()):
            message = 'Not supported mapping arguments: '+','.join(list(set(mapping) - set(self.valid_mappings)))
            raise ValueError(message)

    def _verify_data_mapping(self,data: pl.DataFrame, mapping):
        if not all(v in data.columns for v in mapping.values()):
            message = 'Mapping is not available in data provided: '+','.join(list(set(mapping.values()) - set(data.columns)))
            raise ValueError(message)


    def _create_map_types(self,df,map):
        self._verify_data_mapping(df, map)
        col_types = dict(zip(df.columns, df.dtypes))
        map_types = {k: str(col_types[v]) for k,v in map.items()}
        return map_types
