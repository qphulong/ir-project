from pypdf import PdfReader
from docx import Document
from base64 import b64encode, b64decode
from semantice_chunker import SemanticChunker
from llama_index.core.schema import Document as LlamaIndexDocument
from llama_index.core.schema import TextNode
from typing import List
from nomic_embed import NomicEmbed
from numpy import ndarray
import json
from datetime import datetime

def datetime_to_str(dt: datetime) -> str:
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

class D2D():
    """Class for converting documents to json form and then save it to disk in base64 format. And load back the base64 as json.

    Methods:
        _convert_pdf_to_json: Converts pdf file to json form.
        _convert_docx_to_json: Converts docx file to json form.
        convert_to_json: Converts file to json form.
        save_to_disk: Saves json data to disk.
        load_from_disk: Loads json data from disk.
    """
    
    def __init__(self):
        self.chunker = SemanticChunker()
        self.text_embedder = NomicEmbed()

    def __chunk_nodes_from_document(self, document: LlamaIndexDocument) -> List[TextNode]:
        """Chunks a document into a list of TextNodes.
        """
        nodes = self.chunker.chunk_nodes_from_documents([document])
        return nodes


    def _convert_pdf_to_json(self, file_path:str):
        """Converts pdf file to json form.
        """
        pdf = PdfReader(file_path)
        metadata = pdf.metadata
        metadata = {
            'title': metadata.title,
            'author': metadata.author,
            'creator': metadata.creator,
            'creation_date': datetime_to_str(metadata.creation_date),
            'modification_date': datetime_to_str(metadata.modification_date),
            'producer': metadata.producer,
            'subject': metadata.subject,
        }
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        text = self.__chunk_nodes_from_document(LlamaIndexDocument(text=text))
        text_embed: list[ndarray] = []
        for chunk in text:
            text_embed.append(self.text_embedder._get_text_embedding(chunk.text))
        
        id = 'user_' + str(hash(file_path))
        pdf_json = {
            'id': id,
            'metadata': metadata,
            'content': {
                f'{id}_text_{i}': {
                    'content': text[i].text,
                    'embedding': text_embed[i].tolist()
                    }
                for i in range(len(text))
            },
            'images': {
            }
        }
        pdf_json = json.dumps(pdf_json)
        return pdf_json
    
    def _convert_docx_to_json(self, file_path:str):
        """Converts docx file to json form.
        """
        doc = Document(file_path)
        metadata = doc.core_properties
        metadata = {
            'title': metadata.title,
            'author': metadata.author,
            'category': metadata.category,
            'subject': metadata.subject,
            'comments': metadata.comments,
            'content_status': metadata.content_status,
            'created': datetime_to_str(metadata.created),
            'modified': datetime_to_str(metadata.modified),
            'last_modified_by': metadata.last_modified_by,
            'revision': metadata.revision,
        }
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'

        text = self.__chunk_nodes_from_document(LlamaIndexDocument(text=text))
        text_embed: list[ndarray] = []
        for chunk in text:
            text_embed.append(self.text_embedder._get_text_embedding(chunk.text))

        id = 'user_' + str(hash(file_path))
        doc_json = {
            'id': id,
            'metadata': metadata,
            'content': {
                f'{id}_text_{i}': {
                    'content': text[i].text,
                    'embedding': text_embed[i].tolist()
                    }
                for i in range(len(text))
            },
            'images': {
            }
        }
        doc_json = json.dumps(doc_json)
        return doc_json
    
    def convert_to_json(self, file_path:str) -> str | None:
        """Converts file to json form.
        """
        if file_path.endswith('.pdf'):
            return self._convert_pdf_to_json(file_path)
        elif file_path.endswith('.docx'):
            return self._convert_docx_to_json(file_path)
        else:
            print('Error: Unsupported file format.')
            return None
        
    def save_to_disk(self, file_path:str, json_data:str) -> None:
        """Saves json data to disk.
        """
        json_data = b64encode(json_data.encode())
        with open(file_path, 'wb') as f:
            f.write(json_data)

    def load_from_disk(self, file_path:str) -> str | None:
        """Loads json data from disk.
        """
        try:
            with open(file_path, 'rb') as f:
                json_data = f.read()
            return b64decode(json_data).decode()
        except Exception as e:
            print(f'Error: {e}')
            return None