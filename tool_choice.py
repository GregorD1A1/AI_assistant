from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from todoist_tasks import correct_task
from todoist_tasks import get_tasks_in_date_range
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

conversation_id = ''
airtable = Airtable('appGWWQkZT6s8XWoj', 'tbllSz6YkqEAltse1', airtable_token)


def add_task(name: str, description: str, date=None):
    """Add task to todo list."""
    request_body = {'action': 'add_task', 'name': name, 'description': description}
    if date:
        request_body['date'] = date

    response = requests.post(task_hook, json=request_body)
    print(response.json())

    if response.status_code == 200 and response.json()['success']:
        return f"Added task {name}"
    else:
        return "Wasn't added task. Something went wrong"


def list_tasks(start_date, end_date):
    """call that function if user asked you to list all the tasks"""
    # if start_date available, list tasks in date range
    if start_date and end_date:
        tasks = get_tasks_in_date_range(start_date, end_date)
        tasks = ", ".join(tasks)
        sys.stdout.write(f"Tasks in date range: {tasks}")

    return f"all the tasks: '{tasks}'"


def edit_task(name, new_name=None, description=None, date=None):
    """call that function if user asked you to edit task"""

    response = correct_task(name, new_name, description, date)
    sys.stdout.write("If task edited:")
    sys.stdout.write(response)


def add_info(information, type, tags, name=None):
    """Add information piece to memory base to remember it. call that function if user provided affirmative statement with some info."""
    request_body = {'info': information, 'type': type, 'tags': tags, 'id': str(uuid.uuid4())}
    if name:
        request_body['name'] = name
    response = requests.post(momories_hook, json=request_body)

    if response.status_code == 200:
        return f"Added information {information}"


def add_friend(name: str, description: str, tags: str, city=None, contact=None):
    """Add friend to friends list."""
    request_body = {'action': 'add_friend', 'name': name, 'description': description,
                    'tags': tags, 'id': str(uuid.uuid4())}
    if city:
        request_body['city'] = city
    if contact:
        request_body['contact'] = contact
    sys.stdout.write(str(request_body))
    response = requests.post(friends_hook, json=request_body)
    # check if response 200
    if response.status_code == 200:
        return f"Added friend {name}"


def new_conversation():
    global conversation_id
    conversation_id = str(uuid.uuid4())
    airtable.insert({'uuid': conversation_id, 'Conversation': '[]'})

    return "Started new conversation"


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
                        "description": "date in DD.MM.YYYY or DD.MM.YYYY HH:MM format if provided in user input. "
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
                        "description": "start date of task listing in DD.MM.YYYY",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "end date of task listing in DD.MM.YYYY",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function":
        {
            "name": "edit_task",
            "description": "Edit task data if some parameters were changed",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Exact name of task",
                    },
                    "new_ name": {
                        "type": "string",
                    },
                    "description": {
                        "type": "string",
                    },
                    "date": {
                        "type": "string",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function":
        {
            "name": "add_info",
            "description":
                "Add information piece about interesting service or piece of technichal knowledge Grigorij gained "
                "to memory base. Use English.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "name if needed",
                    },
                    "information": {
                        "type": "string",
                        "description": "information piece to remember. Keep it short and concise with important data only.",
                    },
                    "type": {
                        "type": "string",
                        "description": "type of information, e.g. service, technical knowledge",
                        "enum": ["Services", "Tech_knowledge"],
                    },
                    "tags": {
                        "type": "string",
                        "description":
                            "Tags related to technology used or service functionality. "
                            "Avoid general tags as 'programming', 'app development' etc., but specify concrete technology. "
                            "Use small amount of tags only directly related. Separated by comma",
                    },
                },
                "required": ["information", "type", "tags"],
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
    {
        "type": "function",
        "function":
        {
            "name": "new_conversation",
            "description": "Start new conversation.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]

def tool_choice(user_input):
    client = OpenAI()

    if not conversation_id:
        new_conversation()
    messages = airtable.match('uuid', conversation_id)['fields']['Conversation']
    messages = json.loads(messages)

    messages.append({
      "role": "system",
      "content": f"You are Szarik, Grigorij's personal assistant. Today is {datetime.today().strftime('%d.%m.%Y')} d.m.Y."
                 f"Your responses are short and concise."
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
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            print(function_name)
            funct_response = globals()[function_name](**function_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": funct_response
            })

        second_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            temperature=0.7,
        )
        response_message = second_response.choices[0].message
        response_content = response_message.content



    # save conversation history
    if response_content:
        print(response_content)
        messages.append({"role": "assistant", "content": response_content})
        # remove system message
        messages.pop(0)
        # remove all messages of type other than dict
        messages = [message for message in messages if isinstance(message, dict)]
        # remove all messages of if message['role'] == 'tool_call'
        messages = [message for message in messages if message['role'] != 'tool']

        # save prompt as json file
        print(messages)
        airtable.update_by_field('uuid', conversation_id, {'Conversation': json.dumps(messages)})

        telegram_con.send_voice(response_content)


if __name__ == '__main__':
    tool_choice("Dodaj zadanie xddkochać koty?")
