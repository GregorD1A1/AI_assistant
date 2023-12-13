from flask import Flask, request
from conv_flow import conversate
import sys

app = Flask(__name__)


@app.route('/', methods=['POST'])
def execute():
    sys.stdout.write("Request received.\n")
    sys.stdout.flush()
    body = request.get_json()
    message = body['message']
    conversate(message)

    return "ok"


if __name__ == '__main__':
    app.run(debug=True, port=20217)
