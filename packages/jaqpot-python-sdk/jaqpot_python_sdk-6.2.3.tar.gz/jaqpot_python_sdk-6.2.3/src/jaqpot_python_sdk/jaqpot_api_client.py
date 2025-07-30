import polling2
import os

from .patches.patched_dataset import PatchedDataset as Dataset
from .types import ModelSummary, SearchResult, PredictionResult
from typing import Optional, Union, List, Dict, Any
from jaqpot_api_client import Model
from jaqpot_api_client import (
    ModelApi,
    DatasetApi,
    DatasetType,
    DatasetCSV,
)
from .exceptions.exceptions import (
    JaqpotApiException,
    JaqpotPredictionTimeoutException,
    JaqpotPredictionFailureException,
)

from .helpers.b64encoding import file_to_b64encoding
from .helpers.logging import init_logger
from .helpers.url_utils import add_subdomain
from .jaqpot_api_client_builder import JaqpotApiHttpClientBuilder

QSARTOOLBOX_CALCULATOR_MODEL_ID = 6
QSARTOOLBOX_MODEL_MODEL_ID = 1837
QSAR_PROFILER_MODEL_ID = 1842


class JaqpotApiClient:
    """Client for interacting with the Jaqpot API.

    This client provides methods to interact with various endpoints of the Jaqpot API,
    including retrieving models and datasets, and making synchronous and asynchronous predictions.

    Attributes
    ----------
    base_url : str
        The base URL for the Jaqpot API.
    api_url : str
        The API URL for the Jaqpot API.
    http_client : object
        The HTTP client used to make requests to the Jaqpot API.
    log : object
        The logger object for logging messages.
    """

    def __init__(self, base_url: Optional[str] = None, api_url: Optional[str] = None, create_logs: bool = False, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> None:
        """Initialize the JaqpotApiClient.

        Parameters
        ----------
        base_url : str, optional
            The base URL for the Jaqpot API. Defaults to "https://jaqpot.org".
        api_url : str, optional
            The API URL for the Jaqpot API. If not provided, it is constructed using the base URL.
        create_logs : bool, optional
            Whether to create logs. Defaults to False.
        """
        # logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        self.log = init_logger(
            __name__, testing_mode=False, output_log_file=create_logs
        )
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = "https://jaqpot.org"
        self.api_url = api_url or add_subdomain(self.base_url, "api")
        jaqpot_api_key = api_key or os.getenv("JAQPOT_API_KEY")
        jaqpot_api_secret = api_secret or os.getenv("JAQPOT_API_SECRET")
        self.http_client = (
            JaqpotApiHttpClientBuilder(host=self.api_url)
            .build_with_api_keys(jaqpot_api_key, jaqpot_api_secret)
            .build()
        )

    def get_model_by_id(self, model_id: int) -> Model:
        """Get a model from Jaqpot by its ID.

        Parameters
        ----------
        model_id : int
            The ID of the model on Jaqpot.

        Returns
        -------
        Model
            The model object retrieved from Jaqpot.

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        """
        model_api = ModelApi(self.http_client)
        response = model_api.get_model_by_id_with_http_info(id=model_id)
        if response.status_code < 300:
            return response.data
        raise JaqpotApiException(
            message=response.data.to_dict().get('message', 'Unknown error'),
            status_code=response.status_code,
        )

    def get_model_summary(self, model_id: int) -> ModelSummary:
        """Get a summary of a model from Jaqpot by its ID.

        Parameters
        ----------
        model_id : int
            The ID of the model on Jaqpot.

        Returns
        -------
        ModelSummary
            A typed dictionary containing the model summary with standardized fields.

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        """
        model = self.get_model_by_id(model_id)
        model_summary = {
            "name": model.name,
            "modelId": model.id,
            "description": model.description,
            "type": model.type,
            "independentFeatures": model.independent_features,
            "dependentFeatures": model.dependent_features,
        }
        return model_summary

    def get_shared_models(self, page: Optional[int] = None, size: Optional[int] = None, sort: Optional[str] = None, organization_id: Optional[int] = None) -> Any:
        """Get shared models from Jaqpot.

        Parameters
        ----------
        page : int, optional
            Page number for pagination.
        size : int, optional
            Number of models per page.
        sort : str, optional
            Sort order for models.
        organization_id : int, optional
            Organization ID to filter models.

        Returns
        -------
        list
            A list of shared models.

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        """
        model_api = ModelApi(self.http_client)
        response = model_api.get_shared_models_with_http_info(
            page=page, size=size, sort=sort, organization_id=organization_id
        )
        if response.status_code < 300:
            return response.data
        raise JaqpotApiException(
            message=response.data.to_dict().get('message', 'Unknown error'),
            status_code=response.status_code,
        )

    def search_models(self, query: str, page: Optional[int] = None, size: Optional[int] = None) -> SearchResult:
        """Search for models on Jaqpot based on keywords.

        Parameters
        ----------
        query : str
            The search query string to find models by keywords.
        page : int, optional
            Page number for pagination. Defaults to 0.
        size : int, optional
            Number of models per page. Defaults to 20.

        Returns
        -------
        dict
            A dictionary containing search results with pagination info:
            - content: List of model summaries matching the search query
            - totalElements: Total number of matching models
            - totalPages: Total number of pages
            - pageSize: Number of models per page
            - pageNumber: Current page number

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        """
        model_api = ModelApi(self.http_client)
        response = model_api.search_models_with_http_info(
            query=query, page=page, size=size
        )
        if response.status_code < 300:
            return response.data.to_dict()
        raise JaqpotApiException(
            message=response.data.to_dict().get('message', 'Unknown error'),
            status_code=response.status_code,
        )

    def get_dataset_by_id(self, dataset_id: int) -> Dataset:
        """Get a dataset from Jaqpot by its ID.

        Parameters
        ----------
        dataset_id : int
            The ID of the dataset on Jaqpot.

        Returns
        -------
        Dataset
            The dataset object retrieved from Jaqpot.

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        """
        dataset_api = DatasetApi(self.http_client)
        response = dataset_api.get_dataset_by_id_with_http_info(id=dataset_id)
        if response.status_code < 300:
            return response.data
        raise JaqpotApiException(
            message=response.data.to_dict().get('message', 'Unknown error'),
            status_code=response.status_code,
        )

    def predict_sync(self, model_id: int, dataset: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Any:
        """Make a synchronous prediction with a model on Jaqpot.

        Parameters
        ----------
        model_id : int
            The ID of the model on Jaqpot.
        dataset : list or dict
            The dataset to predict.

        Returns
        -------
        dict
            The prediction result.

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        JaqpotPredictionFailureException
            If the prediction fails, an exception is raised with the failure reason.
        """
        dataset = Dataset(
            type=DatasetType.PREDICTION,
            entry_type="ARRAY",
            input=dataset,
        )

        model_api = ModelApi(self.http_client)
        response = model_api.predict_with_model_with_http_info(
            model_id=model_id, dataset=dataset
        )
        if response.status_code < 300:
            dataset = self._get_dataset_with_polling(response)
            if dataset.status == "SUCCESS":
                return dataset.result
            elif dataset.status == "FAILURE":
                raise JaqpotPredictionFailureException(dataset.failure_reason)
        raise JaqpotApiException(
            message=response.data.to_dict().get('message', 'Unknown error'),
            status_code=response.status_code,
        )

    def predict_async(self, model_id: int, dataset: Union[List[Dict[str, Any]], Dict[str, Any]]) -> int:
        """Make an asynchronous prediction with a model on Jaqpot.

        Parameters
        ----------
        model_id : int
            The ID of the model on Jaqpot.
        dataset : list or dict
            The dataset to predict.

        Returns
        -------
        int
            The ID of the dataset containing the prediction results.

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        """
        dataset = Dataset(
            type=DatasetType.PREDICTION,
            entry_type="ARRAY",
            input=dataset,
        )

        model_api = ModelApi(self.http_client)
        response = model_api.predict_with_model_with_http_info(
            model_id=model_id, dataset=dataset
        )
        if response.status_code < 300:
            dataset_location = response.headers["Location"]
            dataset_id = int(dataset_location.split("/")[-1])
            return dataset_id
        raise JaqpotApiException(
            message=response.data.to_dict().get('message', 'Unknown error'),
            status_code=response.status_code,
        )

    def predict_with_csv_sync(self, model_id: int, csv_path: str) -> Any:
        """Make a synchronous prediction with a model on Jaqpot using a CSV file.

        Parameters
        ----------
        model_id : int
            The ID of the model on Jaqpot.
        csv_path : str
            The path to the CSV file.

        Returns
        -------
        dict
            The prediction result.

        Raises
        ------
        JaqpotApiException
            If the request fails, an exception is raised with the error message and status code.
        JaqpotPredictionFailureException
            If the prediction fails, an exception is raised with the failure reason.
        """
        b64_dataset_csv = file_to_b64encoding(csv_path)
        dataset_csv = DatasetCSV(
            type=DatasetType.PREDICTION, input_file=b64_dataset_csv
        )
        model_api = ModelApi(self.http_client)
        response = model_api.predict_with_model_csv_with_http_info(
            model_id=model_id, dataset_csv=dataset_csv
        )
        if response.status_code < 300:
            dataset = self._get_dataset_with_polling(response)
            if dataset.status == "SUCCESS":
                return dataset.result
            elif dataset.status == "FAILURE":
                raise JaqpotPredictionFailureException(message=dataset.failure_reason)
        raise JaqpotApiException(
            message=response.data.to_dict().get('message', 'Unknown error'),
            status_code=response.status_code,
        )

    def _get_dataset_with_polling(self, response):
        """Retrieve a dataset by polling until it is ready or a timeout occurs.

        Parameters
        ----------
        response : requests.Response
            The HTTP response object containing the dataset location in the headers.

        Returns
        -------
        dict
            The dataset retrieved from the server.

        Raises
        ------
        JaqpotPredictionTimeoutException
            If polling times out while waiting for the dataset to be ready.
        """
        dataset_location = response.headers["Location"]
        dataset_id = int(dataset_location.split("/")[-1])
        try:
            polling2.poll(
                lambda: self.get_dataset_by_id(dataset_id).status
                in ["SUCCESS", "FAILURE"],
                step=3,
                timeout=10 * 60,
            )
        except polling2.TimeoutException:
            raise JaqpotPredictionTimeoutException(
                message="Polling timed out while waiting for prediction result."
            )
        dataset = self.get_dataset_by_id(dataset_id)
        return dataset

    def qsartoolbox_calculator_predict_sync(self, smiles: str, calculator_guid: str) -> Any:
        """Synchronously predict using the QSAR Toolbox calculator.

        Parameters
        ----------
        smiles : str
            The SMILES string representing the chemical structure.
        calculator_guid : str
            The unique identifier for the QSAR Toolbox calculator.

        Returns
        -------
        dict
            The prediction result from the QSAR Toolbox calculator.
        """
        dataset = [{"smiles": smiles, "calculatorGuid": calculator_guid}]
        prediction = self.predict_sync(QSARTOOLBOX_CALCULATOR_MODEL_ID, dataset)
        return prediction

    def qsartoolbox_qsar_model_predict_sync(self, smiles: str, qsar_guid: str) -> Any:
        """Synchronously predict QSAR model results using the QSAR Toolbox.

        Parameters
        ----------
        smiles : str
            The SMILES string representing the chemical structure.
        qsar_guid : str
            The unique identifier for the QSAR model.

        Returns
        -------
        dict
            The prediction results from the QSAR model.
        """
        dataset = [{"smiles": smiles, "qsarGuid": qsar_guid}]
        prediction = self.predict_sync(QSARTOOLBOX_MODEL_MODEL_ID, dataset)
        return prediction

    def qsartoolbox_profiler_predict_sync(self, smiles: str, profiler_guid: str) -> Any:
        """Synchronously predict using the QSAR Toolbox profiler.

        Parameters
        ----------
        smiles : str
            The SMILES string representing the chemical structure.
        profiler_guid : str
            The unique identifier for the profiler.

        Returns
        -------
        dict
            The prediction result from the QSAR profiler model.
        """
        dataset = [{"smiles": smiles, "profilerGuid": profiler_guid}]
        prediction = self.predict_sync(QSAR_PROFILER_MODEL_ID, dataset)
        return prediction
