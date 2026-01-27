"""Noise generation for radar simulation."""
import random
import math
from typing import List

class NoiseGenerator:
    """Generates various types of radar noise."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.thermal_noise_level = 0.02
        self.receiver_noise_level = 0.01

    def generate_thermal_noise(self, num_samples: int) -> List[float]:
        """Generate thermal noise (Gaussian distribution).

        Args:
            num_samples: Number of noise samples to generate

        Returns:
            List of noise values
        """
        return [random.gauss(0, self.thermal_noise_level) for _ in range(num_samples)]

    def add_noise_to_sweep(self, sweep_data: List[float], noise_level: float = None) -> List[float]:
        """Add noise to sweep data.

        Args:
            sweep_data: Original sweep data
            noise_level: Override noise level (default uses thermal_noise_level)

        Returns:
            Sweep data with added noise
        """
        level = noise_level if noise_level is not None else self.thermal_noise_level
        return [
            max(0.0, min(1.0, val + random.gauss(0, level)))
            for val in sweep_data
        ]

    def set_noise_level(self, level: float) -> None:
        """Set the thermal noise level."""
        self.thermal_noise_level = max(0.0, min(0.5, level))
