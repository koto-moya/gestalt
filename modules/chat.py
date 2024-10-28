from .db import *
import ollama


def generate_new_message(messages: list, new_message: str):
    formatted_message = {'role':'user', 'content':new_message}
    chat_state = messages.append(formatted_message) 
    response = ollama.chat(model="calebfahlgren/natural-functions", messages=chat_state)
    chat_state.append({'role':'assistant', 'content':response['message']['content']})
    return response['message']['content'], chat_state

