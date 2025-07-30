def notebook(options,id):
    js = f'''
        require.config({{
            paths: {{
                echarts: "https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min"
            }}
        }});
        require(["echarts"], function(echarts) {{
            var chartDom = document.getElementById("{id}");
            var myChart = echarts.init(chartDom);
            var option = {options};
            myChart.setOption(option);
        }});
        '''
    return js

def html(options, id, height = '500px', width = '700px'):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <script src="https://echarts.apache.org/en/js/vendors/echarts/dist/echarts.js"></script>
        <title>Basic Line Chart - Apache ECharts Demo</title>
    </head>
    <body>
        <div id="{id}" style="position: relative; height: {height}; width: {width};"></div>
        <script>
            var dom = document.getElementById('{id}');
            var myChart = echarts.init(dom, null, {{
            renderer: 'canvas',
            useDirtyRect: false
            }});
            var app = {{}};
            var option;
            option = {options};
            if (option && typeof option === 'object') {{
            myChart.setOption(option);
            }}
            window.addEventListener('resize', myChart.resize);
        </script>
    </body>
    </html>
    """

def iframe(srcdoc):
    text = '''<iframe
        sandbox="allow-scripts allow-forms"
        style="display: block; margin: 0px;"
        frameborder="0"
        srcdoc='{srcdoc}'></iframe>'''
    return text
            

def notebook_test():
    js = '''
        require.config({
            paths: {
                echarts: "https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min"
            }
        });
        require(["echarts"], function(echarts) {
            var chartDom = document.getElementById("echart_test");
            var myChart = echarts.init(chartDom);
            var option = {
                title: {
                    text: "Custom ECharts Example"
                },
                tooltip: {},
                xAxis: {
                    type: "category",
                    data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                },
                yAxis: {
                    type: "value"
                },
                series: [{
                    name: "Sales",
                    type: "line",
                    data: [120, 200, 150, 80, 70, 110, 130]
                }]
            };
            myChart.setOption(option);
        });
        '''
    return js