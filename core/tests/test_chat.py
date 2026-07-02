from core.ollama_client import ask_model

messages = [{'role': 'user', 'content': 'Hello, who are you?'}]
answer = ask_model(messages)

print(answer)