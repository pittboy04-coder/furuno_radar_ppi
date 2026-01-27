"""Scenario management for the radar simulator."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from ..objects.vessel import Vessel, VesselType
from ..environment.weather import WeatherConditions
from ..core.world import World
from ..radar.system import RadarSystem
from ..environment.weather import WeatherEffects

@dataclass
class VesselConfig:
    """Configuration for a vessel in a scenario."""
    id: str
    name: str
    vessel_type: VesselType
    x: float
    y: float
    course: float
    speed: float
    length: float = 50.0
    beam: float = 10.0
    height: float = 15.0

@dataclass
class Scenario:
    """A complete scenario configuration."""
    name: str
    description: str
    vessels: List[VesselConfig]
    weather: WeatherConditions = field(default_factory=WeatherConditions)
    radar_range_nm: float = 6.0
    own_ship_index: int = 0  # Index of own ship in vessels list

    def to_dict(self) -> Dict:
        """Convert scenario to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'vessels': [
                {
                    'id': v.id, 'name': v.name, 'type': v.vessel_type.value,
                    'x': v.x, 'y': v.y, 'course': v.course, 'speed': v.speed,
                    'length': v.length, 'beam': v.beam, 'height': v.height
                }
                for v in self.vessels
            ],
            'weather': {
                'sea_state': self.weather.sea_state,
                'wind_speed': self.weather.wind_speed_knots,
                'wind_direction': self.weather.wind_direction,
                'rain_rate': self.weather.rain_rate_mmh,
                'visibility': self.weather.visibility_nm
            },
            'radar_range_nm': self.radar_range_nm
        }


class ScenarioManager:
    """Manages loading and switching between scenarios."""

    def __init__(self):
        self.scenarios: Dict[str, Scenario] = {}
        self.current_scenario: Optional[str] = None
        self.on_scenario_loaded: Optional[Callable[[Scenario], None]] = None

    def register_scenario(self, scenario: Scenario) -> None:
        """Register a scenario."""
        self.scenarios[scenario.name] = scenario

    def register_scenarios(self, scenarios: List[Scenario]) -> None:
        """Register multiple scenarios."""
        for scenario in scenarios:
            self.register_scenario(scenario)

    def get_scenario(self, name: str) -> Optional[Scenario]:
        """Get a scenario by name."""
        return self.scenarios.get(name)

    def get_scenario_names(self) -> List[str]:
        """Get list of all scenario names."""
        return list(self.scenarios.keys())

    def load_scenario(self, name: str, world: World, radar: RadarSystem,
                     weather: WeatherEffects) -> bool:
        """Load a scenario into the simulation.

        Args:
            name: Scenario name
            world: World instance to populate
            radar: Radar system to configure
            weather: Weather effects to configure

        Returns:
            True if loaded successfully
        """
        scenario = self.scenarios.get(name)
        if not scenario:
            return False

        # Clear existing state
        world.clear()
        radar.clear_sweep_buffer()

        # Create vessels
        for i, config in enumerate(scenario.vessels):
            vessel = Vessel(
                id=config.id,
                name=config.name,
                vessel_type=config.vessel_type,
                x=config.x,
                y=config.y,
                course=config.course,
                speed=config.speed,
                length=config.length,
                beam=config.beam,
                height=config.height
            )

            # Mark own ship
            if i == scenario.own_ship_index:
                vessel.vessel_type = VesselType.OWN_SHIP

            world.add_vessel(vessel)

        # Set weather
        weather.set_conditions(scenario.weather)

        # Set radar range
        radar.set_range_scale(scenario.radar_range_nm)

        self.current_scenario = name

        # Callback
        if self.on_scenario_loaded:
            self.on_scenario_loaded(scenario)

        return True

    def get_current_scenario(self) -> Optional[Scenario]:
        """Get the currently loaded scenario."""
        if self.current_scenario:
            return self.scenarios.get(self.current_scenario)
        return None
