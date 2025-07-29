from typing import Any, Dict
import requests

class Dataset:
    """
    A class to represent a dataset using Schema.org's Dataset type.

    Attributes
    ----------
    metadata : dict
        A dictionary to hold the metadata of the dataset.

    Methods
    -------
    set_metadata(key: str, value: Any):
        Sets a metadata field.
    send_to_kalouk():
        Sends the dataset metadata to Kalouk's API.
    """
    def __init__(self) -> None:
        """Initialize the Dataset with empty metadata."""
        self.metadata: Dict[str, Any] = {}

    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata field.

        Parameters
        ----------
        key : str
            The metadata key.
        value : Any
            The metadata value.
        """
        self.metadata[key] = value

    def send_to_kalouk(self) -> requests.Response:
        """Send the dataset metadata to Kalouk's API.

        Returns
        -------
        requests.Response
            The response from the API request.
        """
        response = requests.post('https://web.kalouk.xyz/api/datasets', json=self.metadata)
        return response

