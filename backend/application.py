from .binary_quantized_rag.retriever import Retriever
from .naive_rag import Generator
from .nomic_embed import NomicEmbed
from .utils import *
from pprint import pprint
from memory_profiler import profile

class Application():
    """
    Application Class

    Attributes:
        retriever (Retriever): Responsible for data retrieval operation
        indexer (Indexer): Index raw data to database
        generator (Generator): Open AI LLM
        text_embed_model (NomicEmbed): generate embeddings for retrieval tasks
    """
    def __init__(self):
        self.retriever = Retriever()
        self.indexer = None #TODO implement class Indexer
        self.generator = Generator()
        self.text_embed_model = NomicEmbed()

    def begin(self):
        while(1):
            query = input("Query: ")
            if query == '/exit':
                return
            query_embedding = self.text_embed_model._get_embeddings_for_image_query(query)
            query_embedding = binary_quantized(query_embedding)
            print("Metadata found\n")
            pprint(
                self.retriever.search_metadata_space(query_embedding)
            )
            texts = self.retriever.search_text_space(query_embedding)
            print("Chunked texts found\n")
            pprint(texts)
            query_embedding = self.text_embed_model._get_embeddings_for_image_query(query)
            pprint(
                self.retriever.search_image_space(query_embedding)
            )
            document_str = ""
            for i,text in enumerate(texts):
                document_str += f"Document {i}:\n{text}\n\n"
            print(self.generator.generate(query,document_str))