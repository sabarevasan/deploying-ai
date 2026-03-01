import gradio as gr
from run import route_input

# Memory (chat history)
chat_history = []


def chat_fn(user_message, history):
    response = route_input(user_message)

    history.append((user_message, response))
    return history, history


with gr.Blocks() as app:
    gr.Markdown("🍋 LemonAI helper")
    gr.Markdown("Ask about Fundamental Python, stocks (limited to AAPL, TSLA, MSFT, AMZN, GOOGL, META, NVDA, NFLX), or as a Task Manager!")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="How may I assist you?", placeholder="e.g.: explain inheritance in python.... or amazon stock insights.... or add/delete/view your tasks")

    state = gr.State([])

    msg.submit(chat_fn, [msg, state], [chatbot, state])
    msg.submit(lambda: "", None, msg)


app.launch()