import gradio as gr
from run import route_input

# Memory (chat history)
chat_history = []


def chat_fn(user_message, history):
    response = route_input(user_message)

    history.append((user_message, response))
    return history, history


with gr.Blocks() as app:
    gr.Markdown("#Python | Stocks | Tasks helper")
    gr.Markdown("Ask about Python, stocks, or manage your tasks!")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Type your message here...")

    state = gr.State([])

    msg.submit(chat_fn, [msg, state], [chatbot, state])
    msg.submit(lambda: "", None, msg)  # clear input


app.launch()