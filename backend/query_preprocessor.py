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

    def preprocess_query(self, query: str, k: int = 1) -> list[str] | None:
        """
        Preprocesses the given query by translating it to English (if necessary), fixing typos, and using regular vocabulary.

        Args:
            query (str): The query string to be preprocessed.

        Returns:
            queries: The list of preprocessed query strings.
                Format: [suggesttion?, query1, query2, ...]
            None if an error occurs.
        """
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
                 You are a helpful query re-writer. 
                 You should translate the query to English (if it not already is), fix all typo, remove all punctuations and stopwords, and use regular-used vocabulary.
                 Your input will be in a form:
                    Query: <query>\nK: <k>
                 Where <query> is a single user query and <k> is the number of queries you need to generate from that single user query.
                 You should return the queries after processing it, seperated by line break.
                 The input is guaranteed a user query, you might return edit suggestion if user's confirmation is required in the form:
                    Suggestion: <edit>
                 With <edit> is what you infer the user query is."""},
                {
                    "role": "user",
                    "content": f"Query: {query}\nK: {k}"
                }
            ]
        )
        try:
            res = completion.choices[0].message.content.split("\n")
        except Exception as e:
            return None
        return [r.strip() for r in res if r.strip() != ""]
    
    def process_query_for_search(self, query: str) -> str:
        """
        Processes a user query into a search-engine-friendly string by translating it to English (if necessary),
        fixing typos, removing punctuation and stopwords, and using simplified vocabulary.

        Args:
            query (str): The query string to be processed.

        Returns:
            str: A single, optimized query string for search engines.
                Returns an empty string if processing fails.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """
                    You are a helpful query optimizer for search engines.
                    Your goal is to transform user queries into a clean and optimized search query for web systems.
                    Steps:
                    - Translate the query to English (if not already).
                    - Fix typos and grammar errors.
                    - Remove punctuation and stopwords.
                    - Replace complex phrases with common and regular vocabulary.
                    - Ensure the final result is compact and highly relevant for search systems.

                    Input format:
                        Query: <query>
                    Output format:
                        <optimized_query>
                    """},
                    {
                        "role": "user",
                        "content": f"Query: {query}"
                    }
                ]
            )
            # Extract the response content
            optimized_query = completion.choices[0].message.content.strip()
            return optimized_query
        except Exception as e:
            return ""
