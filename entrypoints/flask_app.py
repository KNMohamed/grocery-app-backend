from flask import Flask

import config
import orm


orm.start_mappers()
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"
