import gradio as gr
import os
import time
from chat import chat
from search import search
from fetch import fetch
from image_generate import image_generate
from mnist import image_classification
from stt import audio2text
from tts import text2audio
import hashlib

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

messages = []
current_file_text = None

sound_pieces=0
sound_path='./sounds/'


history_dict={}

def getHashKey(text):
    ##把文本输入进来，得到文本的特征key，用此key映射到此文本的消息类型以及其他的附加消息
    hash=hashlib.sha256()
    hash.update(text.encode('utf-8'))
    hash_value=hash.hexdigest()
    return hash_value

def add_text(history, text):
    global messages
    global history_dict
    global sound_pieces
    if '/search' in text:
        history_dict[getHashKey(text)]=['search',None]
        results = search(text[8:])
        messages = messages + [{"role": "user", "content": f"Please answer {text[8:]} based on the search result: \n\n{results}"}]
        history = history + [(text, None)]
    elif '/fetch' in text:
        history_dict[getHashKey(text)]=['fetch',None]
        processed_results = fetch(text[7:])
        messages = messages + [{"role": "user", "content": f"Please summarize: \n\n{processed_results}"}]
        history = history + [(text, None)]
    elif '/image' in text:      # 图片生成
        history_dict[getHashKey(text)]=['image',None]
        messages = messages + [{"role": "user", "content": text}]
        print('add_text:',text)
        history = history + [(text, None)]
    elif '/audio' in text:
        sound_pieces+=1
        filename=str(sound_pieces)+'.wav'
        history_dict[getHashKey(text)]=['audio',filename] #这个标签表示[类型，文件]
        messages = messages + [{"role": "user", "content": text[7:]}]
        history = history + [(text, None)]
    else:
        history_dict[getHashKey(text)]=['chat',None]
        messages = messages + [{"role": "user", "content": text}]
        history = history + [(text, None)]
    
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    global messages
    if 'png' == file.name[-3:]:    # 图片分类
        results = image_classification(file.name)
        messages = messages + [{"role": "user", "content": f"Please classify {file.name}"}]
        messages = messages + [{"role": "assistant", "content": f"Classification result:{results}"}]
        history = history + [((file.name,), f"Classification result:{results}")]
    elif '.wav' == file.name[-4:]:
        text= audio2text(file.name)
        messages = messages + [{"role": "user", "content": f"Please transcribe {file.name}"}]
        messages = messages + [{"role": "assistant", "content": text}]
        history = history + [((file.name,), text)]
    # TODO: 是否更新 messages？
    return history


def bot(history):
    global messages
    global history_dict
    collected_response = ''
    print('history:', history)
    if(history[-1][1] == None):
        # 需要调用语言模型的情况
        label=history_dict[getHashKey(history[-1][0])] #从用户的text获取hash值作为key
        if label[0] == 'chat' or label[0] == 'fetch' or label[0] == 'search':
            response_generator = chat(messages)
            history[-1][1] = ''
            for response in response_generator:
                print(response)
                collected_response += response
                history[-1][1] += response
                time.sleep(0.05)
                yield history
            messages += [{"role": "assistant", "content": collected_response}]
        elif label[0] == 'audio':
            response_generator = chat(messages)
            for response in response_generator:
                collected_response += response
            messages = messages + [{"role": "assistant", "content": collected_response}]
            text2audio(collected_response,label[1])
            history[-1][1]=(sound_path+label[1],)
            yield history
        elif label[0] == 'image':
            text=history[-1][0]
            results = image_generate(text[7:])   
            messages = messages + [{"role": "assistant", "content": results}]
            history[-1][1]=(results,)
            yield history
            
    else:
        # 不需要调用语言模型，history和messages都已经更新完毕的情况
        yield history
    
    # TODO：response的格式处理？
    print(f'messages: {messages}')
   
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear_btn.click(lambda: messages.clear(), None, chatbot, queue=False)

demo.queue()
demo.launch()
