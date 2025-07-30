"""TIF to GeoJSON converter with SAM-based automatic mask generation."""

__version__ = "1.0.2"
__author__ = "Nicholas McCarty"
__email__ = "nick@upskilled.consulting"

from .feature_extractor import RasterFeatureExtractor
from .mask_generator import MaskGenerator

__all__ = ["RasterFeatureExtractor", "MaskGenerator"]
