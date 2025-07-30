import polars as pl

class Theme:
    def __init__(
        self,
        background_color: str = "#ffffff",
        grid_color: str = "#e0e0e0",
        axis_color: str = "#333333",
        axis_label_color: str = "#333333",
        title_color: str = "#222222",
        font: str = "Arial",
        font_size: int = 12,
        legend_background: str = "#f9f9f9",
        legend_border: str = "#cccccc",
        palette: list = None
    ):
        self.background_color = background_color
        self.grid_color = grid_color
        self.axis_color = axis_color
        self.axis_label_color = axis_label_color
        self.title_color = title_color
        self.font = font
        self.font_size = font_size
        self.legend_background = legend_background
        self.legend_border = legend_border
        self.palette = palette or [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
            "#bcbd22", "#17becf"
        ]
        self.grid = self.Grid()

    class Grid:
        def __init__(self):
            self.margin = self.Margin()
            self.spacing = self.Spacing()
        class Margin:
            def __init__(self, top=7, right=7, bottom=7, left=7):
                self.top = top
                self.right = right
                self.bottom = bottom
                self.left = left
        class Spacing:
            def __init__(self, cols=7, rows=7):
                self.cols = cols
                self.rows = rows
    

