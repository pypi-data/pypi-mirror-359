from fastsdk import FastSDK, APISeex
from typing import Union

from media_toolkit import MediaFile


class nsfw_image_detection(FastSDK):
    """
    Generated client for falcons-ai/nsfw-image-detection
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="8e26b425-7598-435b-8e80-38e58d4b1664", api_key=api_key)
    
    def predictions(self, image: Union[str, MediaFile, bytes], **kwargs) -> APISeex:
        """
        
        
        
        Args:
            image: Input image
            
        """
        return self.submit_job("/predictions", image=image, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions