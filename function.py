import os
import requests
import openai
import json
from typing import List, Dict

openai.api_key = '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'
openai.api_base = "http://166.111.80.169:8080/v1"

key = "ff92e536a82e47839a9e1520d11acf74"
TODO_list = []

def lookup_location_id(location: str):
    url = 'https://geoapi.qweather.com/v2/city/lookup?'
    params = {
        'location': location,
        'key': key,
    }
    infos = requests.get(url=url, params=params).json()
    return infos["location"][0]["id"]

def get_current_weather(location: str):
    url = 'https://devapi.qweather.com/v7/weather/now?'
    params = {
        'location': lookup_location_id(location),
        'key': key,
    }
    infos = requests.get(url=url, params=params).json()
    print(infos)
    temp = infos['now']["feelsLike"]
    text = infos['now']["text"]
    hmd = infos['now']["humidity"]
    return f"Temperature: {temp} Description: {text} Humidity: {hmd}"

def add_todo(todo: str):
    TODO_list.append(todo)
    table = ""
    for item in TODO_list:
        table += ("- " + item + "\n")
    return table[:-1]

def function_calling(messages: List[Dict]):
    print("start function call......")
    functions = [
        # function1: get_current_weather，获取当前天气状况
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. Beijing",
                    },
                },
                "required": ["location"],
            },
        },
        # function2: add_todo，增添TODO项
        {
            "name": "add_todo",
            "description": "Add a new todo item into the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo": {
                        "type": "string",
                        "description": "A thing that needs to be done, e.g. walk",
                    },
                },
                "required": ["todo"],
            },
        }
    ]

    response = openai.ChatCompletion.create(
        model = "openllama",
        messages = messages,
        functions = functions
    )
    response_message = response["choices"][0]["message"]
    print(response_message)

    if "function_call" in response_message:
        available_function_infos = {
            "get_current_weather": (get_current_weather, "location"),
            "add_todo": (add_todo, "todo")
        }

        function_name = response_message["function_call"]["name"]
        function_info = available_function_infos[function_name]
        function_arg = json.loads(response_message["function_call"]["arguments"])[function_info[1]]

        return function_info[0](function_arg)

    return None
        

if __name__ == "__main__":
    # messages = [{"role": "user", "content": "Add a todo: walk"}]
    # response = function_calling(messages)
    # print(response)
    
    # messages = [{"role": "user", "content": "What's the weather like in Beijing?"}]
    # response = function_calling(messages)
    # print(response)
    get_current_weather("Beijing")
