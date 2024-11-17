import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from openai import OpenAI
from backend import env
client = OpenAI()

"""
This script test if open ai api key loaded correctly.
If yes, you will recieve a message from gpt-4o-mini
"""

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "hello chat gpt"
        }
    ]
)

print(completion.choices[0].message)