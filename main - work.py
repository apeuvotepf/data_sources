from flask import Flask, redirect, url_for, request, Response

app = Flask(__name__)


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

@app.route("/logger", methods=["GET"])
def logger():
    return Response('test', status=200, mimetype="text/html")
