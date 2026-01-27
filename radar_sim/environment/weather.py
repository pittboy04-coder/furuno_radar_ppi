"""Weather effects for radar simulation."""
from dataclasses import dataclass
from typing import List
from .noise import NoiseGenerator
from .clutter import SeaClutter, RainClutter

@dataclass
class WeatherConditions:
    """Current weather conditions."""
    sea_state: int = 3  # 0-9 Douglas scale
    wind_speed_knots: float = 10.0
    wind_direction: float = 0.0  # degrees
    rain_rate_mmh: float = 0.0
    visibility_nm: float = 10.0

class WeatherEffects:
    """Combines all weather-related effects on radar."""

    def __init__(self):
        self.conditions = WeatherConditions()
        self.noise_gen = NoiseGenerator()
        self.sea_clutter = SeaClutter()
        self.rain_clutter = RainClutter()

    def set_conditions(self, conditions: WeatherConditions) -> None:
        """Set weather conditions."""
        self.conditions = conditions
        self.sea_clutter.set_sea_state(conditions.sea_state)
        self.sea_clutter.set_wind(conditions.wind_direction)
        self.rain_clutter.set_rain_rate(conditions.rain_rate_mmh)

    def set_sea_state(self, state: int) -> None:
        """Set sea state."""
        self.conditions.sea_state = state
        self.sea_clutter.set_sea_state(state)

    def set_wind(self, direction: float, speed_knots: float) -> None:
        """Set wind conditions."""
        self.conditions.wind_direction = direction
        self.conditions.wind_speed_knots = speed_knots
        self.sea_clutter.set_wind(direction, speed_knots)

    def set_rain(self, rate_mmh: float) -> None:
        """Set rain rate."""
        self.conditions.rain_rate_mmh = rate_mmh
        self.rain_clutter.set_rain_rate(rate_mmh)

    def apply_to_sweep(self, sweep_data: List[float], bearing: float,
                      max_range_m: float, sea_suppression: float = 0.0,
                      rain_suppression: float = 0.0) -> List[float]:
        """Apply all weather effects to sweep data.

        Args:
            sweep_data: Original radar returns
            bearing: Current antenna bearing
            max_range_m: Maximum range
            sea_suppression: Sea clutter suppression (0-1)
            rain_suppression: Rain clutter suppression (0-1)

        Returns:
            Modified sweep data with weather effects
        """
        num_bins = len(sweep_data)

        # Generate clutter
        sea = self.sea_clutter.generate_clutter(
            num_bins, bearing, max_range_m, sea_suppression
        )
        rain = self.rain_clutter.generate_clutter(
            num_bins, bearing, max_range_m, rain_suppression
        )

        # Combine: targets + clutter + noise
        result = []
        for i, val in enumerate(sweep_data):
            combined = max(val, sea[i], rain[i])  # Use max for display
            result.append(combined)

        # Add noise
        result = self.noise_gen.add_noise_to_sweep(result)

        return result

    def get_attenuation_factor(self, range_m: float) -> float:
        """Calculate atmospheric attenuation based on weather.

        Args:
            range_m: Range in meters

        Returns:
            Attenuation factor (0-1, 1 = no attenuation)
        """
        # Rain attenuation (significant at X-band)
        rain_atten_db_per_km = 0.01 * self.conditions.rain_rate_mmh

        # Convert range to km
        range_km = range_m / 1000.0

        # Total attenuation
        total_atten_db = rain_atten_db_per_km * range_km * 2  # Two-way path

        # Convert to linear
        return 10 ** (-total_atten_db / 10)
