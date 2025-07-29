from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field,root_validator

from cyborgdb_service.api.schemas.index import IndexOperationRequest

# ============================
# Vector Item Models
# ============================

class VectorItem(BaseModel):
    """
    Represents a vectorized item for storage in the encrypted index.

    Attributes:
        id (str): Unique identifier for the vector item.
        vector (Optional[List[float]]): The vector representation of the item.
        contents (Optional[Union[str, bytes]]): The original text or associated content (can be string or bytes).
        metadata (Optional[Dict[str, Any]]): Additional metadata associated with the item.
    """
    id: str
    vector: Optional[List[float]] = None
    contents: Optional[Union[str, bytes]] = None
    metadata: Optional[Dict[str, Any]] = None


class UpsertRequest(IndexOperationRequest):
    """
    Request model for adding or updating vectors in an encrypted index.

    Inherits:
        IndexOperationRequest: Includes `index_name` and `index_key`.

    Attributes:
        items (List[VectorItem]): List of vector items to be inserted or updated.
    """
    items: List[VectorItem]


# ============================
# Query Models
# ============================
class QueryRequest(IndexOperationRequest):
    """
    Request model for performing a similarity search in the encrypted index.

    Inherits:
        IndexOperationRequest: Includes `index_name` and `index_key`.

    Attributes:
        query_vectors (Optional[List[float]]): The vector used for the similarity search.
        query_contents (Optional[str]): Text-based content used for semantic search.
        top_k (int): Number of nearest neighbors to return for each query. Defaults to 100.
        n_probes (int): Number of lists to probe during the query. Defaults to 1.
        greedy (bool): Whether to use greedy search. Defaults to False.
        filters (Optional[Dict[str, Any]]): JSON-like dictionary specifying metadata filters. Defaults to {}.
        include (List[str]): List of additional fields to include in the response. Defaults to `["distance", "metadata"]`.
    """
    query_vectors: Optional[List[float]] = None
    query_contents: Optional[str] = None
    top_k: int = 100
    n_probes: int = 1
    greedy: bool = False
    filters: Optional[Dict[str, Any]] = {}
    include: List[str] = ["distance", "metadata"]


class BatchQueryRequest(IndexOperationRequest):
    """
    Request model for batch similarity search.

    Inherits:
        IndexOperationRequest: Includes `index_name` and `index_key`.

    Attributes:
        query_vectors (List[List[float]]): List of vectors to search for in batch mode.
        top_k (int): Number of nearest neighbors to return for each query. Defaults to 100.
        n_probes (int): Number of lists to probe during the query. Defaults to 1.
        greedy (bool): Whether to use greedy search. Defaults to False.
        filters (Optional[Dict[str, Any]]): JSON-like dictionary specifying metadata filters. Defaults to {}.
        include (List[str]): List of additional fields to include in the response. Defaults to `["distance", "metadata"]`.
    """
    query_vectors: List[List[float]]
    top_k: int = 100
    n_probes: int = 1
    greedy: bool = False
    filters: Optional[Dict[str, Any]] = {}
    include: List[str] = ["distance", "metadata"]



# ============================
# Get & Delete Models
# ============================

class GetRequest(IndexOperationRequest):
    """
    Request model for retrieving specific vectors from the index.

    Inherits:
        IndexOperationRequest: Includes `index_name` and `index_key`.

    Attributes:
        ids (List[str]): List of vector item IDs to retrieve.
        include (List[str]): List of fields to include in the response. 
            Defaults to `["vector", "contents", "metadata"]`.
    """
    ids: List[str]
    include: List[str] = ["vector", "contents", "metadata"]

class GetResultItemModel(BaseModel):
    """
    Represents an individual item retrieved from the encrypted index.

    Attributes:
        id (str): The unique identifier of the item.
        metadata (Optional[Dict[str, Any]]): Additional metadata associated with the item.
        contents (Optional[bytes]): The raw byte contents of the item.
        vector (Optional[List[float]]): The vector representation of the item.
    """
    id: str
    metadata: Optional[Dict[str, Any]] = None
    contents: Optional[bytes] = None
    vector: Optional[List[float]] = None


class GetResponseModel(BaseModel):
    """
    Response model for retrieving multiple encrypted index items.

    Attributes:
        results (List[GetResultItem]): A list of retrieved items with requested fields.
    """
    results: List[GetResultItemModel]

class DeleteRequest(IndexOperationRequest):
    """
    Request model for deleting vectors from the encrypted index.

    Inherits:
        IndexOperationRequest: Includes `index_name` and `index_key`.

    Attributes:
        ids (List[str]): List of vector item IDs to be deleted.
    """
    ids: List[str]


# ============================
# Query Response Models
# ============================

class QueryResultItem(BaseModel):
    """
    Represents a single result from a similarity search.

    Attributes:
        id (str): The identifier of the retrieved item.
        distance (Optional[float]): Distance from the query vector (smaller = more similar).
        metadata (Optional[Dict[str, Any]]): Additional metadata for the result.
        vector (Optional[List[float]]): The retrieved vector (if included in response).
    """
    id: str
    distance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    vector: Optional[List[float]] = None


class QueryResponse(BaseModel):
    """
    Response model for similarity search queries.

    Attributes:
        results (List[QueryResultItem]): List of search results.
    """
    results: Union[List[QueryResultItem], List[List[QueryResultItem]]]
    @root_validator(pre=True)
    def normalize_results(cls, values):
        results = values.get("results")
        if not results:
            return values

        if isinstance(results, list):
            # Check if flat list (all items are QueryResultItem-like)
            if all(isinstance(item, dict) or isinstance(item, QueryResultItem) for item in results):
                return values
            # Check if nested list
            if all(isinstance(group, list) for group in results):
                return values

        raise ValueError("`results` must be a list of QueryResultItem or list of lists of QueryResultItem.")

# ============================
# Standard Response Model
# ============================

class SuccessResponseModel(BaseModel):
    """
    Standard success response model for operations like upsert and delete.

    Attributes:
        status (str): Operation status. Defaults to `"success"`.
        message (str): Descriptive success message.
    """
    status: str = "success"
    message: str

class ErrorResponseModel(BaseModel):
    """
    Standard error response model.

    Attributes:
        status_code (int): HTTP status code of the error.
        detail (str): A detailed message describing the error.
    """
    status_code: int
    detail: str



# ============================
# API Response Dictionary
# ============================
ErrorResponses: Dict[int, Dict] = {
    401: {"description": "Permission denied from license issue", "model": ErrorResponseModel},
    500: {"description": "Unexpected server error", "model": ErrorResponseModel},
}

UpsertResponses: Dict[int, Dict] = {
    **ErrorResponses,
    200: {"description": "Successful response", "model": SuccessResponseModel},
}
QueryResponses: Dict[int, Dict] = {
    **ErrorResponses,
    200: {"description": "Successful response", "model": QueryResponse},
}
GetResponses: Dict[int, Dict] = {
    **ErrorResponses,
    200: {"description": "Successful response", "model": GetResponseModel},
}
DeleteResponses: Dict[int, Dict] = {
    **ErrorResponses,
    200: {"description": "Successful response", "model": SuccessResponseModel},
    401: {"description": "Unable to find item to delete", "model": ErrorResponseModel},
}

NumVectorsResponses: Dict[int, Dict] = {
    **ErrorResponses,
    200: {"description": "Successful response", "model": SuccessResponseModel},
}