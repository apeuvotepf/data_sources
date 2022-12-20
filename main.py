from flask import Flask, request, Response, render_template
import logging
from io import StringIO
import requests

app = Flask(__name__)

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

if __name__=="__main__":
    app.run(debug=True)