from flask import Flask, request
from conv_flow import conversate
import sys
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
@app.route('/', methods=['POST'])
def execute():
    sys.stdout.write("Request received.\n")
    logging.error('Dzik!')
    body = request.get_json()
    message = body['message']
    conversate(message)

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)