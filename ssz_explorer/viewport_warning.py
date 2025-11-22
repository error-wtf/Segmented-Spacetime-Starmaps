#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Viewport Warning System - Phase A Fix 2

Simple warning when user moves outside loaded region.

© 2025 Carmen Wrede, Lino Casu
"""

class ViewportWarning:
    """Track loaded regions and warn when outside."""
    
    def __init__(self):
        self.loaded_region = None
        
    def set_loaded_region(self, ra_min, ra_max, dec_min, dec_max):
        """Store currently loaded region."""
        self.loaded_region = {
            'ra_min': ra_min,
            'ra_max': ra_max,
            'dec_min': dec_min,
            'dec_max': dec_max
        }
    
    def check_viewport(self, ra_min, ra_max, dec_min, dec_max):
        """
        Check if viewport is outside loaded region.
        
        Returns
        -------
        tuple
            (needs_reload: bool, message: str)
        """
        if self.loaded_region is None:
            return True, "⚠️ Loading initial data..."
        
        # Check if completely outside
        if (ra_max < self.loaded_region['ra_min'] or
            ra_min > self.loaded_region['ra_max'] or
            dec_max < self.loaded_region['dec_min'] or
            dec_min > self.loaded_region['dec_max']):
            return True, "⚠️ Loading data for this region..."
        
        # Check if partially outside (>50% outside)
        overlap_ra = min(ra_max, self.loaded_region['ra_max']) - max(ra_min, self.loaded_region['ra_min'])
        overlap_dec = min(dec_max, self.loaded_region['dec_max']) - max(dec_min, self.loaded_region['dec_min'])
        
        total_ra = ra_max - ra_min
        total_dec = dec_max - dec_min
        
        overlap_percent = (overlap_ra * overlap_dec) / (total_ra * total_dec)
        
        if overlap_percent < 0.5:
            return True, "⚠️ Loading additional data..."
        
        return False, ""
