import asyncio
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
from numpy import ndarray
from PIL.ImageFile import ImageFile
from .D2D import D2D
from .nomic_embed_vision import NomicEmbedVision
from .query_session import QuerySession, QueryState
from database import Indexer

class Application():
    """
    Application Class

    Attributes:
        retriever (Retriever): Responsible for data retrieval operation
        indexer (Indexer): Index raw data to database
        generator (Generator): Open AI LLM
        text_embed_model (NomicEmbed): generate embeddings for retrieval tasks
    """
    _instance = None

    # Make this class a singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Application, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Ensure __init__ is only called once
            self.retriever = Retriever()
            self.indexer = Indexer()
            self.generator = Generator()
            self.text_embed_model = NomicEmbed()
            self.query_preprocessor = QueryPreprocessor()
            self.initialized = True

    def insert_doc(self,path:str)->None:
        """Save the document in the database path (./resources/quantized-db) 
        and upload the vectors to vector space

        Args: 
            - path (str): file path
        Returns:
            - None

        Guilde
        1. Save the json in database path (retriever.database_path)
        2. For each chunked text, load that id + vector to retriever.text_space
        using self.retriever.add_point_to_text_space(point_id=,vector=)
        """
        try:
            data = self._load_doc(path)
        except:
            print(f"ERROR: Cannot load data from {path}")
            return
        self._save_data(os.path.join(self.retriever.database_path, f"{data['id']}.json"), data)
        for key, value in data['content'].items():
            point_id = key
            vector = value['embedding']
            vector = base64_to_binary_array(vector)
            self.retriever.add_point_to_text_space(point_id=point_id,vector=vector)
        """Uncomment this if you want to add image vectors to image space and D2D support image (currently not)
        for key, value in data['images'].items():
            point_id = key
            vector = value['embedding']
            self.retriever.add_point_to_image_space(point_id=point_id,vector=vector)"""


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
            img_urls, image_score_points = self.retriever.search_image_space(query_embedding)
            pprint("This is the list of image urls")
            pprint(img_urls)
            pprint("List of image id which you use to retrieve full document text")
            pprint(image_score_points)
            
            query_embedding = binary_quantized(query_embedding)
            
            # search text space
            texts, text_score_points  = self.retriever.search_text_space(query_embedding)
            document_str = ""
            for i,text in enumerate(texts):
                document_str += f"Document {i}:\n{text}\n\n"
            response = self.generator.check_informative(user_query=query,documents_str=document_str)
            if response != 'False': # If response if informative, continue to next loop/question
                pprint("This is the list of text show up on the right scroll box")
                pprint(texts)
                pprint("This is the list of result (id,similarity score) which you will use id to get full document text")
                pprint(text_score_points)
                print(response)
                continue
            
            # search metadata space
            metadatas,metadatas_score_points = self.retriever.search_metadata_space(query_embedding)
            document_str = ""
            for i,metadata in enumerate(metadatas):
                document_str += f"Document {i}:\n{metadata}\n\n"
            response = self.generator.check_informative(user_query=query,documents_str=document_str)
            if response != 'False': # If response if informative, continue to next loop/question
                pprint("This is the list of text show up on the right scroll box")
                pprint(metadatas)
                pprint("This is the list of result (id,similarity score) which you will use id to get full document text")
                pprint(metadatas_score_points)
                print(response)
                continue
            
            # if both search fail, search internet and try again
            search_query = self.query_preprocessor.process_query_for_search(query)
            self.search_internet(search_query=search_query)

            # Re-search vector store
            texts, text_score_points  = self.retriever.search_text_space(query_embedding)
            document_str = ""
            for i,text in enumerate(texts):
                document_str += f"Document {i}:\n{text}\n\n"
            response = self.generator.check_informative(user_query=query,documents_str=document_str)
            pprint("This is the list of text show up on the right scroll box")
            pprint(texts)
            if response != 'False': # If response if informative, continue to next loop/question
                pprint("This is the list of text show up on the right scroll box")
                pprint(texts)
                pprint("This is the list of result (id,similarity score) which you will use id to get full document text")
                pprint(text_score_points)
                print(response)
                continue   

            metadatas,metadatas_score_points = self.retriever.search_metadata_space(query_embedding)
            document_str = ""
            for i,metadata in enumerate(metadatas):
                document_str += f"Document {i}:\n{metadata}\n\n"
            response = self.generator.generate(query,document_str)
            pprint("RELOAD THE RIGHT SCROLL BOX, This is the list of text show up on the right scroll box")
            pprint(metadatas)
            pprint("This is the list of result (id,similarity score) which you will use id to get full document text")
            pprint(metadatas_score_points)
            print(response)

    async def process_query(self, query: str, query_sessions: dict, client_id: str):
        """
        Chat with retrieval system (stand-alone questions answering, 
        conversation not supported)

        Process a single query, interact with the retriever, generator, and 
        possibly internet search, and return a JSON-friendly dictionary of results.

        process_query function is the API endpoint version of the begin function
        """
        # get query_embedding and search images space
        result = {
            "texts": {
                "documents": [],
                "fragment_ids": []
            },
            "images": {
                "urls": [],
                "fragment_ids": []
            },
            # "metadatas": {
            #     "documents": [],
            #     "score_points": []
            # },
            "final_response": None,
            "search_phase": ""
        }
        # # Get query_embedding and search image space
        query_embedding = self.text_embed_model._get_embeddings_for_image_query(query)
        img_urls, image_score_points = self.retriever.search_image_space(query_embedding)

        result["images"]["urls"] = img_urls
        result["images"]["fragment_ids"] = [image_score_point.id for image_score_point in image_score_points]

        # Quantize query embedding
        query_embedding = binary_quantized(query_embedding)

        # Search text space
        texts, text_score_points = self.retriever.search_text_space(query_embedding)
        result["texts"]["documents"] = texts
        result["texts"]["fragment_ids"] = [text_score_point.id for text_score_point in text_score_points]

        # Attempt to generate an informative response from text results
        document_str = ""
        for i, text in enumerate(texts):
            document_str += f"Document {i}:\n{text}\n\n"
        response = self.generator.check_informative(user_query=query, documents_str=document_str)
        if response != 'False':
            result["final_response"] = response
            result["search_phase"] = "text_space"
            query_sessions[client_id] = QuerySession(QueryState.SUCCESS, result)
            return

        # # Search metadata space if text not informative enough
        metadatas, metadatas_score_points = self.retriever.search_metadata_space(query_embedding)
        # result["metadatas"]["documents"] = metadatas
        # result["metadatas"]["score_points_id"] = metadatas_score_points

        document_str = ""
        for i, metadata in enumerate(metadatas):
            document_str += f"Document {i}:\n{metadata}\n\n"
        response = self.generator.check_informative(user_query=query, documents_str=document_str)
        if response != 'False':
            result["final_response"] = response
            result["search_phase"] = "metadata_space"
            query_sessions[client_id] = QuerySession(QueryState.SUCCESS, result)
            return

        # If both text and metadata search fail, try internet search
        query_sessions[client_id] = QuerySession(QueryState.SEARCHING_INTERNET, result)
        await asyncio.sleep(0)  # Allow the consumer to process the query
        search_query = self.query_preprocessor.process_query_for_search(query)
        try:
            self.search_internet(search_query=search_query)
        except Exception:
            query_sessions[client_id] = QuerySession(QueryState.SUCCESS, result)
            return

        # Re-search text space after internet search
        texts, text_score_points = self.retriever.search_text_space(query_embedding)
        result["texts"]["documents"] = texts
        # Get ids from text_score_points
        result["texts"]["fragment_ids"] = [text_score_point.id for text_score_point in text_score_points]

        document_str = ""
        for i, text in enumerate(texts):
            document_str += f"Document {i}:\n{text}\n\n"
        response = self.generator.check_informative(user_query=query, documents_str=document_str)
        if response != 'False':
            result["final_response"] = response
            result["search_phase"] = "text_space_after_internet"
            query_sessions[client_id] = QuerySession(QueryState.SUCCESS, result)
            return

        # If still not informative, re-search metadata space after internet search
        metadatas, metadatas_score_points = self.retriever.search_metadata_space(query_embedding)
        # result["metadatas"]["documents"] = metadatas
        # result["metadatas"]["score_points"] = metadatas_score_points

        document_str = ""
        for i, metadata in enumerate(metadatas):
            document_str += f"Document {i}:\n{metadata}\n\n"
        response = self.generator.generate(query, document_str)
        # result["final_response"] = response
        # result["search_phase"] = "metadata_space_after_internet"
        # metadatas,metadatas_score_points = self.retriever.search_metadata_space(query_embedding)
        # # pprint("RELOAD THE RIGHT SCROLL BOX, This is the list of text show up on the right scroll box")
        # # pprint(metadatas)
        # # pprint("This is the list of result (id,similarity score) which you will use id to get full document text")
        # # pprint(metadatas_score_points)
        # document_str = ""
        # for i,metadata in enumerate(metadatas):
        #     document_str += f"Document {i}:\n{metadata}\n\n"
        # response = self.generator.generate(query,document_str)
        result["final_response"] = response
        query_sessions[client_id] = QuerySession(QueryState.SUCCESS, result)

    
    def search_internet(self,search_query:str,n_cnn:int=5,n_medium:int=5):
        """
        Function to crawl realtime posts on CNN and medium

        Results:
            - n posts on medium and cnn save to local json database
            - new vectors added to RAM in the current session
        """
        self.indexer.crawl_both(search_query, n_cnn, n_medium)

        contents = self.indexer.get_content_embeddings()

        metadatas = self.indexer.get_metadata_items_embeddings()

        images = self.indexer.get_images_items_embeddings()

        for item in contents:
            for id, value in item.items():
                self.retriever.add_point_to_text_space(id, base64_to_binary_array(value["embedding"]))

        for item in metadatas:
            for id, value in item.items():
                self.retriever.add_point_to_metadata_space(id, base64_to_binary_array(value))

        for item in images:
            for id, value in item.items():
                self.retriever.add_point_to_image_space(id, base64_to_float32_vector(value["embedding"]))

        self.indexer.clear_data()

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
    
    def get_all_text_from_fragment_id(self, point_id:str) -> str:
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
