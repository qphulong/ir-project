import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from llama_index.core import Document as LlamaIndexDocument
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingMode, OpenAIEmbeddingModelType
from typing import List
from llama_index.core.schema import TextNode

class SemanticChunker():
    """
    Class for chunking documents into semantic text nodes using LlamaIndex's
    SemanticSplitterNodeParser. The chunking process is based on semantic 
    similarity.

    WARNING: Although include_metadata is boolean, it is not recommend to chunk
    documents with metadata

    Attributes:
        embed_model (OpenAIEmbedding): The model used for semantic embedding.
        semantic_chunker (SemanticSplitterNodeParser): The LlamaIndex semantic chunker.

    Methods:
        chunk_nodes_from_documents(documents: List[LLamaIndexDocument]) -> List[TextNode]:
            Chunks a list of LLamaIndexDocuments into a list of TextNodes.
    """
    def __init__(
            self,
            mode: OpenAIEmbeddingMode = OpenAIEmbeddingMode.SIMILARITY_MODE,
            model: OpenAIEmbeddingModelType = OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL,
            buffer_size: int = 1,
            breakpoint_percentile_threshold: int = 95,
            include_metadata: bool = True
        ) -> None:
        """
        Initialize the SemanticChunker.

        Args:
            mode (OpenAIEmbeddingMode): The embedding mode to use.
            model (OpenAIEmbeddingModelType): The OpenAI model to use for embeddings.
            buffer_size (int): The number of sentences to group together when evaluating 
                                semantic similarity.
            breakpoint_percentile_threshold (int): The percentile of cosine dissimilarity 
                                                    that must be exceeded between a group 
                                                    of sentences and the next to form a node. 
                                                    The smaller this number is, the more nodes 
                                                    will be generated.
            include_metadata (bool): Whether to include metadata in the chunking process.
        """
        self.embed_model = OpenAIEmbedding(
            mode=mode,
            model=model
        )
        self.semantic_chunker = SemanticSplitterNodeParser(
            buffer_size=buffer_size,
            breakpoint_percentile_threshold=breakpoint_percentile_threshold,
            embed_model=self.embed_model,
            include_metadata=include_metadata,
        )

    def chunk_nodes_from_documents(self, documents: List[LlamaIndexDocument]) -> List[TextNode]:
        """
        Chunk list of LLamaIndexDocuments into text nodes by applying semantic chunking method

        Args:
            documents (List[LLamaIndexDocument]): The list of documents to chunk.

        Returns:
            List[TextNode]: A list of TextNodes created from the provided documents.
        """
        nodes:List[TextNode] = self.semantic_chunker.get_nodes_from_documents(documents=documents)
        return nodes