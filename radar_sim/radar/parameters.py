"""Radar system parameters based on Furuno marine radar specifications."""
from dataclasses import dataclass
from enum import Enum
from typing import List

class RadarBand(Enum):
    X_BAND = "X"  # 9.3-9.5 GHz
    S_BAND = "S"  # 2.9-3.1 GHz

@dataclass
class RadarParameters:
    """Configuration parameters for the radar system."""

    # Radar identification
    name: str = "Furuno FAR-2xx7"
    band: RadarBand = RadarBand.X_BAND

    # Transmitter
    peak_power_kw: float = 25.0  # Peak transmit power in kW
    frequency_ghz: float = 9.41  # Operating frequency
    pulse_lengths_us: List[float] = None  # Available pulse lengths
    prf_hz: float = 3000  # Pulse repetition frequency

    # Antenna
    antenna_gain_db: float = 28.0
    horizontal_beamwidth_deg: float = 1.2
    vertical_beamwidth_deg: float = 22.0
    rotation_rpm: float = 24.0  # Antenna rotation speed
    antenna_height_m: float = 15.0  # Height above sea level

    # Receiver
    noise_figure_db: float = 5.0
    min_detectable_signal_dbm: float = -100.0

    # Range settings
    range_scales_nm: List[float] = None  # Available range scales
    current_range_nm: float = 6.0  # Currently selected range

    # Processing
    gain: float = 0.5  # 0-1, receiver gain
    sea_clutter: float = 0.3  # 0-1, sea clutter suppression
    rain_clutter: float = 0.3  # 0-1, rain clutter suppression
    interference_rejection: bool = True

    def __post_init__(self):
        if self.pulse_lengths_us is None:
            self.pulse_lengths_us = [0.07, 0.15, 0.5, 0.8, 1.2]
        if self.range_scales_nm is None:
            self.range_scales_nm = [0.25, 0.5, 0.75, 1.5, 3, 6, 12, 24, 48, 96]

    @property
    def rotation_period_s(self) -> float:
        """Time for one complete antenna rotation in seconds."""
        return 60.0 / self.rotation_rpm

    @property
    def range_resolution_m(self) -> float:
        """Range resolution based on pulse length."""
        # Using shortest pulse for best resolution
        pulse_s = min(self.pulse_lengths_us) * 1e-6
        c = 299792458  # Speed of light
        return c * pulse_s / 2

    @property
    def max_range_m(self) -> float:
        """Maximum range in meters based on current scale."""
        return self.current_range_nm * 1852  # nm to meters

    def set_range_scale(self, range_nm: float) -> None:
        """Set the range scale to the nearest available value."""
        closest = min(self.range_scales_nm, key=lambda x: abs(x - range_nm))
        self.current_range_nm = closest
