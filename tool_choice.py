from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import create_openai_fn_runnable
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
from openai import OpenAI
import requests
from datetime import datetime
import uuid
from airtable import Airtable
import telegram_con
import sys
import json
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
airtable_token = os.getenv('AIRTABLE_API_TOKEN')

task_hook = 'https://hook.eu1.make.com/spamxm6lfcrycw8tdajlwb2qifj0spok'
momories_hook = 'https://hook.eu2.make.com/3y9bun2efpae5h05ki5u62gc18uqqmwl'
friends_hook = 'https://hook.eu2.make.com/ui1m997zqbtugc4qm7925n3yr0om7oc5'


def add_task(name: str, description: str, date=None):
    """Add task to todo list."""
    request_body = {'action': 'add_task', 'name': name, 'description': description}
    if date:
        request_body['date'] = date

    requests.post(task_hook, json=request_body)


def list_tasks(start_date, end_date):
    """call that function if user asked you to list all the tasks"""
    from todoist_tasks import get_tasks_in_date_range
    # if start_date available, list tasks in date range
    if start_date and end_date:
        tasks = get_tasks_in_date_range(start_date, end_date)
        tasks = ", ".join(tasks)
        sys.stdout.write(f"Tasks in date range: {tasks}")
    request_body = {'action': 'say_tasks', 'tasks': tasks}
    requests.post(task_hook, json=request_body)


def add_info(information: str):
    """Add information piece to memory base to remember it. call that function if user provided affirmative statement with some info."""
    request_body = {'action': 'add_memory', 'memory': information, 'id': str(uuid.uuid4())}
    requests.post(momories_hook, json=request_body)


def add_friend(name: str, description: str, tags: str, city=None, contact=None):
    """Add friend to friends list."""
    request_body = {'action': 'add_friend', 'name': name, 'description': description,
                    'tags': tags, 'id': str(uuid.uuid4())}
    if city:
        request_body['city'] = city
    if contact:
        request_body['contact'] = contact
    sys.stdout.write(str(request_body))
    requests.post(friends_hook, json=request_body)


llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", f"You are Szarik, Grigorij's personal assistant. "
                   f"Remember, today is {datetime.today().strftime('%m/$d/%Y')}."),
        ("user", "User input:'''{input}'''"),
    ]
)
runnable = create_openai_fn_runnable([add_task, list_tasks, add_info, add_friend], llm, prompt)

tools = [
    {
        "type": "function",
        "function":
        {
            "name": "add_task",
            "description": "Add task to todo list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "task name",
                    },
                    "description": {
                        "type": "string",
                        "description": "task description",
                    },
                    "date": {
                        "type": "string",
                        "description": "date in MM/DD/YYYY or MM/DD/YYYY HH:MM format if provided in user input. "
                                       "null if no date provided in user input",
                    },
                },
                "required": ["name", "description"],
            },
        },
    },
    {
        "type": "function",
        "function":
        {
            "name": "list_tasks",
            "description": "List tasks in date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "start date of task listing in MM/DD/YYYY",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "end date of task listing in MM/DD/YYYY",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function":
        {
            "name": "add_info",
            "description": "Add information piece to memory base to remember it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "information": {
                        "type": "string",
                        "description": "information piece to remember",
                    },
                    "name": {
                        "type": "string",
                        "description": "name of service if some",
                    },
                    "link": {
                        "type": "string",
                        "description": "url of service if some",
                    }
                },
                "required": ["information"],
            },
        },
    },
    {
        "type": "function",
        "function":
        {
            "name": "add_friend",
            "description": "Add friend to friends list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "name of friend",
                    },
                    "description": {
                        "type": "string",
                        "description": "description of friend's interests, business, potential ways of cooperation",
                    },
                    "tags": {
                        "type": "string",
                        "description": "tags of friend, related to his interests, business, potential ways of cooperation. "
                                       "Separated by comma",
                    },
                    "city": {
                        "type": "string",
                        "description": "city friend lives",
                    },
                    "contact": {
                        "type": "string",
                        "description": "contact of friend",
                    },
                },
                "required": ["name", "description", "tags"],
            },
        },
    },
]

def tool_choice_old(user_input):
    output = runnable.invoke({"input": user_input})
    print(output)
    # run function
    function_name = output["name"]
    sys.stdout.write(f"LLM returned:\n{output}\n")
    print(output["arguments"])
    globals()[function_name](**output["arguments"])


def tool_choice(user_input):
    client = OpenAI()

    airtable = Airtable('appGWWQkZT6s8XWoj', 'tbllSz6YkqEAltse1', airtable_token)
    messages = airtable.search('uuid', 'dzik')[0]['fields']['Conversation']
    messages = json.loads(messages)

    messages.append({
      "role": "system",
      "content": f"You are Szarik, Grigorij's personal assistant. Remember, today is {datetime.today().strftime('%m/%d/%Y')}."
    })  # przenieść to na początek
    messages.append({"role": "user", "content": user_input})
    print(messages)

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        tools=tools,
        temperature=0.7,
    )
    response_message = response.choices[0].message
    response_content = response_message.content
    print(response_content)
    tool_calls = response_message.tool_calls
    if tool_calls:
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            print(function_name)
            print(function_args)
            globals()[function_name](**function_args)

    # save conversation history
    if response_content:
        messages.append({"role": "assistant", "content": response_content})
        # remove system message
        messages.pop(0)
        # save prompt as json file
        airtable.update_by_field('uuid', 'dzik', {'Conversation': json.dumps(messages)})

        telegram_con.send_msg(response_content)


if __name__ == '__main__':
    tool_choice("Tak, porozmawiajmy")
