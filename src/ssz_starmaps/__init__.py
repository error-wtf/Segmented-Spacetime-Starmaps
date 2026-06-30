"""
SSZ StarMaps - Segmented Spacetime Star Map Generator

**AKTUALISIERT MIT ECHTER SSZ-LOGIK aus ssz-metric-pure!**

A Python package for generating star maps with Segmented Spacetime (SSZ) 
metric deformations, using real astronomical catalog data.

KEINE FAKE-LOGIK! Basiert auf echter SSZ-Physik (Carmen Wrede & Lino Casu).

Kernformeln:
- Segment Saturation: Xi(r) = 1 - exp(-phi * r_s / r)
- Time Dilation SSZ: D_SSZ(r) = 1 / (1 + Xi(r))
- SSZ Deformation: R_ssz = r * (1 + Xi(r))

© 2025 Carmen Wrede, Lino Casu
Licensed under the Anti-Capitalist Software License v1.4
"""

__version__ = "0.2.0"  # Major update: ECHTE SSZ-Logik!

# Geometry (Ramanujan ellipse formulas)
from .geometry import ramanujan_ellipse_circumference, deform_circle_to_ellipse

# Catalog (SIMBAD + GAIA DR3)
from .catalog import fetch_sample_catalog, fetch_gaia_catalog, create_mock_catalog

# Projection (Gnomonic + SSZ deformations)
from .projection import (
    gnomonic_projection,
    apply_ssz_deformation,  # LEGACY! Use apply_ssz_metric_deformation instead
    apply_ssz_metric_deformation  # ECHTE SSZ-Logik!
)

# SSZ Metric (Xi(r)-ANSATZ ONLY!)
from .ssz_metric import (
    Xi,  # Segment saturation: 1 - exp(-phi*r_s / r)
    radial_stretch,  # Stretch factor: 1 + Xi(r)
    D_SSZ,  # SSZ time dilation: 1 / (1 + Xi)
    D_GR,  # GR time dilation: sqrt(1 - r_s/r)
    PHI,  # Golden ratio constant
    schwarzschild_radius  # r_s = 2GM/c^2
)

__all__ = [
    # Geometry
    "ramanujan_ellipse_circumference",
    "deform_circle_to_ellipse",
    # Catalog
    "fetch_sample_catalog",
    "fetch_gaia_catalog",
    "create_mock_catalog",
    # Projection
    "gnomonic_projection",
    "apply_ssz_deformation",  # LEGACY
    "apply_ssz_metric_deformation",  # ECHTE SSZ
    # SSZ Metric
    "Xi",
    "radial_stretch",
    "D_SSZ",
    "D_GR",
    "PHI",
    "schwarzschild_radius",
]
