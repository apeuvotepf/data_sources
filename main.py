from flask import Flask, request, Response, render_template
import logging
from io import StringIO
import requests
from oauth2client.service_account import ServiceAccountCredentials
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import random

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

        # Convert the dataframe to a list of dictionaries for the chart data
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



if __name__=="__main__":
    app.run(debug=True)