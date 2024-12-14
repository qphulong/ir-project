from .binary_quantized_rag.retriever import Retriever
from .naive_rag import Generator
from .nomic_embed import NomicEmbed
from .nomic_embed_vision import NomicEmbedVision
from .D2D import D2D
from .utils import *
from pprint import pprint
from memory_profiler import profile
from numpy import ndarray
from PIL.ImageFile import ImageFile

class Application():
    """
    Application Class

    Attributes:
        retriever (Retriever): Responsible for data retrieval operation
        indexer (Indexer): Index raw data to database
        generator (Generator): Open AI LLM
        text_embed_model (NomicEmbed): generate embeddings for retrieval tasks
        image_embed_model (NomicEmbedVision): generate embeddings for retrieval tasks
        documents_loader (D2D): convert documents to json form and then save it to disk in base64 format. And load back the base64 as json.
    """
    def __init__(self):
        self.retriever = Retriever()
        self.indexer = None #TODO implement class Indexer
        self.generator = Generator()
        self.text_embed_model = NomicEmbed()
        self.image_embed_model = NomicEmbedVision()
        self.documents_loader = D2D()

    def _load_doc(self, path: str) -> str:
        """Load document file (docx, pdf) to ram (json)
        Args:
            path str: file path
        Returns:
            str: data in json format
        """
        data = self.documents_loader.convert_to_json(path)
        if data is None:
            raise ValueError(f"Cannot load data from {path}")
        return data

    def _load_data(self, path: str) -> str:
        """Load data from disk (base64) to ram (json)
        Args:
            path str: file path
        Returns:
            str: data in json format
        """
        data = self.documents_loader.load_from_disk(path)
        if data is None:
            raise ValueError(f"Cannot load data from {path}")
        return data
    
    def _save_data(self, path: str, data: str) -> None:
        """Save data from ram (json) to disk (base64)
        Args:
            path str: file path
            data str: json data
        Returns:
            str: data in json format
        """
        self.documents_loader.save_to_disk(path, data)

    def _url_embed(self, url: str) -> ndarray:
        """Embed image from url
        Args:
            url str: the url of the image
        Returns:
            ndarray: the image embedding
        """
        return self.image_embed_model.embed_image(url)
    
    def _img_embed(self, img: ImageFile) -> ndarray:
        """Embed image from url
        Args:
            img PIL ImageFile: the image in PIL ImageFile class
        Returns:
            ndarray: the image embedding
        """
        return self.image_embed_model.embed_PIL_image(img)

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
