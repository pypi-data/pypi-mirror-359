# MmRAG-SDK
MmRAG-SDK is a simple Python SDK designed to make testing easier by eliminating the need to send HTTP requests from the terminal or script them manually.

# 🚀 How to Use
1. Set Up Your Environment:

I recommend using uv to manage your environment:
```
uv init .
uv add mmragsdk
```
Otherwise, with pip:
```
python3 -m venv .venv
. .venv/bin/activate
pip install mmragsdk
```
That’s it! Your environment is ready.


2. Initialize the SDK

Import and initialize the Client:
```
from mmragsdk import Client


client = Client(token='your_token_here')
```
> 💡 Note: To obtain a token, please email me at tambascomarco35@gmail.com and I will generate one for you.

## Available Methods
```
# Send a prompt
client.chat(prompt="your prompt here")
# - prompt: str
# - Raises ValueError if the prompt is empty

# Upload a file
client.upload(file_path="path/to/your/file.txt")
# - file_path: str
# - Raises FileNotFoundError if the file does not exist

# Perform a search
client.search(query="your search query")
# - query: str
# - Raises ValueError if the query is empty

# Clean storage
client.clean()
# - No parameters
# - ⚠️ DANGER: This method clears all stored data
```

# 🎉 Have Fun!
Enjoy a smooth and hassle-free testing experience with MmRAG-SDK. If you have questions or suggestions, feel free to reach out!
