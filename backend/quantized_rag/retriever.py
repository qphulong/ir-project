from ..nomic_embed import NomicEmbed, NomicEmbedQuantized
from typing import List,Tuple
from llama_index.core.schema import Document as LLamaDocument
from llama_index.core.schema import TextNode
import json
import os
from ..semantice_chunker import SemanticChunker
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core import load_index_from_storage
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import VectorStoreQuery, VectorStoreQueryResult
from qdrant_client.local.qdrant_local import QdrantLocal
from qdrant_client import QdrantClient, models


class Retriever():
    """
    Retriever class.

    Attributes:
        resource_path (str): Path to resource (database + index)
        embed_model_path (str): The path to the local embedding model.
        embed_model (NomicEmbedQuantized): The embedding model used for vectorizing the data.
    """
    def __init__(
        self,
        resource_path:str,
        embed_model_path:str,
    ):
        self.database_path = os.path.join(resource_path, 'database')
        self.index_path = os.path.join(resource_path, 'index')
        self.embed_model_path = embed_model_path
        self.embed_model = NomicEmbedQuantized(model_path=embed_model_path)
        self.qdrant_local = QdrantLocal(location=":memory:")
        
    def _setup(self):
        collection_name = ''
        quantization_config=models.BinaryQuantization(
        binary=models.BinaryQuantizationConfig(
            always_ram=True  # Keep binary embeddings in RAM for fast access
        )
)
        self.qdrant_local.create_collection()

    def _init_vector_store_index(self,nodes):
        """Init self.vector_store_index"""
        if nodes is not []:
            self.vector_store_index = VectorStoreIndex(
                embed_model=self.embed_model,
                nodes=nodes
            )
        else:
            print("Cannot init VectorStoreIndex with empty List[TextNode]")

    def persist_to_disk(self):
        """Persist the vector store to disk"""
        self.vector_store_index.storage_context.persist(persist_dir=self.index_path)

    def load_from_disk(self):
        """Load the vector store from disk to RAM"""
        storage_context = StorageContext.from_defaults(persist_dir=self.index_path)
        self.vector_store_index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=self.embed_model,
        )

    def _load_documents(self)->List[LLamaDocument]:
        """Load raw json in 'database' directory, each json is now return as 
        a LlamaDocument object, result in a list of LlamaDocument.

        Returns:
            - documents (List[LlamaDocument]): list of documents
        """
        documents = []  
        if os.path.isdir(self.database_path):
            for filename in os.listdir(self.database_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.database_path, filename)
                    with open(file_path, 'r',encoding='utf-8') as file:
                        data = json.load(file)
                        # extra_info = {}
                        # extra_info['author_profile'] = data['author_profile']
                        document = LLamaDocument(
                            text=data['content'],
                            # metadata=extra_info
                        )
                        documents.append(document)
        else:
            print(f"Invalid path: {self.database_path}. Please provide a directory or JSON file.")
        return documents
    
    def _chunk_documents(self,documents:List[LLamaDocument]) -> List[TextNode]:
        """Chunk a list of LlamaDocument to a list of TextNode with Semantic chunking method"""
        semantic_chunker = SemanticChunker(
            breakpoint_percentile_threshold=60,
            include_metadata=False
        )
        nodes = semantic_chunker.chunk_nodes_from_documents(documents=documents)
        return nodes

    def _generate_embeddings(self,nodes:List[TextNode]):
        """Generate embeddings

        Args:
            - nodes (List[TextNode]): a list of TextNode

        Return
            - The same List[TextNode] but with embeddings
        """
        for i,node in enumerate(nodes):
            print(f"embedding {i}th node")
            embedding = self.embed_model._get_text_embedding(node.text)
            node.embedding = embedding
        return nodes
    
    def retrieve(self, query: str, top_k: int = 8) -> VectorStoreQueryResult:
        """Retrieve top k similar nodes.
        Args:
            - query (str): User query
            - top_k: get top k nodes

        Returns:
            - results (VectorStoreQueryResult): the results :)
            yes, this document is shit, but VectorStoreQueryResult source code explain better than i do
        """
        query_embedding = self.embed_model.get_query_embedding(query)
        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding, similarity_top_k=top_k, mode='default'
        )
        results = self.vector_store_index.vector_store.query(vector_store_query)
        return results
    
    def get_node_by_id(self,id:str)->TextNode:
        """
        Get the node by using it id
        Args:
            - id (str): id

        Returns:
            - TextNode: TextNode with same id.
        """
        return self.vector_store_index.docstore.get_node(id)