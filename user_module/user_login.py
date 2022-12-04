from flask import Flask

from main import app


@app.route("/hello", methods=["GET"])
def hello():
    return "Hello World"
