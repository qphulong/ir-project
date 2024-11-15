from openai import OpenAI

class QueryPreprocessor:
    """
    A class used to preprocess user queries using OpenAI's GPT model.
    Methods
    -------
    __init__():
        Initializes the QueryPreprocessor with an OpenAI client.
    preprocess_query(query: str) -> str:
        Takes a user query as input, processes it using the OpenAI GPT model to translate it to English (if necessary),
        fix typos, and use regular vocabulary, then returns the processed query.
    """
    def __init__(self):
        self.client = OpenAI()

    def preprocess_query(self, query: str) -> str:
        """
        Preprocesses the given query by translating it to English (if necessary), fixing typos, and using regular vocabulary.

        Args:
            query (str): The query string to be preprocessed.

        Returns:
            str: The preprocessed query string.
        """
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful query re-writer. You should translate the query to English (if it not already is), fix all typo, use regular-used vocabulary."},
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        return completion.choices[0].message