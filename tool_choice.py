from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import create_openai_fn_runnable
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
import requests
from datetime import datetime
import telegram_con
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

task_hook = 'https://hook.eu1.make.com/spamxm6lfcrycw8tdajlwb2qifj0spok'


class OptionalDate(BaseModel):
    """Either a date or null."""

    date: Optional[str] = Field(
        None,
        description="date in '2016/06/20' format or '2016/06/20 17:26' format if provided in user input."
                    "null if no date provided in user input",
    )


def add_task(name: str, decription: str, date: OptionalDate):
    """Add task to todo list."""
    request_body = {'action': 'add', 'name': name, 'description': decription}
    date = date['date']
    if date:
        request_body['date'] = date

    requests.post(task_hook, json=request_body)
    #telegram_con.send_msg(f'Added task: {name} to todo list')


def list_tasks():
    """call that function if user asked you to list all the tasks"""
    request_body = {'action': 'list'}
    requests.post(task_hook, json=request_body)


llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", f"You are a helpful assistant. Remember, today is {datetime.today().strftime('%d-%m-%Y')}."),
        ("user", "User input:'''{input}'''"),
    ]
)
runnable = create_openai_fn_runnable([add_task, list_tasks], llm, prompt)


def tool_choice(user_input):
    output = runnable.invoke({"input": user_input})
    # run function
    globals()[output["name"]](**output["arguments"])
