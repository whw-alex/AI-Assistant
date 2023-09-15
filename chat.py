import os
import openai


openai.api_key = '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'
openai.api_base = "http://166.111.80.169:8080/v1"

model='gpt-3.5-turbo'

def chat(messages):
    print('start chatting...')
    print(f'messages: {messages}')
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        stream=True
    )
    # 流式传输
    for chunk in response:
        if 'content' in chunk['choices'][0]['delta']:
            content = chunk['choices'][0]['delta']['content']
            yield content

    # 完整回答
    # return response['choices'][0]['message']['content']