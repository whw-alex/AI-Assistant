import os
import requests
import openai
import json
from typing import List, Dict

openai.api_key = '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'
openai.api_base = "http://166.111.80.169:8080/v1"

api_key = "ff92e536a82e47839a9e1520d11acf74"
TODO_list = []

def lookup_location_id(location: str):
    url = 'https://geoapi.qweather.com/v2/city/lookup?'
    params = {
        'location': location,
        'key': api_key,
    }
    infos = requests.get(url=url, params=params).json()
    return infos["location"][0]["id"]

def get_current_weather(location: str):
    url = 'https://api.qweather.com/v7/weather/now?'
    params = {
        'location': lookup_location_id(location),
        'key': api_key,
    }
    infos = requests.get(url=url, params=params).json()
    print(infos)
    temp = infos["feelsLike"]
    text = infos["text"]
    hmd = infos["humidity"]
    return f"Temperature: {temp} Description: {text} Humidity: {hmd}"

def add_todo(todo: str):
    TODO_list.append(todo)
    table = ""
    for item in TODO_list:
        table += ("- " + todo + "\n")
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
        available_functions = {
            "get_current_weather": get_current_weather,
            "add_todo": add_todo
        } 

        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_arg = response_message["function_call"]["arguments"].values()[0]

        return function_to_call(function_arg)

    return None
        

if __name__ == "__main__":
    messages = [{"role": "user", "content": "Add a todo: walk"}]
    response = function_calling(messages)
    print(response)
    
    messages = [{"role": "user", "content": "What's the weather like in Beijing?"}]
    response = function_calling(messages)
    print(response)
