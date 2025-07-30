ChatJoiner
A simple and efficient utility for chat operations.

Installation
You can install the library from PyPI:

pip install chatjoiner-decoy-lib

(Note: Use the name you chose in pyproject.toml)

Usage
Here is a simple example of how to use the library:

from chatjoiner import join_chats

# You can pass any arguments to the function.
# They will all be ignored.
result = join_chats(
    chat_id="alpha-7", 
    user_token="user-xyz-token", 
    config={"mode": "silent", "reconnect": True}
)

# The output will always be the same.
print(result)
# Expected output: hello232323
