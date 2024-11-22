from typing import Any, Callable, List, Optional, Sequence, TypedDict
from typing_extensions import Annotated

import numpy as np
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.bridge.pydantic import Field, SerializeAsAny, WithJsonSchema
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.node_parser import NodeParser
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.node_parser.node_utils import (
    build_nodes_from_splits,
    default_id_func,
)
from llama_index.core.schema import BaseNode, Document
from llama_index.core.utils import get_tqdm_iterable

DEFAULT_OG_TEXT_METADATA_KEY = "original_text"


class paragraphCombination(TypedDict):
    paragraph: str
    index: int
    combined_paragraph: str
    combined_paragraph_embedding: List[float]


ParagraphSplitterCallable = Annotated[
    Callable[[str], List[str]],
    WithJsonSchema({"type": "string"}, mode="serialization"),
    WithJsonSchema({"type": "string"}, mode="validation"),
]

def simple_paragraph_splitter() -> Callable[[str], List[str]]:
    return lambda text: text.split("\n")

class SemanticSplitterNodeParser(NodeParser):
    """Semantic node parser.

    Splits a document into Nodes, with each node being a group of semantically related paragraphs.

    Args:
        buffer_size (int): number of paragraphs to group together when evaluating semantic similarity
        embed_model: (BaseEmbedding): embedding model to use
        paragraph_splitter (Optional[Callable]): splits text into paragraphs
        include_metadata (bool): whether to include metadata in nodes
        include_prev_next_rel (bool): whether to include prev/next relationships
    """

    paragraph_splitter: ParagraphSplitterCallable = Field(
        default_factory=simple_paragraph_splitter,
        description="The text splitter to use when splitting documents.",
        exclude=True,
    )

    embed_model: SerializeAsAny[BaseEmbedding] = Field(
        description="The embedding model to use to for semantic comparison",
    )

    buffer_size: int = Field(
        default=1,
        description=(
            "The number of paragraphs to group together when evaluating semantic similarity. "
            "Set to 1 to consider each paragraph individually. "
            "Set to >1 to group paragraphs together."
        ),
    )

    breakpoint_percentile_threshold: int = Field(
        default=75,
        description=(
            "The percentile of cosine dissimilarity that must be exceeded between a "
            "group of paragraphs and the next to form a node.  The smaller this "
            "number is, the more nodes will be generated"
        ),
    )

    @classmethod
    def class_name(cls) -> str:
        return "SemanticSplitterNodeParser"

    @classmethod
    def from_defaults(
        cls,
        embed_model: Optional[BaseEmbedding] = None,
        breakpoint_percentile_threshold: Optional[int] = 75,
        buffer_size: Optional[int] = 1,
        paragraph_splitter: Optional[Callable[[str], List[str]]] = None,
        original_text_metadata_key: str = DEFAULT_OG_TEXT_METADATA_KEY,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        callback_manager: Optional[CallbackManager] = None,
        id_func: Optional[Callable[[int, Document], str]] = None,
    ) -> "SemanticSplitterNodeParser":
        callback_manager = callback_manager or CallbackManager([])

        paragraph_splitter = paragraph_splitter or simple_paragraph_splitter()
        if embed_model is None:
            try:
                from llama_index.embeddings.openai import (
                    OpenAIEmbedding,
                )  # pants: no-infer-dep

                embed_model = embed_model or OpenAIEmbedding()
            except ImportError:
                raise ImportError(
                    "`llama-index-embeddings-openai` package not found, "
                    "please run `pip install llama-index-embeddings-openai`"
                )

        id_func = id_func or default_id_func

        return cls(
            embed_model=embed_model,
            breakpoint_percentile_threshold=breakpoint_percentile_threshold,
            buffer_size=buffer_size,
            paragraph_splitter=paragraph_splitter,
            original_text_metadata_key=original_text_metadata_key,
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel,
            callback_manager=callback_manager,
            id_func=id_func,
        )

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[BaseNode]:
        """Parse document into nodes."""
        all_nodes: List[BaseNode] = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")

        for node in nodes_with_progress:
            nodes = self.build_semantic_nodes_from_documents([node], show_progress)
            all_nodes.extend(nodes)

        return all_nodes

    def build_semantic_nodes_from_documents(
        self,
        documents: Sequence[Document],
        show_progress: bool = False,
    ) -> List[BaseNode]:
        """Build window nodes from documents."""
        all_nodes: List[BaseNode] = []
        for doc in documents:
            text = doc.text
            text_splits = self.paragraph_splitter(text)

            paragraphs = self._build_paragraph_groups(text_splits)

            combined_paragraph_embeddings = self.embed_model.get_text_embedding_batch(
                [s["combined_paragraph"] for s in paragraphs],
                show_progress=show_progress,
            )

            for i, embedding in enumerate(combined_paragraph_embeddings):
                paragraphs[i]["combined_paragraph_embedding"] = embedding

            distances = self._calculate_distances_between_paragraph_groups(paragraphs)

            chunks = self._build_node_chunks(paragraphs, distances)

            nodes = build_nodes_from_splits(
                chunks,
                doc,
                id_func=self.id_func,
            )

            all_nodes.extend(nodes)

        return all_nodes

    def _build_paragraph_groups(
        self, text_splits: List[str]
    ) -> List[paragraphCombination]:
        paragraphs: List[paragraphCombination] = [
            {
                "paragraph": x,
                "index": i,
                "combined_paragraph": "",
                "combined_paragraph_embedding": [],
            }
            for i, x in enumerate(text_splits)
        ]

        # Group paragraphs and calculate embeddings for paragraph groups
        for i in range(len(paragraphs)):
            combined_paragraph = ""

            for j in range(i - self.buffer_size, i):
                if j >= 0:
                    combined_paragraph += paragraphs[j]["paragraph"]

            combined_paragraph += paragraphs[i]["paragraph"]

            for j in range(i + 1, i + 1 + self.buffer_size):
                if j < len(paragraphs):
                    combined_paragraph += paragraphs[j]["paragraph"]

            paragraphs[i]["combined_paragraph"] = combined_paragraph

        return paragraphs

    def _calculate_distances_between_paragraph_groups(
        self, paragraphs: List[paragraphCombination]
    ) -> List[float]:
        distances = []
        for i in range(len(paragraphs) - 1):
            embedding_current = paragraphs[i]["combined_paragraph_embedding"]
            embedding_next = paragraphs[i + 1]["combined_paragraph_embedding"]

            similarity = self.embed_model.similarity(embedding_current, embedding_next)

            distance = 1 - similarity

            distances.append(distance)

        return distances

    def _build_node_chunks(
        self, paragraphs: List[paragraphCombination], distances: List[float]
    ) -> List[str]:
        chunks = []
        if len(distances) > 0:
            breakpoint_distance_threshold = np.percentile(
                distances, self.breakpoint_percentile_threshold
            )

            indices_above_threshold = [
                i for i, x in enumerate(distances) if x > breakpoint_distance_threshold
            ]

            # Chunk paragraphs into semantic groups based on percentile breakpoints
            start_index = 0

            for index in indices_above_threshold:
                group = paragraphs[start_index : index + 1]
                combined_text = "".join([d["paragraph"] for d in group])
                chunks.append(combined_text)

                start_index = index + 1

            if start_index < len(paragraphs):
                combined_text = "".join(
                    [d["paragraph"] for d in paragraphs[start_index:]]
                )
                chunks.append(combined_text)
        else:
            # If, for some reason we didn't get any distances (i.e. very, very small documents) just
            # treat the whole document as a single node
            chunks = [" ".join([s["paragraph"] for s in paragraphs])]

        return chunks
