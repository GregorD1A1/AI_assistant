from flask import Flask, request
from tool_choice import tool_choice
import sys

app = Flask(__name__)


@app.route('/', methods=['POST'])
def execute():
    body = request.get_json()
    tool_choice(body['message'])
    sys.stdout.write("Request received.\n")

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)