"""
SSZ Skymap - Interactive3D-style 3D Interactive Star Map

An interactive 3D visualization tool for exploring the universe
with Segmented Spacetime (SSZ) physics.

© 2025 Carmen Wrede, Lino Casu
"""

__version__ = '0.1.0'

from .core import (
    SkymapRenderer,
    Camera,
    prepare_star_coordinates,
    prepare_ssz_coordinates
)

__all__ = [
    'SkymapRenderer',
    'Camera',
    'prepare_star_coordinates',
    'prepare_ssz_coordinates'
]
