import os
import openai

# TODO： 更换api_key
openai.api_key = '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'
openai.api_base = "http://166.111.80.169:8080/v1"


def chat(messages):
    print('start chatting...')
    print(f'messages: {messages}')
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
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