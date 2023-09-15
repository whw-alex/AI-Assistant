import gradio as gr
import os
import time
from chat import chat
from search import search
from fetch import fetch
from image_generate import image_generate
from pdf import generate_summary, generate_question, generate_text
from mnist import image_classification
from stt import audio2text
from tts import text2audio
from function import function_calling
import hashlib

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

messages = []
current_file_text = None

sound_pieces=0
sound_path='./sounds/'

# key: 输入的标识，即(user, assistant)的user项; value: [类型，文件]，类型
history_dict={}

def getHashKey(text):
    ##把文本输入进来，得到文本的特征key，用此key映射到此文本的消息类型以及其他的附加消息
    if(type(text)==tuple):
        str_text='('+text[0]+',)'
    else: 
        str_text=text
    hash = hashlib.sha256()
    hash.update(str_text.encode('utf-8'))
    hash_value = hash.hexdigest()
    return hash_value

def add_text(history, text):
    global messages
    global history_dict
    global sound_pieces
    
    print('add_text his:',history)
    if '/search' == text[0:7]:
        results = search(text[8:])
        messages = messages + [{"role": "user", "content": f"Please answer {text[8:]} based on the search result: \n\n{results}"}]
        history = history + [(text, None)]
        history_dict[getHashKey(text)] = ['search', None]

    elif '/fetch' == text[0:6]:
        processed_results = fetch(text[7:])
        messages = messages + [{"role": "user", "content": f"Please summarize: \n\n{processed_results}"}]
        history = history + [(text, None)]
        history_dict[getHashKey(text)] = ['fetch', None]

    elif '/image' == text[0:6]:      # 图片生成
        messages = messages + [{"role": "user", "content": text}]
        history = history + [(text, None)]
        history_dict[getHashKey(text)] = ['image', None]

    elif '/file' == text[0:5]:
        prompt = generate_question(current_file_text, text[6:])
        messages = messages + [{"role": "user", "content": prompt}]
        print('add_text:',text)
        history = history + [(text, None)]
        history_dict[getHashKey(text)] = ['file', None]

    elif '/audio' == text[0:6]:
        sound_pieces+=1
        filename=str(sound_pieces)+'.wav'
        messages = messages + [{"role": "user", "content": text[7:]}]
        history = history + [(text, None)]
        history_dict[getHashKey(text)] = ['audio', filename] 

    elif '/function' == text[0:9]:
        messages = messages + [{"role": "user", "content": text[10:]}]
        history = history + [(text, None)]
        history_dict[getHashKey(text)] = ['function', None]

    else:
        messages = messages + [{"role": "user", "content": text}]
        history = history + [(text, None)]
        history_dict[getHashKey(text)] = ['chat', None]
    
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    global messages
    global current_file_text
    print('add_file his:',history)
    if 'png' == file.name[-3:]:    # 图片分类
        messages = messages + [{"role": "user", "content": f"Please classify {file.name}"}]
        history = history + [((file.name,), None)]
        history_dict[getHashKey((file.name,))] = ['png', file.name]
        

    elif 'txt' == file.name[-3:]:
        with open(file.name, "r", encoding='utf-8') as f:  #打开文本
            current_file_text = f.read()   #读取文本
        prompt = generate_summary(current_file_text)
        messages = messages + [{"role": "user", "content": prompt}]
        history = history + [((file.name,), None)]
        history_dict[getHashKey((file.name,))] = ['txt', None]

    elif '.wav' == file.name[-4:]:
        messages = messages + [{"role": "user", "content": f"Please transcribe {file.name}"}]
        history = history + [((file.name,), None)]
        history_dict[getHashKey((file.name,))] = ['wav',file.name]
        
    # TODO: 是否更新 messages？
    return history


def bot(history):
    global messages
    global history_dict
    collected_response = ''
    print('bot his: ',history)
    if(history[-1][1] == None):
        label=history_dict[getHashKey(history[-1][0])] #从用户的text获取hash值作为key
        
        if label[0] == 'chat' or label[0] == 'fetch' or label[0] == 'search':
            response_generator = chat(messages)
            history[-1][1] = ''
            for response in response_generator:
                print(response)
                collected_response += response
                history[-1][1] += response
                yield history
            messages += [{"role": "assistant", "content": collected_response}]
        
        elif label[0] == 'file' or label[0] == 'txt':
            response_generator = generate_text(messages[-1]["content"])
            history[-1][1] = ''
            for response in response_generator:
                print(response)
                collected_response += response
                history[-1][1] += response
                yield history
            if history[-1][1] == '':
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
            text = history[-1][0]
            results = image_generate(text[7:])   
            messages = messages + [{"role": "assistant", "content": results}]
            history[-1][1]=(results,)
            yield history

        elif label[0] == 'function':
            response = function_calling(messages)
            messages = messages + [{"role": "assistant", "content": response}]
            history[-1][1] = response
            yield history
            
        elif label[0] == 'wav':
            print('loc 1')
            text= audio2text(label[1])
            print('loc 2')
            messages = messages + [{"role": "assistant", "content": text}]
            history[-1][1]=text
            yield history
            
        elif label[0] == 'png':
            results=image_classification(label[1])
            messages = messages + [{"role": "assistant", "content": f"Classification result:{results}"}]
            history[-1][1]=f"Classification result:{results}"
            yield history
            
        else:
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
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

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
