# gocharts

**gocharts** is a Python library for creating interactive, publication-quality charts using [ECharts](https://echarts.apache.org/) and a grammar of graphics approach inspired by [ggplot2](https://ggplot2.tidyverse.org/).

## Features

- **Grammar of Graphics**: Build complex visualizations by layering components (data, aesthetics, geoms, scales, etc.).
- **Interactive Charts**: Powered by ECharts for rich, interactive visualizations.
- **Flexible API**: Compose plots using a familiar, declarative syntax.
- **Export Options**: Render charts in Jupyter notebooks, web apps, or export as HTML.

## Installation

```bash
pip install gocharts
```

## Quick Start

```python
import gocharts as goc
import pandas as pd

df = pd.DataFrame({
    "time": [1, 2, 3, 4],
    "score": [10, 15, 13, 17]
})

gochart = goc.GoChart(df) \
    .geom('line', map = {'x':'time','y':'score'})

gochart.display()
```

## Documentation

- [User Guide](docs/user_guide.md)
- [API Reference](docs/api.md)
- [Examples](examples/)

## License

TBD

## Acknowledgements

- [ECharts](https://echarts.apache.org/)
- [ggplot2](https://ggplot2.tidyverse.org/)
- Inspired by the grammar of graphics paradigm
