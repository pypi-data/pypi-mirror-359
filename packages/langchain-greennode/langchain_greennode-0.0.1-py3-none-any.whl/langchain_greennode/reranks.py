

from copy import deepcopy
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)
import yaml
import warnings
import greennode

from pydantic import (
    ConfigDict,
    Field,
    SecretStr,
    model_validator,
)
from typing_extensions import Self

from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
from langchain_core.utils import from_env, get_pydantic_field_names, secret_from_env


class GreenNodeRerank(BaseDocumentCompressor):
    """Document compressor that uses `GreenNode Rerank API`."""

    client: Any = Field(default=None, exclude=True) 
    """GreenNode client to use for compressing documents."""
    top_n: Optional[int] = 3
    """Number of documents to return."""
    model: str = "BAAI/bge-reranker-v2-m3"
    """Reranking model name to use.
    Instead, use 'BAAI/bge-reranker-v2-m3' for example.
    """
    greennode_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("GREENNODE_API_KEY", default=None),
    )
    """GreenNode API key.

    Automatically read from env variable `GREENNODE_API_KEY` if not provided.
    """
    greennode_api_base: str = Field(
        default_factory=from_env(
            "GREENNODE_API_BASE", default="https://maas.api.greennode.ai/v1/"
        ),
        alias="base_url",
    )
    """Endpoint URL to use."""
    
    max_retries: int = 2
    """Maximum number of retries to make when generating."""
    request_timeout: Optional[Union[float, Tuple[float, float], Any]] = Field(
        default=None, alias="timeout"
    )
    """Timeout for requests to GreenNode embedding API. Can be float, httpx.Timeout or
        None."""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Holds any model parameters valid for `create` call not explicitly specified."""
    skip_empty: bool = False
    """Whether to skip empty strings when embedding or raise an error.
    Defaults to not skipping.

    Not yet supported."""
    default_headers: Union[Mapping[str, str], None] = None

    http_client: Union[Any, None] = None
    """Optional httpx.Client. Only used for sync invocations. Must specify
        http_async_client as well if you'd like a custom client for async invocations.
    """
    http_async_client: Union[Any, None] = None
    """Optional httpx.AsyncClient. Only used for async invocations. Must specify
        http_client as well if you'd like a custom client for sync invocations."""


    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: Dict[str, Any]) -> Any:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name in extra:
                raise ValueError(f"Found {field_name} supplied twice.")
            if field_name not in all_required_field_names:
                warnings.warn(
                    f"""WARNING! {field_name} is not default parameter.
                    {field_name} was transferred to model_kwargs.
                    Please confirm that {field_name} is what you intended."""
                )
                extra[field_name] = values.pop(field_name)

        invalid_model_kwargs = all_required_field_names.intersection(extra.keys())
        if invalid_model_kwargs:
            raise ValueError(
                f"Parameters {invalid_model_kwargs} should be specified explicitly. "
                f"Instead they were passed in as part of `model_kwargs` parameter."
            )

        values["model_kwargs"] = extra
        return values
    
    @model_validator(mode="after")
    def post_init(self) -> Self:
        """Logic that will post Pydantic initialization."""
        if self.top_n is not None and self.top_n == 0:
            raise ValueError("Top n cannot 0")
        client_params: dict = {
            "api_key": (
                self.greennode_api_key.get_secret_value()
                if self.greennode_api_key
                else None
            ),
            "base_url": self.greennode_api_base,
            "timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "supplied_headers": self.default_headers
        }
        if not (self.client or None):
            sync_specific: dict = (
                {"http_client": self.http_client} if self.http_client else {}
            )
            self.client = greennode.GreenNode(**client_params, **sync_specific).reranks
        return self
    
    @property
    def _invocation_params(self) -> Dict[str, Any]:
        params: Dict = {"model": self.model, "top_n": self.top_n, **self.model_kwargs}
        return params
    
    def _document_to_str(
        self,
        document: Union[str, Document, dict],
        rank_fields: Optional[Sequence[str]] = None,
    ) -> str:
        if isinstance(document, Document):
            return document.page_content
        elif isinstance(document, dict):
            filtered_dict = document
            if rank_fields:
                filtered_dict = {}
                for key in rank_fields:
                    if key in document:
                        filtered_dict[key] = document[key]

            return yaml.dump(filtered_dict, sort_keys=False)
        else:
            return document

    def rerank(
            self,
            documents: Sequence[Union[str, Document, dict]],
            query: str,
            top_n: Optional[int] = -1,
            rank_fields: Optional[Sequence[str]] = None,
    ):
        if len(documents) == 0:  # to avoid empty api call
            return []
        docs = [self._document_to_str(doc, rank_fields) for doc in documents]
        params = self._invocation_params
        if top_n is None or top_n > 0:
            params["top_n"] = top_n

        results = self.client.create(
            query=query,
            documents=docs,
            **params
        )
        result_dicts = []
        for res in results.results:
            result_dicts.append(
                {"index": res["index"], "relevance_score": res["relevance_score"]}
            )
        return result_dicts

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Compress documents using GreenNode's rerank API.

        Args:
            documents: A sequence of documents to compress.
            query: The query to use for compressing the documents.
            callbacks: Callbacks to run during the compression process.

        Returns:
            A sequence of compressed documents.
        """
        compressed = []
        for res in self.rerank(documents, query):
            doc = documents[res["index"]]
            doc_copy = Document(doc.page_content, metadata=deepcopy(doc.metadata))
            doc_copy.metadata["relevance_score"] = res["relevance_score"]
            compressed.append(doc_copy)
        return compressed
        
    

