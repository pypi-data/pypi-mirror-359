import gocharts.template as template

class ChartExporter:
    def __init__(self):
        pass

    @staticmethod
    def save_text(options):
        return options
    
    @staticmethod
    def save_html(options, file_name, height, width, id = 'div_echart'):
        text = template.html(options,id, height, width)
        with open(file_name, 'w') as fd:
            fd.write(text + '\n')