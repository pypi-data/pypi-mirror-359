"""Tests for the Dataset class."""

import pytest
from unittest.mock import patch, Mock
from kalouk import Dataset


def test_dataset_initialization():
    """Test that Dataset initializes with empty metadata."""
    dataset = Dataset()
    assert dataset.metadata == {}


def test_set_metadata():
    """Test setting metadata fields."""
    dataset = Dataset()
    dataset.set_metadata("name", "Test Dataset")
    dataset.set_metadata("description", "A test dataset")
    
    assert dataset.metadata["name"] == "Test Dataset"
    assert dataset.metadata["description"] == "A test dataset"


@patch('kalouk.dataset.requests.post')
def test_send_to_kalouk(mock_post):
    """Test sending dataset to Kalouk API."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    
    # Create dataset and add metadata
    dataset = Dataset()
    dataset.set_metadata("name", "Test Dataset")
    dataset.set_metadata("description", "A test dataset")
    
    # Send to API
    response = dataset.send_to_kalouk()
    
    # Verify the request was made correctly
    mock_post.assert_called_once_with(
        'https://web.kalouk.xyz/api/datasets',
        json={"name": "Test Dataset", "description": "A test dataset"}
    )
    assert response.status_code == 200
