import os
import openai

# TODO： 更换api_key
openai.api_key = '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'
openai.api_base = "http://166.111.80.169:8080/v1"

def image_generate(content: str):

    response = openai.Image.create(
        prompt=content,
        size="256x256"
    )
    img = response['data'][0]['url']
    return img

if __name__ == "__main__":
    image_generate('A cute baby sea otter')