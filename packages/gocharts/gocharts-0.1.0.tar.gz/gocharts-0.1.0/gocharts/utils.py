def percent_value(value: float, percent: bool) -> str | float:
    return f"{value}%" if percent else value

def calculate_distance(margin_1, margin_2, spacing, length):
    distance = (100 - margin_1 - margin_2 - (length - 1) * spacing) / length
    if distance < 0:
        raise ValueError('Facet columns/rows are too many to fit in the chart width')
    return distance