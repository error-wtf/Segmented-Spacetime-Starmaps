"""
Core rendering and coordinate systems.

© 2025 Carmen Wrede, Lino Casu
"""

from .renderer import SkymapRenderer
from .coordinates import (
    galactic_to_cartesian,
    cartesian_to_spherical,
    spherical_to_cartesian,
    apply_ssz_stretch,
    prepare_star_coordinates,
    prepare_ssz_coordinates,
    calculate_distance_3d,
    get_region_stars,
    get_box_stars
)
from .camera import Camera

__all__ = [
    'SkymapRenderer',
    'galactic_to_cartesian',
    'cartesian_to_spherical',
    'spherical_to_cartesian',
    'apply_ssz_stretch',
    'prepare_star_coordinates',
    'prepare_ssz_coordinates',
    'calculate_distance_3d',
    'get_region_stars',
    'get_box_stars',
    'Camera'
]
