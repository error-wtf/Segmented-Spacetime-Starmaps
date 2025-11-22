#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDSS Fetcher - Sprint 4 Task 2
Sloan Digital Sky Survey integration

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import logging
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from astroquery.sdss import SDSS
    SDSS_AVAILABLE = True
except ImportError:
    SDSS_AVAILABLE = False
    logger.warning("SDSS not available")


class SDSSFetcher:
    """Fetch galaxy data from Sloan Digital Sky Survey."""
    
    def __init__(self):
        self.available = SDSS_AVAILABLE
        if self.available:
            logger.info("SDSS initialized")
    
    def is_available(self) -> bool:
        return self.available
    
    def cone_search(self, ra: float, dec: float, radius: float = 3.0) -> Optional[pd.DataFrame]:
        """Cone search for SDSS objects."""
        if not self.available:
            return None
        
        try:
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            
            coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
            result = SDSS.query_region(coord, radius=radius*u.arcmin, spectro=True)
            
            if result is None or len(result) == 0:
                return None
            
            df = result.to_pandas()
            df['source_catalog'] = 'SDSS'
            return df
            
        except Exception as e:
            logger.error(f"SDSS cone search error: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        return {
            'catalog': 'SDSS',
            'available': self.available,
            'objects': '1M+ galaxies with spectra',
            'coverage': '~35% of sky'
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("="*80)
    print("SDSS FETCHER TEST")
    print("="*80)
    
    fetcher = SDSSFetcher()
    
    if not fetcher.is_available():
        print("❌ SDSS not available!")
    else:
        print("✅ SDSS available!")
    
    print("="*80)
