"""Tests for model search functionality."""

import pytest
from unittest.mock import Mock, patch
from jaqpot_python_sdk.jaqpot_api_client import JaqpotApiClient
from jaqpot_python_sdk.exceptions.exceptions import JaqpotApiException


class TestModelSearch:
    """Test cases for model search functionality."""

    @patch('jaqpot_python_sdk.jaqpot_api_client.JaqpotApiHttpClientBuilder')
    def test_search_models_success(self, mock_builder):
        """Test successful model search."""
        # Mock the HTTP client and response
        mock_http_client = Mock()
        mock_builder.return_value.build_with_api_keys.return_value.build.return_value = mock_http_client
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data.to_dict.return_value = {
            'content': [
                {
                    'id': 1,
                    'name': 'Test Model 1',
                    'description': 'A test model for machine learning',
                    'type': 'REGRESSION'
                },
                {
                    'id': 2,
                    'name': 'Test Model 2', 
                    'description': 'Another test model',
                    'type': 'CLASSIFICATION'
                }
            ],
            'totalElements': 2,
            'totalPages': 1,
            'pageSize': 20,
            'pageNumber': 0
        }
        
        # Mock ModelApi
        with patch('jaqpot_python_sdk.jaqpot_api_client.ModelApi') as mock_model_api:
            mock_model_api.return_value.search_models_with_http_info.return_value = mock_response
            
            # Create client and test search
            client = JaqpotApiClient()
            result = client.search_models(query="test", page=0, size=20)
            
            # Assertions
            assert result is not None
            assert 'content' in result
            assert len(result['content']) == 2
            assert result['totalElements'] == 2
            assert result['content'][0]['name'] == 'Test Model 1'
            
            # Verify API was called correctly
            mock_model_api.return_value.search_models_with_http_info.assert_called_once_with(
                query="test", page=0, size=20
            )

    @patch('jaqpot_python_sdk.jaqpot_api_client.JaqpotApiHttpClientBuilder')
    def test_search_models_default_params(self, mock_builder):
        """Test model search with default parameters."""
        # Mock the HTTP client and response
        mock_http_client = Mock()
        mock_builder.return_value.build_with_api_keys.return_value.build.return_value = mock_http_client
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data.to_dict.return_value = {'content': [], 'totalElements': 0}
        
        # Mock ModelApi
        with patch('jaqpot_python_sdk.jaqpot_api_client.ModelApi') as mock_model_api:
            mock_model_api.return_value.search_models_with_http_info.return_value = mock_response
            
            # Create client and test search with minimal params
            client = JaqpotApiClient()
            client.search_models(query="nonexistent")
            
            # Verify API was called with None for optional params
            mock_model_api.return_value.search_models_with_http_info.assert_called_once_with(
                query="nonexistent", page=None, size=None
            )

    @patch('jaqpot_python_sdk.jaqpot_api_client.JaqpotApiHttpClientBuilder')
    def test_search_models_api_error(self, mock_builder):
        """Test model search with API error."""
        # Mock the HTTP client and response
        mock_http_client = Mock()
        mock_builder.return_value.build_with_api_keys.return_value.build.return_value = mock_http_client
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.data.to_dict.return_value = {'message': 'Invalid query parameter'}
        
        # Mock ModelApi
        with patch('jaqpot_python_sdk.jaqpot_api_client.ModelApi') as mock_model_api:
            mock_model_api.return_value.search_models_with_http_info.return_value = mock_response
            
            # Create client and test search with error
            client = JaqpotApiClient()
            
            with pytest.raises(JaqpotApiException) as exc_info:
                client.search_models(query="")
                
            assert exc_info.value.status_code == 400
