from flask import Flask, request
from tool_choice import tool_choice
import logging

app = Flask(__name__)


@app.route('/', methods=['POST'])
def execute():
    body = request.get_json()
    tool_choice(body['message'])

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)