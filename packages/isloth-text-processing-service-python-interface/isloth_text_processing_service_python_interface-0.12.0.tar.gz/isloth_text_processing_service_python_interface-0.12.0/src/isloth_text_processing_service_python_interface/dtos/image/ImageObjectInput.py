"""
ImageObjectInput.py
-------------------
Defines the input data model for object-level image processing requests.
Used by image-processing-service to send metadata and cropped image to text-processing-service.
"""

from pydantic import BaseModel, ConfigDict
from typing import Dict, Any


class ImageObjectInput(BaseModel):
    """
    DTO representing a single detected object input from the image-processing-service.

    Attributes
    ----------
    metadata : dict
        Dictionary containing object detection metadata such as coordinates, 
        labels, or model confidence.
    image : IO
        File-like object containing the cropped image (e.g., SpooledTemporaryFile).
    """
    metadata: Dict
    image: Any
    model_config = ConfigDict(arbitrary_types_allowed=True)
