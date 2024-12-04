from openai import OpenAI

from typing import List
from llama_index.core.schema import Document as LLamaDocument

class Generator():
    def __init__(self) -> None:
        self.model = OpenAI()

    def generate(self, user_query:str ,documents_str:str) -> str:
        completion = self.model.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", 
                 "content": """You are an assistant for question-answering tasks.
                    The user will provide their query and documents.
                    Use the provided documents to answer the question.
                    If the document does not provide enough information, please say the document does not provide enough information.
                """
                },
                {
                    "role": "user",
                    "content": f"Query: {user_query}\nDocuments:\n{documents_str}"
                }
            ]
        )
        return completion.choices[0].message.content