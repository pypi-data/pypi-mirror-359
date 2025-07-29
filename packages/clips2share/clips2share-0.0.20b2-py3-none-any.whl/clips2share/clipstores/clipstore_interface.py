from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Clip:
    title: str
    studio: str
    url: str
    image_url: str

class ClipstoreInterface(ABC):
    """
    Clipstore Interface to adapt new clipstore
    """
    supported_urls = None

    @staticmethod
    @abstractmethod
    def extract_clip_data(clip_url: str) -> Clip:
        """ Extracts clipdata from given clip store url and returns Clip Object """
        raise NotImplementedError
