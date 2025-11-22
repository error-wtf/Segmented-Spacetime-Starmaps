"""
Astronomical catalog retrieval modules.

Supports:
- GAIA DR3 (positions, parallax, proper motion)
- SIMBAD (named objects, stellar parameters)
- Mock catalogs (offline mode)

© 2025 Carmen Wrede, Lino Casu
"""

from .gaia_fetch import fetch_gaia_nearby, fetch_gaia_cone, INTERESTING_REGIONS
from .simbad_fetch import fetch_named_star, fetch_bright_stars
from .manager import CatalogManager, StarEntry

__all__ = [
    'fetch_gaia_nearby',
    'fetch_gaia_cone',
    'fetch_named_star',
    'fetch_bright_stars',
    'CatalogManager',
    'StarEntry',
    'INTERESTING_REGIONS',
]
