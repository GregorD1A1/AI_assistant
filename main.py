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


@app.route('/aidevs_api', methods=['POST'])
def aidevs_api():
    body = request.get_json()
    sys.stdout.write(f"Request received:\n{body}\n")
    question = body['question']
    from langchain.prompts import PromptTemplate
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import StrOutputParser
    import json
    prompt = PromptTemplate.from_template("respond the next question: {question}")
    chain = prompt | ChatOpenAI() | StrOutputParser()
    result = chain.invoke({'question': question})
    sys.stdout.write(f"Response:\n{result}\n")

    return json.dumps({'reply': result})


if __name__ == '__main__':
    app.run(debug=True)