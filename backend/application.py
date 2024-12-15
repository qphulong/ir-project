from .binary_quantized_rag.retriever import Retriever
from .naive_rag import Generator
from .nomic_embed import NomicEmbed
from .utils import *
from pprint import pprint
from memory_profiler import profile
from .query_preprocessor import QueryPreprocessor
from qdrant_client.conversions.common_types import ScoredPoint
from typing import List
import os
import json

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
    
    def _search_text_space(self, user_query:str, top_k: int=8) -> List[ScoredPoint]:
        """
        Private method to search text space

        Args:
            - user_query (str): User query string
            - top_k (int): Get top top_k results 

        Returns:
            - List[ScoredPoint]: List of results (id, similarity score, ...)

        Example outputs:
        [ScoredPoint(id='medium_c20340289683_text_12', version=0, score=25094.0, payload={}, vector=None, shard_key=None, order_value=None), 
        ScoredPoint(id='medium_610bbb304850_text_3', version=0, score=25853.0, payload={}, vector=None, shard_key=None, order_value=None)]
        """
        query_embedding = self.text_embed_model._get_embeddings_for_image_query(user_query)
        query_embedding = binary_quantized(query_embedding)
        search_results = self.retriever.qdrant_local.search(
            collection_name='text_space',
            query_vector=query_embedding,
            limit=top_k,
        )
        return search_results
    
    def _search_metadata_space(self, user_query:str, top_k:int = 8) -> List[ScoredPoint]:
        """Like above"""
        query_embedding = self.text_embed_model._get_embeddings_for_image_query(user_query)
        query_embedding = binary_quantized(query_embedding)
        search_results = self.retriever.qdrant_local.search(
            collection_name='metadata_space',
            query_vector=query_embedding,
            limit=top_k,
        )
        return search_results
    
    def _search_image_space(self, user_query:str, top_k:int =8) -> List[ScoredPoint]:
        """Like above but for images"""
        query_embedding = self.text_embed_model._get_embeddings_for_image_query(user_query)
        search_results = self.retriever.qdrant_local.search(
            collection_name='image_space',
            query_vector=query_embedding,
            limit=top_k,
        )
        return search_results
    
    def _get_all_text_from_fragment_id(self, point_id:str) -> str:
        """
        Get all document content base on the id of that document elements
        
        Args:
            - point_id: id of the 'Point' in vector space
                For example,
                chunked text id: cnn_L19wYWdlcy9jbHc3eHZ2YmEwMDAwYmpwZDNuaG1hYnFo_text_5
                image id: cnn_L19wYWdlcy9jbHc3eHZ2YmEwMDAwYmpwZDNuaG1hYnFo_image_4
                metadata_id: cnn_L19wYWdlcy9jbHc3eHZ2YmEwMDAwYmpwZDNuaG1hYnFo

        Returns:
            - str: Concated string of all text element in that document
        """
        post_id = point_id.split('_text_')[0].split('_image_')[0]
        json_file_path = os.path.join(self.retriever.database_path, f"{post_id}.json")
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            document_data = json.load(json_file)
        content_dict = document_data['content']
        output_str = ''
        for key,value in content_dict.items():
            chunked_text = value['content'] + "\n"
            output_str +=chunked_text
        return output_str