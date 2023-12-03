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


def search_DuckDuckGo(information):
    from langchain.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
    search = DuckDuckGoSearchResults()
    return search.run(information)


@app.route('/aidevs_api', methods=['POST'])
def aidevs_api():
    body = request.get_json()
    sys.stdout.write(f"Request received:\n{body}\n")
    question = body['question']
    from openai import OpenAI
    import json
    client = OpenAI()


    messages = [{"role": "system", "content": f"Use internet search to provide answer for the next question. Return answer only, without additional informations."}, {"role": "user", "content": f"User:'''{question}'''"}]
    tools = [
        {
            "type": "function",
            "function":
                {
                    "name": "search_DuckDuckGo",
                    "description": "search information on Internet",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "information": {
                                "type": "string",
                                "description": "information to search",
                            },
                            "unit": {"type": "string"},
                        },
                        "required": ["information"],
                    },
                },
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_calls[0].function.name
            function_args = json.loads(tool_calls[0].function.arguments)
            info = globals()[function_name](**function_args)
            sys.stdout.write(info)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": info
            })
        second_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            temperature=0.7,
        )
        response_message = second_response.choices[0].message
        response_content = response_message.content



    response = json.dumps({'reply': response_content})
    sys.stdout.write(response)

    return response


if __name__ == '__main__':
    app.run(debug=True)