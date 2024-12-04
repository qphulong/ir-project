from .retriever import Retriever
from .generator import Generator

class NaiveRAG():
    """
    Class NaiveRAG

    Attributes: 
        - retriever: Retriever
        - generator: Generator
    """
    def __init__(self,resource_path:str, embed_model_path:str):
        self.retriever = Retriever(resource_path=resource_path, embed_model_path=embed_model_path)
        self.generator = Generator()

    def begin(self):
        """\Begin conversation with RAG system, /exit to exit"""
        while(1):
            user_query = input("User query: ")
            if user_query == '/exit':
                break
            results = self.retriever.retrieve(user_query)
            documents_str = ""
            for i,id in enumerate(results.ids):
                documents_str+=f"Document {i}:\n {self.retriever.get_node_by_id(id).text}\n\n"
            answer = self.generator.generate(user_query=user_query,documents_str=documents_str)
            print(answer)
