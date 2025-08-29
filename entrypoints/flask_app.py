from flask import Flask
from adapters.orm import start_mappers

import config


start_mappers()
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"
