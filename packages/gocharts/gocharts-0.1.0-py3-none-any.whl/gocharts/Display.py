
from IPython.display import display, HTML, Javascript
import gocharts.template as template

class Display:
    def __init__(self):
        pass
    
    @staticmethod
    def display_text(options):
        return template.notebook(options)

    @staticmethod
    def display_nootbook(options,id,width,height):
        display(HTML(f'<div id="{id}" style="width:{width};height:{height};background:white"></div>'))
        display(Javascript(template.notebook(options,id)))

    @staticmethod
    def display_nootbook_test():
        display(HTML(f'<div id="echart_test" style="width:400px;height:300px;background:white"></div>'))
        display(Javascript(template.notebook_test()))
