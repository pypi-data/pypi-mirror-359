"""Type definitions for the Jaqpot Python SDK."""

from typing import List, Any, Optional, TypedDict, Union, Dict


class ModelSummary(TypedDict, total=False):
    """Summary representation of a Jaqpot model.
    
    Attributes:
        name: The name of the model
        modelId: The unique identifier of the model
        description: A description of what the model does
        type: The type/category of the model
        independentFeatures: List of input features the model expects
        dependentFeatures: List of output features the model produces
    """
    name: Optional[str]
    modelId: Optional[int]
    description: Optional[str]
    type: Optional[Any]
    independentFeatures: Optional[List[Any]]
    dependentFeatures: Optional[List[Any]]


class SearchResult(TypedDict, total=False):
    """Result from model search operations.
    
    Attributes:
        content: List of models matching the search query
        totalElements: Total number of matching models
        totalPages: Total number of pages
        pageSize: Number of models per page
        pageNumber: Current page number
    """
    content: Optional[List[Dict[str, Any]]]
    totalElements: Optional[int]
    totalPages: Optional[int]
    pageSize: Optional[int]
    pageNumber: Optional[int]


class PredictionResult(TypedDict, total=False):
    """Result from prediction operations.
    
    Attributes:
        predictions: The prediction results
        status: Status of the prediction
        message: Any message associated with the prediction
    """
    predictions: Optional[List[Dict[str, Any]]]
    status: Optional[str]
    message: Optional[str]