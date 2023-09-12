import requests
import os
import json

sound_path='./sounds/'

def text2audio(content: str,filename):
    """
    TODO
    """
    
    response=requests.post(url='http://166.111.80.169:8080/tts',data=json.dumps({
      "input": content,
      "model": "en-us-blizzard_lessac-medium.onnx",
    }),headers={
        'Content-Type': 'application/json'
    })
    with open(f'{sound_path+filename}','wb') as f:
        f.write(response.content)


if __name__ == "__main__":
    file=text2audio("Sun Wukong (also known as the Great Sage of Qi Tian, Sun Xing Shi, and Dou Sheng Fu) is one of the main characters in the classical Chinese novel Journey to the West")