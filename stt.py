import requests
import os
import openai


# TODO： 更换api_key
openai.api_key = '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'
openai.api_base = "http://166.111.80.169:8080/v1"

def audio2text(filename):
    """
    TODO
    """
    file=open(filename,'rb')
    result=openai.Audio.transcribe(model="whisper-1",file=file)
    text=''
    segments=result['segments']
    for seg in segments:
        text+=seg['text']
        text+=' '
    return text


if __name__ == "__main__":
    audio2text('./sun-wukong.wav')