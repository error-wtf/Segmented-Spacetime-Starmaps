#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NED Fetcher - Sprint 4 Task 1
NASA/IPAC Extragalactic Database integration

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import logging
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from astroquery.ipac.ned import Ned
    NED_AVAILABLE = True
except ImportError:
    NED_AVAILABLE = False
    logger.warning("NED not available")


class NEDFetcher:
    """Fetch galaxy data from NASA/IPAC Extragalactic Database."""
    
    def __init__(self):
        self.available = NED_AVAILABLE
        if self.available:
            logger.info("NED initialized")
    
    def is_available(self) -> bool:
        return self.available
    
    def cone_search(self, ra: float, dec: float, radius: float = 5.0) -> Optional[pd.DataFrame]:
        """Cone search for galaxies."""
        if not self.available:
            return None
        
        try:
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            
            coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
            result = Ned.query_region(coord, radius=radius*u.arcmin)
            
            if result is None or len(result) == 0:
                return None
            
            df = result.to_pandas()
            df['source_catalog'] = 'NED'
            return df
            
        except Exception as e:
            logger.error(f"NED cone search error: {e}")
            return None
    
    def query_by_name(self, name: str) -> Optional[pd.DataFrame]:
        """Query by object name."""
        if not self.available:
            return None
        
        try:
            result = Ned.query_object(name)
            if result is None:
                return None
            
            df = result.to_pandas()
            df['source_catalog'] = 'NED'
            return df
            
        except Exception as e:
            logger.error(f"NED name query error: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        return {
            'catalog': 'NED',
            'available': self.available,
            'objects': '200M+ galaxies',
            'coverage': 'All-sky extragalactic'
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("="*80)
    print("NED FETCHER TEST")
    print("="*80)
    
    fetcher = NEDFetcher()
    
    if not fetcher.is_available():
        print("❌ NED not available!")
    else:
        print("✅ NED available!")
        
        # Test query
        result = fetcher.query_by_name("M31")
        if result is not None:
            print(f"✅ Found M31: {len(result)} entries")
    
    print("="*80)
