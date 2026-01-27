"""Radar antenna simulation."""
import math
from dataclasses import dataclass
from .parameters import RadarParameters

@dataclass
class AntennaState:
    """Current state of the antenna."""
    bearing: float = 0.0  # Current bearing in degrees
    rotation_direction: int = 1  # 1 = clockwise, -1 = counter-clockwise

class Antenna:
    """Simulates radar antenna rotation and beam pattern."""

    def __init__(self, params: RadarParameters):
        self.params = params
        self.state = AntennaState()

    def update(self, dt: float) -> None:
        """Update antenna position based on time step.

        Args:
            dt: Time step in seconds
        """
        # Calculate rotation rate in degrees per second
        degrees_per_second = (self.params.rotation_rpm / 60.0) * 360.0

        # Update bearing
        self.state.bearing += degrees_per_second * dt * self.state.rotation_direction
        self.state.bearing = self.state.bearing % 360.0

    def get_bearing(self) -> float:
        """Get current antenna bearing in degrees."""
        return self.state.bearing

    def set_bearing(self, bearing: float) -> None:
        """Set antenna bearing directly (for testing/debugging)."""
        self.state.bearing = bearing % 360.0

    def get_beam_pattern(self, angle_offset: float) -> float:
        """Get antenna gain at a given angle offset from beam center.

        Args:
            angle_offset: Angle in degrees from beam center

        Returns:
            Relative gain (0-1) at the given angle
        """
        # Simplified sinc-squared beam pattern
        half_beamwidth = self.params.horizontal_beamwidth_deg / 2

        if abs(angle_offset) < 0.01:
            return 1.0

        # Normalize angle to beamwidth
        x = angle_offset / half_beamwidth

        # Sinc-squared pattern with side lobes
        if abs(x) > 5:
            return 0.001  # Very low gain in far side lobes

        sinc = math.sin(math.pi * x / 2) / (math.pi * x / 2) if abs(x) > 0.01 else 1.0
        return max(0.001, sinc * sinc)

    def is_target_in_beam(self, target_bearing: float, threshold: float = 0.1) -> bool:
        """Check if a target bearing is within the main beam.

        Args:
            target_bearing: Target bearing in degrees
            threshold: Minimum relative gain to consider 'in beam'

        Returns:
            True if target is within beam
        """
        angle_diff = (target_bearing - self.state.bearing + 180) % 360 - 180
        return self.get_beam_pattern(angle_diff) >= threshold

    def get_gain_for_target(self, target_bearing: float) -> float:
        """Get the antenna gain for a target at a given bearing.

        Args:
            target_bearing: Target bearing in degrees

        Returns:
            Relative gain (0-1)
        """
        angle_diff = (target_bearing - self.state.bearing + 180) % 360 - 180
        return self.get_beam_pattern(angle_diff)
