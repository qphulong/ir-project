from .binary_quantized_rag.retriever import Retriever
from .naive_rag import Generator
from .nomic_embed import NomicEmbed
from .utils import *
from pprint import pprint
from memory_profiler import profile
from .query_preprocessor import QueryPreprocessor

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
        self.query_preprocessor = QueryPreprocessor()

    def begin(self):
        """
        Chat with retrieval system (stand-alone questions answering, 
        conversation not supported)

        For every query,
        The retriever will get the data in text space, if the not enough information it will search in 
        metadata space, if not informative enough, it will call search_internet function.

        Image retrieval is just a side retrieval.
        """
        while(1):
            query = input("Query: ")
            if query == '/exit':
                return           

            # get query_embedding and search images space
            query_embedding = self.text_embed_model._get_embeddings_for_image_query(query)
            img_urls = self.retriever.search_image_space(query_embedding)
            query_embedding = binary_quantized(query_embedding)
            
            # search text space
            texts = self.retriever.search_text_space(query_embedding)
            document_str = ""
            for i,text in enumerate(texts):
                document_str += f"Document {i}:\n{text}\n\n"
            response = self.generator.check_informative(user_query=query,documents_str=document_str)
            print(response)
            if response != 'False': # If response if informative, continue to next loop/question
                print(response)
                continue
            
            # search metadata space
            metadatas = self.retriever.search_metadata_space(query_embedding)
            document_str = ""
            for i,metadata in enumerate(metadatas):
                document_str += f"Document {i}:\n{metadata}\n\n"
            response = self.generator.check_informative(user_query=query,documents_str=document_str)
            print(response)
            if response != 'False': # If response if informative, continue to next loop/question
                print(response)
                continue
            
            # if both search fail, search internet and try again
            search_query = self.query_preprocessor.process_query_for_search(query)
            self.search_internet(search_query=search_query)

            # Re-search vector store
            texts = self.retriever.search_text_space(query_embedding)
            document_str = ""
            for i,text in enumerate(texts):
                document_str += f"Document {i}:\n{text}\n\n"
            response = self.generator.check_informative(user_query=query,documents_str=document_str)
            if response != 'False': # If response if informative, continue to next loop/question
                print(response)
                continue   

            metadatas = self.retriever.search_metadata_space(query_embedding)
            document_str = ""
            for i,metadata in enumerate(metadatas):
                document_str += f"Document {i}:\n{metadata}\n\n"
            response = self.generator.generate(query,document_str)
            print(response)
    
    def search_internet(self,search_query:str,n_cnn:int=4,n_medium:int=4):
        """
        Function to crawl realtime posts on CNN and medium

        Results:
            - n posts on medium and cnn save to local json database
            - new vectors added to RAM in the current session
        """
        # TODO: phan cua a Hao, see class Retriever to use function to add vectors to ram
        pass

    def preprocess_query(self, user_query:str, k:int =3):
        """
        Preprocess query, if user is not confident about the thing they describe,
        this would suggest refined and quality queries

        Input:
            user_query (str): A complex and hard to understand query
            k (int): Number of suggestions

        Returns:
            - List[str]: a list of refined queries
        """
        return self.query_preprocessor.preprocess_query(query=user_query,k=k)