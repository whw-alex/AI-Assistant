import gradio as gr
import os
import time
from chat import chat
from search import search
from fetch import fetch
from image_generate import image_generate
from pdf import generate_summary, generate_question, generate_text
from mnist import image_classification

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

messages = []
current_file_text = None
isTxt = False

def add_text(history, text):
    global messages
    global isTxt
    if '/search' in text:
        results = search(text[8:])
        messages = messages + [{"role": "user", "content": f"Please answer {text[8:]} based on the search result: \n\n{results}"}]
        history = history + [(text, None)]
        isTxt = False
    elif '/fetch' in text:
        processed_results = fetch(text[7:])
        messages = messages + [{"role": "user", "content": f"Please summarize: \n\n{processed_results}"}]
        history = history + [(text, None)]
        isTxt = False
    elif '/image' in text:      # 图片生成
        results = image_generate(text[7:])
        messages = messages + [{"role": "user", "content": text}]
        history = history + [(text, results)]
        isTxt = False
    elif '/file' in text:
        prompt = generate_question(current_file_text, text[6:])
        messages = messages + [{"role": "user", "content": prompt}]
        history = history + [(text, None)]
        isTxt = True
    else:
        messages = messages + [{"role": "user", "content": text}]
        history = history + [(text, None)]
        isTxt = False
    
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    global messages
    global isTxt
    print(history)
    if 'png' == file.name[-3:]:    # 图片分类
        results = image_classification(file.name)
        messages = messages + [{"role": "user", "content": f"Please classify {file.name}"}]
        messages = messages + [{"role": "user", "content": f"Classification result:{results}"}]
        history = history + [((file.name,), f"Classification result:{results}")]
        isTxt = False

    elif 'txt' == file.name[-3:]:
        current_file_text = file.read().decode("utf-8")   # 读取文件内容
        prompt = generate_summary(current_file_text)
        messages = messages + [{"role": "user", "content": prompt}]
        history = history + [((file.name,), None)]
        isTxt = True
    # TODO: 是否更新 messages？
    return history


def bot(history):
    global messages
    collected_response = ''
    print('bot his: ',history)
    if(history[-1][1] == None):
        # 需要调用语言模型的情况
        if isTxt:
            response_generator = generate_text(messages[-1]["content"])
        else:
            response_generator = chat(messages)
        history[-1][1] = ''
        for response in response_generator:
            print(response)
            collected_response += response
            history[-1][1] += response
            time.sleep(0.05)
            yield history
        messages += [{"role": "assistant", "content": collected_response}]
    else:
        # 不需要调用语言模型，history和messages都已经更新完毕的情况
        return history
    
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
