from .db import *
import ollama
import asyncio
from typing import List, AsyncGenerator

async def generate_new_message_stream(messages: List[dict], new_message: str) -> AsyncGenerator[str, None]:
    formatted_message = {'role':'user', 'content':new_message}
    messages.append(formatted_message)
    response = await asyncio.to_thread(ollama.chat, model="tinyllama", messages=messages, stream=True)
    for chunk in response:
        yield chunk["message"]["content"]
        await asyncio.sleep(0)


async def generate_new_message(messages: list, new_message: str):
    formatted_message = {'role':'user', 'content':new_message}
    messages.append(formatted_message)
    print(messages)
    response = ollama.chat(model="tinyllama", messages=messages)
    
    print(response)
    messages.append({'role':'assistant', 'content':response['message']['content']})
    return response['message']['content'], messages

