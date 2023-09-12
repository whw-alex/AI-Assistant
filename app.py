import gradio as gr
import os
import time
from chat import chat
from search import search
from fetch import fetch

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

messages = []
current_file_text = None

def add_text(history, text):
    global messages
    if '/search' in text:
        results = search(text[8:])
        messages = messages + [{"role": "user", "content": f"Please answer {text[8:]} based on the searchresult: \n\n{results}"}]
    elif '/fetch' in text:
        processed_results = fetch(text[7:])
        messages = messages + [{"role": "user", "content": f"Please summarize: \n\n{processed_results}"}]
    else:
        messages = messages + [{"role": "user", "content": text}]
    history = history + [(text, None)]
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    global messages
    # TODO: 是否更新 messages？
    history = history + [((file.name,), None)]
    return history


def bot(history):
    global messages
    collected_response = ''
    response_generator = chat(messages)
    history[-1][1] = ''
    for response in response_generator:
        print(response)
        collected_response += response
        history[-1][1] += response
        time.sleep(0.05)
        yield history
    
    # TODO：response的格式处理？
    messages += [{"role": "assistant", "content": collected_response}]
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
