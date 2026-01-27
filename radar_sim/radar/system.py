"""Integrated radar system combining all radar components."""
from typing import List, Optional, Tuple
from .parameters import RadarParameters
from .antenna import Antenna
from .detection import DetectionEngine, Detection
from ..core.world import World

class RadarSystem:
    """Complete radar system integrating antenna, detection, and processing."""

    def __init__(self, params: Optional[RadarParameters] = None):
        self.params = params or RadarParameters()
        self.antenna = Antenna(self.params)
        self.detection_engine = DetectionEngine(self.params, self.antenna)

        # Sweep data storage (polar format)
        self.num_bearings = 360  # One degree resolution
        self.num_range_bins = 512
        self.sweep_buffer: List[List[float]] = [
            [0.0] * self.num_range_bins for _ in range(self.num_bearings)
        ]

        # Detection history
        self.detections: List[Detection] = []
        self.detection_persistence_s: float = 5.0  # How long detections persist

        # State
        self.is_transmitting = True
        self.last_bearing = 0.0

    def update(self, world: World, dt: float) -> None:
        """Update radar system state.

        Args:
            world: World containing all vessels
            dt: Time step in seconds
        """
        if not self.is_transmitting or world.own_ship is None:
            return

        # Update antenna position
        self.antenna.update(dt)
        current_bearing = self.antenna.get_bearing()

        # Get own ship position
        own_x = world.own_ship.x
        own_y = world.own_ship.y

        # Get targets (all vessels except own ship)
        targets = world.get_targets()

        # Generate sweep data for current bearing
        sweep_data = self.detection_engine.generate_sweep_data(
            targets, own_x, own_y, world.time, self.num_range_bins
        )

        # Store in sweep buffer (quantize bearing to integer degree)
        bearing_idx = int(current_bearing) % self.num_bearings
        self.sweep_buffer[bearing_idx] = sweep_data

        # Process detections when we complete a bearing
        if int(current_bearing) != int(self.last_bearing):
            new_detections = self.detection_engine.detect_targets(
                targets, own_x, own_y, world.time
            )

            # Filter out old detections and add new ones
            self.detections = [
                d for d in self.detections
                if world.time - d.timestamp < self.detection_persistence_s
            ]
            self.detections.extend(new_detections)

        self.last_bearing = current_bearing

    def get_sweep_buffer(self) -> List[List[float]]:
        """Get the complete sweep buffer."""
        return self.sweep_buffer

    def get_sweep_at_bearing(self, bearing: float) -> List[float]:
        """Get sweep data for a specific bearing."""
        bearing_idx = int(bearing) % self.num_bearings
        return self.sweep_buffer[bearing_idx]

    def get_detections(self) -> List[Detection]:
        """Get current detection list."""
        return self.detections

    def get_current_bearing(self) -> float:
        """Get current antenna bearing."""
        return self.antenna.get_bearing()

    def set_range_scale(self, range_nm: float) -> None:
        """Set the radar range scale."""
        self.params.set_range_scale(range_nm)

    def set_gain(self, gain: float) -> None:
        """Set receiver gain (0-1)."""
        self.params.gain = max(0.0, min(1.0, gain))

    def set_sea_clutter(self, level: float) -> None:
        """Set sea clutter suppression level (0-1)."""
        self.params.sea_clutter = max(0.0, min(1.0, level))

    def set_rain_clutter(self, level: float) -> None:
        """Set rain clutter suppression level (0-1)."""
        self.params.rain_clutter = max(0.0, min(1.0, level))

    def toggle_transmission(self) -> bool:
        """Toggle radar transmission on/off."""
        self.is_transmitting = not self.is_transmitting
        return self.is_transmitting

    def clear_sweep_buffer(self) -> None:
        """Clear all sweep data."""
        for i in range(self.num_bearings):
            self.sweep_buffer[i] = [0.0] * self.num_range_bins
        self.detections.clear()
