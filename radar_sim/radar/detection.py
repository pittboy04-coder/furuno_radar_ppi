"""Radar detection engine for target detection calculations."""
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .parameters import RadarParameters
from .antenna import Antenna
from ..objects.vessel import Vessel

@dataclass
class Detection:
    """Represents a radar detection/contact."""
    range_m: float
    bearing_deg: float
    intensity: float  # 0-1, signal strength
    vessel_id: Optional[str] = None  # If associated with a known vessel
    timestamp: float = 0.0

class DetectionEngine:
    """Handles radar detection calculations."""

    def __init__(self, params: RadarParameters, antenna: Antenna):
        self.params = params
        self.antenna = antenna

    def calculate_received_power(self, target: Vessel, own_x: float, own_y: float) -> float:
        """Calculate received signal power from a target using radar equation.

        Args:
            target: Target vessel
            own_x, own_y: Own ship position

        Returns:
            Relative signal strength (0-1)
        """
        # Calculate range
        dx = target.x - own_x
        dy = target.y - own_y
        range_m = math.sqrt(dx * dx + dy * dy)

        if range_m < 10:  # Minimum range
            return 0.0

        # Calculate bearing to target
        target_bearing = math.degrees(math.atan2(dx, dy)) % 360

        # Get antenna gain for this bearing
        antenna_gain = self.antenna.get_gain_for_target(target_bearing)

        if antenna_gain < 0.01:  # Target not in beam
            return 0.0

        # Simplified radar equation
        # P_r proportional to (P_t * G^2 * lambda^2 * RCS) / (R^4)

        # Normalize to max range
        max_range = self.params.max_range_m
        range_factor = (max_range / range_m) ** 4

        # RCS factor (normalized)
        rcs_factor = min(1.0, target.rcs / 1000.0)

        # Combine factors
        signal = antenna_gain * range_factor * rcs_factor * self.params.gain

        # Apply receiver sensitivity
        signal = min(1.0, signal)

        return signal

    def detect_targets(self, targets: List[Vessel], own_x: float, own_y: float,
                      current_time: float) -> List[Detection]:
        """Process all targets and return detections.

        Args:
            targets: List of potential targets
            own_x, own_y: Own ship position
            current_time: Current simulation time

        Returns:
            List of Detection objects
        """
        detections = []

        for target in targets:
            if not target.is_active:
                continue

            # Calculate range and bearing
            dx = target.x - own_x
            dy = target.y - own_y
            range_m = math.sqrt(dx * dx + dy * dy)
            bearing_deg = math.degrees(math.atan2(dx, dy)) % 360

            # Check if within radar range
            if range_m > self.params.max_range_m:
                continue

            # Calculate signal strength
            signal = self.calculate_received_power(target, own_x, own_y)

            if signal < 0.05:  # Detection threshold
                continue

            # Add measurement noise
            range_noise = random.gauss(0, self.params.range_resolution_m * 0.5)
            bearing_noise = random.gauss(0, self.params.horizontal_beamwidth_deg * 0.3)

            detection = Detection(
                range_m=range_m + range_noise,
                bearing_deg=(bearing_deg + bearing_noise) % 360,
                intensity=signal,
                vessel_id=target.id,
                timestamp=current_time
            )
            detections.append(detection)

        return detections

    def generate_sweep_data(self, targets: List[Vessel], own_x: float, own_y: float,
                           current_time: float, num_range_bins: int = 512) -> List[float]:
        """Generate radar return data for the current beam position.

        Args:
            targets: List of potential targets
            own_x, own_y: Own ship position
            current_time: Current simulation time
            num_range_bins: Number of range bins in the sweep

        Returns:
            List of intensities for each range bin
        """
        sweep_data = [0.0] * num_range_bins
        max_range = self.params.max_range_m
        bin_size = max_range / num_range_bins

        current_bearing = self.antenna.get_bearing()

        for target in targets:
            if not target.is_active:
                continue

            # Calculate range and bearing
            dx = target.x - own_x
            dy = target.y - own_y
            range_m = math.sqrt(dx * dx + dy * dy)
            bearing_deg = math.degrees(math.atan2(dx, dy)) % 360

            # Check if in beam
            bearing_diff = (bearing_deg - current_bearing + 180) % 360 - 180
            beam_gain = self.antenna.get_beam_pattern(bearing_diff)

            if beam_gain < 0.01 or range_m > max_range:
                continue

            # Calculate signal and range bin
            signal = self.calculate_received_power(target, own_x, own_y)
            range_bin = int(range_m / bin_size)

            if 0 <= range_bin < num_range_bins:
                # Spread signal across a few bins based on target size
                spread = max(1, int(target.length / bin_size))
                for i in range(-spread, spread + 1):
                    bin_idx = range_bin + i
                    if 0 <= bin_idx < num_range_bins:
                        # Reduce intensity for spread bins
                        spread_factor = 1.0 - abs(i) / (spread + 1)
                        sweep_data[bin_idx] = max(sweep_data[bin_idx],
                                                  signal * spread_factor)

        return sweep_data
