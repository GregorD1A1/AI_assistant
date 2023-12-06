import json

from flask import Flask, request
from conv_flow import conversate
import sys

app = Flask(__name__)


@app.route('/', methods=['POST'])
def execute():
    sys.stdout.write("Request received.\n")
    body = request.get_json()
    message = body['message']
    conversate(message)

    return "ok"

@app.route('/aidevs_api', methods=['POST'])
def aidevs_api():
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import StrOutputParser
    body = request.get_json()
    message = body['question']
    sys.stdout.write(f"Message: {message}\n")
    prompt = ChatPromptTemplate.from_template("{message}")
    llm = ChatOpenAI(model='ft:gpt-3.5-turbo-1106:personal::8SkYi0jA', temperature=0)
    chain = prompt | llm | StrOutputParser()
    output = chain.invoke({'message': message})
    response = {"reply": output}

    return response


if __name__ == '__main__':
    app.run(debug=True)