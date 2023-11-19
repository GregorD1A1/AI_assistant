from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def endpoint():
    data = request.get_json()  # Get the JSON data from the request
    print(data)

    # Perform any data processing or logic here

    response = {'message': 'Success', 'data': data}  # Create a response JSON

    return jsonify(response)  # Return the response as JSON


if __name__ == '__main__':
    app.run()