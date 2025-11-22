"""
SSZ StarMaps - Main Demo Script

**AKTUALISIERT MIT ECHTER SSZ-LOGIK!**

Demonstrates:
1. Fetching real star catalog data from SIMBAD
2. Projecting stars onto a 2D plane
3. Applying ECHTE SSZ metric deformations (Xi(r) = 1 - exp(-phi*r/r_s))
4. Computing orbit circumferences with Ramanujan's formula
5. Visualizing Minkowski vs SSZ star positions

KEINE FAKE-LOGIK! Basiert auf ssz-metric-pure (Carmen Wrede & Lino Casu)

© 2025 Carmen Wrede, Lino Casu
Licensed under the Anti-Capitalist Software License v1.4
"""

import numpy as np
import matplotlib.pyplot as plt
from .catalog import fetch_sample_catalog, create_mock_catalog
from .projection import gnomonic_projection, apply_ssz_metric_deformation
from .geometry import compute_circumference_ratio
from .ssz_metric import PHI


def main():
    """Main demonstration of SSZ StarMaps."""
    
    print("\n" + "=" * 70)
    print("SSZ STARMAPS - Segmented Spacetime Star Map Demo")
    print("=" * 70)
    
    # Configuration - ECHTE SSZ PARAMETER!
    M_sun = 1.98847e30  # kg (Sun's mass)
    r_scale = 0.5  # Scale factor for coordinate units
    use_real_data = True  # Set to False for offline testing
    
    print(f"\nPhysical Parameters:")
    print(f"  phi (golden ratio) = {PHI:.6f}")
    print(f"  Mass = {M_sun:.3e} kg (Sun)")
    print(f"  SSZ Formula: Xi(r) = 1 - exp(-phi*r/r_s)")
    
    # Step 1: Fetch star catalog
    print("\n[1/5] Fetching star catalog...")
    
    if use_real_data:
        catalog = fetch_sample_catalog(
            center_ra_deg=0.0,
            center_dec_deg=0.0,
            radius_deg=5.0,
            limit=50
        )
        if catalog is None:
            print("  Failed to fetch real data, using mock catalog instead.")
            catalog = create_mock_catalog(n_stars=50)
    else:
        catalog = create_mock_catalog(n_stars=50)
    
    ra = catalog['ra']
    dec = catalog['dec']
    print(f"  [OK] Loaded {len(ra)} stars")
    
    # Step 2: Project to 2D
    print("\n[2/5] Projecting to 2D plane (gnomonic)...")
    x_mink, y_mink = gnomonic_projection(ra, dec, center_ra=np.mean(ra), center_dec=np.mean(dec))
    print(f"  [OK] Projected {len(x_mink)} positions")
    
    # Step 3: Apply ECHTE SSZ deformation!
    print(f"\n[3/5] Applying ECHTE SSZ deformation...")
    print(f"  Formula: R_ssz = r * (1 + Xi(r))")
    x_ssz, y_ssz = apply_ssz_metric_deformation(
        x_mink, y_mink,
        mass_kg=M_sun,
        r_scale_deg=r_scale
    )
    print(f"  [OK] Deformed coordinates computed (phi-based!)")
    
    # Step 4: Orbit circumference analysis (Ramanujan ellipse formula)
    print("\n[4/5] Computing orbit circumferences (Ramanujan formula)...")
    r_orbit = 1.0  # arbitrary units
    eps_ellipse = 0.15  # ellipse eccentricity parameter (separate from SSZ deformation!)
    result = compute_circumference_ratio(r_orbit, eps_ellipse)
    
    print(f"\n  Ellipse Analysis (r = {r_orbit}, eps = {eps_ellipse}):")
    print(f"    Minkowski (circle):  C = {result['C_minkowski']:.6f}")
    print(f"    Ellipse (Ramanujan): C = {result['C_ssz']:.6f}")
    print(f"    Semi-axes:           a = {result['a']:.4f}, b = {result['b']:.4f}")
    print(f"    Circumference ratio: {result['ratio']:.6f}")
    print(f"    Deviation:           {result['deviation_percent']:+.3f}%")
    
    # Step 5: Visualization
    print("\n[5/5] Generating plot...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Minkowski projection
    ax1.scatter(x_mink, y_mink, s=30, c='blue', alpha=0.6, edgecolors='darkblue', label='Stars')
    ax1.set_xlabel('RA offset [deg]', fontsize=11)
    ax1.set_ylabel('Dec offset [deg]', fontsize=11)
    ax1.set_title('Minkowski Projection (Standard Sky)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    ax1.legend()
    
    # SSZ projection - ECHTE PHYSIK!
    ax2.scatter(x_ssz, y_ssz, s=30, c='red', alpha=0.6, edgecolors='darkred', 
                label=f'Stars (SSZ, phi={PHI:.3f})')
    ax2.set_xlabel('x\' [deg]', fontsize=11)
    ax2.set_ylabel('y\' [deg]', fontsize=11)
    ax2.set_title(r'SSZ Projection: $\Xi(r) = 1 - e^{-\phi r/r_s}$', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('ssz_starmap_demo.png', dpi=150, bbox_inches='tight')
    print("  [OK] Plot saved: ssz_starmap_demo.png")
    
    plt.show()
    
    print("\n" + "=" * 70)
    print("[OK] Demo complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
