from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import create_openai_fn_runnable
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
import requests
from datetime import datetime
import uuid
import telegram_con
import sys
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

task_hook = 'https://hook.eu1.make.com/spamxm6lfcrycw8tdajlwb2qifj0spok'
momories_hook = 'https://hook.eu2.make.com/3y9bun2efpae5h05ki5u62gc18uqqmwl'

class OptionalDate(BaseModel):
    """Either a date or null."""

    date: Optional[str] = Field(
        None,
        description="date in '2016/06/20' format or '2016/06/20 17:26' format if provided in user input."
                    "null if no date provided in user input",
    )

class FriendsData(BaseModel):
    """Data for friends."""

    name: str = Field(
        None,
        description="name of friend",
    )
    description: str = Field(
        None,
        description="description of friend's interests, business, potential ways of cooperation",
    )
    tags: str = Field(
        None,
        description="tags of friend, related to his interests, business, potential ways of cooperation. "
                    "Separated by comma",
    )
    city: Optional[str] = Field(
        None,
        description="city friend lives if given else null",
    )
    contact: Optional[str] = Field(
        None,
        description="contact of friend if given else null",
    )


def add_task(name: str, description: str, date: OptionalDate):
    """Add task to todo list."""
    request_body = {'action': 'add_task', 'name': name, 'description': description}
    date = date['date']
    if date:
        request_body['date'] = date

    requests.post(task_hook, json=request_body)


def list_tasks():
    """call that function if user asked you to list all the tasks"""
    request_body = {'action': 'list_tasks'}
    requests.post(task_hook, json=request_body)


def add_memory(memory: str):
    """Add memory piece to memory base to remember it."""
    request_body = {'action': 'add_memory', 'memory': memory, 'id': str(uuid.uuid4())}
    requests.post(momories_hook, json=request_body)

def add_friend(friends_data: FriendsData):
    """Add friend to friends list."""
    request_body = {'action': 'add_friend', 'name': friends_data['name'], 'description': friends_data['description'],
                    'tags': friends_data['tags']}
    if 'city' in friends_data:
        request_body['city'] = friends_data['city']
    if 'contact' in friends_data:
        request_body['contact'] = friends_data['contact']
    sys.stdout.write(str(request_body))

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", f"You are , Grigorij's personal assistant. "
                   f"Remember, today is {datetime.today().strftime('%d-%m-%Y')}."),
        ("user", "User input:'''{input}'''"),
    ]
)
runnable = create_openai_fn_runnable([add_task, list_tasks, add_memory, add_friend], llm, prompt)


def tool_choice(user_input):
    output = runnable.invoke({"input": user_input})
    # run function
    function_name = output["name"]
    sys.stdout.write(f"LLM returned:\n{output}\n")
    globals()[function_name](**output["arguments"])

tool_choice("Dodaj kolegę Andrzeja Lubelskiego, który lubi prgranować")