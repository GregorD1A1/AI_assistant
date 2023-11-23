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

notes = []
def save_note(note):
    global notes
    notes.append(note)

@app.route('/aidevs_api', methods=['POST'])
def aidevs_api():
    global notes
    body = request.get_json()
    sys.stdout.write(f"Request received:\n{body}\n")
    question = body['question']
    from openai import OpenAI
    import json
    client = OpenAI()

    # Step 1: send the conversation and available functions to the model
    notesy = "\n".join(notes) if notes else ""
    messages = [{"role": "system", "content": f"{notesy}\nAnswer question if user provided question; if it provided statement, save it as a note."}, {"role": "user", "content": f"User:'''{question}'''"}]
    sys.stdout.write(notesy)
    tools = [
        {
            "type": "function",
            "function":
                {
                    "name": "save_note",
                    "description": "save information note if some information is provided",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "note": {
                                "type": "string",
                                "description": "information note",
                            },
                            "unit": {"type": "string"},
                        },
                        "required": ["note"],
                    },
                },
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        function_name = tool_calls[0].function.name
        function_args = json.loads(tool_calls[0].function.arguments)
        globals()[function_name](**function_args)

    reply = response_message.content
    reply = "ok" if not reply else reply

    sys.stdout.write(f"Response:\n{reply}\n")

    return json.dumps({'reply': reply})


if __name__ == '__main__':
    app.run(debug=True)