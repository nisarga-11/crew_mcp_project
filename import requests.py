import requests

response = requests.post(
    "http://127.0.0.1:11434/run/llama2",
    json={"prompt": "Hello Ollama! Convert this to JSON."}
)
print(response.json())
