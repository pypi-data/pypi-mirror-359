"""
ObjectProcessor.py
------------------
Client-side adapter for sending detected object data from image-processing-service
to the text-processing-service endpoint for further product-level analysis.
"""

import requests
from typing import Any, Dict, List
from isloth_text_processing_service_python_interface.dtos.image.ImageObjectInput import ImageObjectInput
from isloth_text_processing_service_python_interface.services.interfaces.IObjectProcessor import IObjectProcessor


class ObjectProcessor(IObjectProcessor):
    """
    HTTP client that implements object processing by delegating to the text-processing-service.
    """

    def __init__(self, host: str = 'http://localhost:8002', route: str = '/api/v1/texts/image'):
        """
        Initialize the adapter with the target text-processing-service URL.

        Parameters
        ----------
        host : str
            Base URL of the text-processing-service.
        route : str
            Route for image object processing.
        """
        self.url = f'{host.rstrip("/")}{route}'

    def process_objects(self, object_data: List[ImageObjectInput]) -> List[Dict[str, Any]]:
        """
        Send image object data to the text-processing-service for product detection.

        Parameters
        ----------
        object_data : List[ImageObjectInput]
            List of DTOs containing binary image data and metadata.

        Returns
        -------
        List[Dict[str, Any]]
            List of extracted products from the object images.
        """
        payload = [obj.model_dump() for obj in object_data]
        response = requests.post(self.url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

