from flask import Flask, request, Response, render_template
import logging
from io import StringIO
import requests
from oauth2client.service_account import ServiceAccountCredentials
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import random
import time
from collections import Counter

app = Flask(__name__)


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'data-sources-372218-e099443d9007.json'
VIEW_ID = '<REPLACE_WITH_VIEW_ID>'

# Create a stream-like object using StringIO
stream = StringIO()

# Configure a stream handler for the logger
stream_handler = logging.StreamHandler(stream)
stream_handler.setLevel(logging.WARNING)

# Add the handler to the logger's handlers list
app.logger.addHandler(stream_handler)

@app.route('/', methods=["GET"])
def hello_world():
 prefix_google = """
 <!-- Google tag (gtag.js) -->
<script async
src="https://www.googletagmanager.com/gtag/js?id=G-3SCJG24T32"></script>
<script>
 window.dataLayer = window.dataLayer || [];
 function gtag(){dataLayer.push(arguments);}
 gtag('js', new Date());
 gtag('config', 'G-3SCJG24T32');
</script>
 """
 return prefix_google + "Hello World"

@app.route("/logger", methods=["GET", "POST"])
def logger():
    app.logger.warning('A warning occurred !!')
    log_messages = stream_handler.stream.getvalue()
    print(log_messages) # it can be seen on Deta 
    return render_template('logger.html', log_messages=log_messages)


@app.route("/cookies", methods=["GET", "POST"])
def cookies():
    # Make a GET request to Google
    # req = requests.get("https://www.google.com/")
    req = requests.get("https://analytics.google.com/analytics/web/#/p344244454/")
    # Get the cookies
    cookies = req.cookies.get_dict()
    # Display the cookies in the app
    # return str(cookies)
    return req.text



################# GOOGLE TREND ################################

@app.route('/trends', methods=['GET', 'POST'])
def trends():
    if request.method == 'POST':

        # Initialize the pytrends library
        pytrend = TrendReq()

        # Get the keywords from the form
        keywords = request.form['keywords']

        # Split the keywords into a list
        keywords_list = keywords.split(' ')

        # Set the timeframe for the trend data
        timeframe='2022-01-01 2023-01-01'

        # Get the trend data
        pytrend.build_payload(kw_list=keywords_list, timeframe=timeframe)
        trend_data = pytrend.interest_over_time().drop(['isPartial'], axis=1)

        # Convert the trend data to a Pandas DataFrame
        dates = [datetime.fromtimestamp(int(date/1e9)).date().isoformat() for date in trend_data.index.values.tolist()]

        params = {'type': 'line', 
                'data':{
                    'labels': dates,
                    'datasets':[]
                },
                'options': {
                    "title": {
                        "text": 'My chart'
                        },
                    "scales": {
                        "yAxes": [{
                            "ticks": {
                                "beginAtZero": 'true'
                            }
                        }]
                    }
                }}

        # create datasets for each keyword
        for column in trend_data.columns:
            params['data']['datasets'].append({'label': column, 
                                            'data': trend_data[column].values.tolist(),
                                            # generate random color
                                            "borderColor": "#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)]),
                                            "fill": 'false',
                                        })


        template = f"""  
        <html>
            <head>
                <title>Trend Comparison</title>
            </head>
            <body>
                <h1>Trend Data</h1>
                <p>Keywords: {keywords}</p>    
                <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js"></script>
                <div><canvas id="myChart" width="25" height="25"></canvas></div>
                <script>
                    var ctx = document.getElementById('myChart');
                    var myChart = new Chart(ctx, {params});
                </script>
            </body>
        </html>
        """

        return template
    else:
        # Render the trends form template
        return render_template('trends_form.html')


################# EXECUTION TIME ################################

def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        return result
    return wrapper

@log_execution_time
def count_words_dict(text):
    word_counts = {}
    for word in text.split():
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

@log_execution_time
def count_words_counter(text):
    Counter(text.split())

@app.route('/execution_time', methods=['GET', 'POST'])
def execution_time():
    # Read in the text file
    with open('shakespeare.txt', 'r') as f:
        text = f.read()
    
    dict_execution_times = []
    counter_execution_times = []
    for i in range(1):
        start_time_dict = time.time()
        word_count_dict = count_words_dict(text)
        end_time_dict = time.time()
        word_count_counter = count_words_counter(text)
        end_time_counter = time.time()
        dict_execution_times.append(end_time_dict - start_time_dict)
        counter_execution_times.append(end_time_counter - end_time_dict)
    

    # Calculate the mean and variance of the execution times
    dict_mean_time = sum(dict_execution_times) / len(dict_execution_times)
    dict_variance = sum((x - dict_mean_time) ** 2 for x in dict_execution_times) / len(dict_execution_times)

    counter_mean_time = sum(counter_execution_times) / len(counter_execution_times)
    counter_variance = sum((x - counter_mean_time) ** 2 for x in counter_execution_times) / len(counter_execution_times)
    

    params_mean = {'type': 'line', 
                'data':{
                    # 'labels': ['Mean using a dictionary' 'Mean using the Counter function'],
                    'datasets':[
                        {'label': 'Mean using a dictionary', 
                        'data': [dict_mean_time],
                        "backgroundColor": "red",
                        },
                        {'label': 'Mean using the Counter function', 
                        'data': [counter_mean_time],
                        "backgroundColor": "blue",
                        }
                    ]
                },
                'options': {
                    "title": {
                        "text": 'Mean'
                        },
                }
            }

    params_variance = {'type': 'line', 
                'data':{
                    # 'labels': ['Variance using a dictionary' 'Variance using the Counter function'],
                    'datasets':[
                        {'label': 'Variance using a dictionary', 
                        'data': [dict_variance],
                        "backgroundColor": "red",
                        },
                        {'label': 'Variance using the Counter function', 
                        'data': [counter_variance],
                        "backgroundColor": "blue",
                        }
                    ]
                },
                'options': {
                    "title": {
                        "text": 'Variance'
                        },
                }
            }

    template = f"""  
        <html>
            <head>
                <title>Execution time</title>
            </head>
            <body>
                <h1>Execution time for two different methods</h1>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js"></script>
                <div><canvas id="myChart" width="25" height="25"></canvas></div>
                <div><script>
                    var ctx = document.getElementById('myChart');
                    new Chart(ctx, {params_mean});
                </script></div>

                <div><script>
                    var ctx = document.getElementById('myChart');
                    new Chart(ctx, {params_variance});
                </script></div>
            </body>
        </html>
        """
    return template

if __name__=="__main__":
    app.run(debug=True)