#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera controls for 3D navigation.

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
from typing import Dict, Tuple


class Camera:
    """
    3D Camera with orbital controls.
    
    Parameters
    ----------
    distance : float
        Distance from target
    theta : float
        Polar angle (elevation) in radians
    phi : float
        Azimuthal angle (rotation) in radians
    target : tuple
        Look-at target (x, y, z)
    """
    
    def __init__(
        self,
        distance: float = 100.0,
        theta: float = np.pi/4,
        phi: float = np.pi/4,
        target: Tuple[float, float, float] = (0, 0, 0)
    ):
        self.distance = distance
        self.theta = theta  # elevation
        self.phi = phi  # rotation
        self.target = np.array(target)
        
        self.min_distance = 1.0
        self.max_distance = 10000.0
    
    def get_position(self) -> Tuple[float, float, float]:
        """
        Get camera position in Cartesian coordinates.
        
        Returns
        -------
        tuple
            (x, y, z) camera position
        """
        x = self.distance * np.sin(self.theta) * np.cos(self.phi)
        y = self.distance * np.sin(self.theta) * np.sin(self.phi)
        z = self.distance * np.cos(self.theta)
        
        return tuple(self.target + np.array([x, y, z]))
    
    def rotate(self, delta_phi: float, delta_theta: float):
        """
        Rotate camera.
        
        Parameters
        ----------
        delta_phi : float
            Change in azimuthal angle (radians)
        delta_theta : float
            Change in polar angle (radians)
        """
        self.phi += delta_phi
        self.theta += delta_theta
        
        # Clamp theta to avoid gimbal lock
        self.theta = np.clip(self.theta, 0.01, np.pi - 0.01)
    
    def zoom(self, factor: float):
        """
        Zoom camera (change distance).
        
        Parameters
        ----------
        factor : float
            Zoom factor (>1 = zoom out, <1 = zoom in)
        """
        self.distance *= factor
        self.distance = np.clip(
            self.distance,
            self.min_distance,
            self.max_distance
        )
    
    def pan(self, dx: float, dy: float, dz: float):
        """
        Pan camera (move target).
        
        Parameters
        ----------
        dx, dy, dz : float
            Target displacement
        """
        self.target += np.array([dx, dy, dz])
    
    def look_at(self, target: Tuple[float, float, float]):
        """
        Set new look-at target.
        
        Parameters
        ----------
        target : tuple
            New target (x, y, z)
        """
        self.target = np.array(target)
    
    def get_eye_dict(self) -> Dict:
        """
        Get camera eye position for Plotly.
        
        Returns
        -------
        dict
            {'x': ..., 'y': ..., 'z': ...}
        """
        pos = self.get_position()
        # Normalize for Plotly (relative to scene)
        norm = np.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
        if norm > 0:
            return {
                'x': pos[0] / norm * 2,
                'y': pos[1] / norm * 2,
                'z': pos[2] / norm * 2
            }
        else:
            return {'x': 1.5, 'y': 1.5, 'z': 1.2}
    
    def get_camera_dict(self) -> Dict:
        """
        Get full camera dict for Plotly.
        
        Returns
        -------
        dict
            Camera configuration
        """
        return {
            'eye': self.get_eye_dict(),
            'center': {'x': 0, 'y': 0, 'z': 0},
            'up': {'x': 0, 'y': 0, 'z': 1}
        }
    
    def orbit_preset(self, preset: str):
        """
        Apply camera preset.
        
        Parameters
        ----------
        preset : str
            'top', 'side', 'front', 'isometric'
        """
        presets = {
            'top': (np.pi/2, 0.01, 100),
            'side': (np.pi/2, np.pi/2, 100),
            'front': (np.pi/2, 0, 100),
            'isometric': (np.pi/4, np.pi/4, 100),
            'far': (np.pi/3, np.pi/3, 300)
        }
        
        if preset in presets:
            self.phi, self.theta, self.distance = presets[preset]
