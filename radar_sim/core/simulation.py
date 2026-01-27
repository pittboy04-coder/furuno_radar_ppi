"""Main simulation engine."""
import time
from typing import Optional, Callable, List
from .world import World
from ..radar.system import RadarSystem
from ..environment.weather import WeatherEffects, WeatherConditions
from ..environment.coastline import Coastline, create_harbor_coastline, create_island_coastline
from ..data_export import RadarDataExporter

class Simulation:
    """Main simulation controller."""

    def __init__(self):
        self.world = World()
        self.radar = RadarSystem()
        self.weather = WeatherEffects()

        # Coastline/landmass
        self.coastlines: List[Coastline] = []
        self.coastline_enabled = False

        # Data export
        self.exporter = RadarDataExporter()

        # Timing
        self.time_scale = 1.0  # 1.0 = real-time
        self.target_fps = 60
        self.dt = 1.0 / self.target_fps

        # State
        self.is_running = False
        self.is_paused = False
        self.frame_count = 0

        # Callbacks
        self.on_update: Optional[Callable[[float], None]] = None

    def add_coastline(self, coastline: Coastline) -> None:
        """Add a coastline to the simulation."""
        self.coastlines.append(coastline)
        self.coastline_enabled = True

    def clear_coastlines(self) -> None:
        """Remove all coastlines."""
        self.coastlines.clear()
        self.coastline_enabled = False

    def setup_harbor_coastline(self) -> None:
        """Set up a default harbor coastline ahead of own ship."""
        self.clear_coastlines()

        # Main harbor coastline
        harbor = create_harbor_coastline(
            center_x=0,
            center_y=8000,  # 8km ahead
            width=12000,    # 12km wide
            depth=3000      # 3km deep harbor
        )
        self.add_coastline(harbor)

        # Add a small island to the side
        island = create_island_coastline(
            center_x=4000,  # 4km to starboard
            center_y=5000,  # 5km ahead
            radius=500,     # 500m radius
            num_points=16
        )
        self.add_coastline(island)

    def setup_default_scenario(self) -> None:
        """Set up a default scenario with own ship and some targets."""
        from ..objects.vessel import Vessel, VesselType

        # Own ship at origin
        own_ship = Vessel(
            id="own_ship",
            name="Own Ship",
            vessel_type=VesselType.OWN_SHIP,
            x=0, y=0,
            course=0, speed=10,
            length=100, beam=15, height=20
        )
        self.world.add_vessel(own_ship)

        # Add some targets
        targets = [
            Vessel(id="target_1", name="Cargo Ship", vessel_type=VesselType.CARGO,
                  x=3000, y=5000, course=225, speed=12, length=150, beam=20, height=25),
            Vessel(id="target_2", name="Tanker", vessel_type=VesselType.TANKER,
                  x=-4000, y=3000, course=90, speed=8, length=200, beam=30, height=20),
            Vessel(id="target_3", name="Fishing Boat", vessel_type=VesselType.FISHING,
                  x=2000, y=-2000, course=315, speed=6, length=25, beam=6, height=8),
            Vessel(id="target_4", name="Sailing Yacht", vessel_type=VesselType.SAILING,
                  x=-1500, y=-4000, course=45, speed=5, length=15, beam=4, height=15),
        ]

        for target in targets:
            self.world.add_vessel(target)

        # Set default weather
        self.weather.set_conditions(WeatherConditions(
            sea_state=3,
            wind_speed_knots=15,
            wind_direction=45,
            rain_rate_mmh=0,
            visibility_nm=10
        ))

    def update(self, dt: float = None) -> None:
        """Update simulation by one time step.

        Args:
            dt: Time step in seconds (uses default if not specified)
        """
        if self.is_paused:
            return

        dt = dt or self.dt
        scaled_dt = dt * self.time_scale

        # Update world (vessel positions)
        self.world.update(scaled_dt)

        # Update radar system
        self.radar.update(self.world, scaled_dt)

        self.frame_count += 1

        # Callback
        if self.on_update:
            self.on_update(scaled_dt)

    def get_radar_sweep_data(self, bearing: float, record: bool = True) -> list:
        """Get radar sweep data for visualization.

        Args:
            bearing: Bearing to get data for
            record: Whether to record this sweep for export

        Returns:
            List of intensities for each range bin
        """
        # Get raw sweep data from targets
        sweep_data = self.radar.get_sweep_at_bearing(bearing)

        # Add coastline returns
        if self.coastline_enabled and self.world.own_ship:
            own_x = self.world.own_ship.x
            own_y = self.world.own_ship.y

            for coastline in self.coastlines:
                coast_returns = coastline.generate_returns(
                    own_x, own_y,
                    bearing,
                    self.radar.params.horizontal_beamwidth_deg,
                    self.radar.params.max_range_m,
                    len(sweep_data)
                )
                # Merge coastline returns (take max)
                for i, val in enumerate(coast_returns):
                    sweep_data[i] = max(sweep_data[i], val * self.radar.params.gain)

        # Apply weather effects
        if self.world.own_ship:
            sweep_data = self.weather.apply_to_sweep(
                sweep_data,
                bearing,
                self.radar.params.max_range_m,
                self.radar.params.sea_clutter,
                self.radar.params.rain_clutter
            )

        # Record for export if enabled
        if record and self.exporter.is_active():
            self.exporter.add_sweep(
                timestamp=self.world.time,
                bearing_deg=bearing,
                range_scale_nm=self.radar.params.current_range_nm,
                gain=self.radar.params.gain,
                sea_clutter=self.radar.params.sea_clutter,
                rain_clutter=self.radar.params.rain_clutter,
                echo_values=sweep_data
            )

        return sweep_data

    def start_recording(self) -> str:
        """Start recording radar data for export."""
        return self.exporter.start_recording()

    def stop_recording(self) -> str:
        """Stop recording and save to CSV file."""
        return self.exporter.stop_recording()

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.exporter.is_active()

    def get_record_count(self) -> int:
        """Get number of recorded sweeps."""
        return self.exporter.get_record_count()

    def export_current_sweep(self, bearing: float) -> str:
        """Export current sweep data to a single CSV file."""
        sweep_data = self.get_radar_sweep_data(bearing, record=False)
        return self.exporter.export_single_sweep(
            timestamp=self.world.time,
            bearing_deg=bearing,
            range_scale_nm=self.radar.params.current_range_nm,
            gain=self.radar.params.gain,
            sea_clutter=self.radar.params.sea_clutter,
            rain_clutter=self.radar.params.rain_clutter,
            echo_values=sweep_data
        )

    def set_time_scale(self, scale: float) -> None:
        """Set simulation time scale."""
        self.time_scale = max(0.1, min(10.0, scale))

    def pause(self) -> None:
        """Pause simulation."""
        self.is_paused = True

    def resume(self) -> None:
        """Resume simulation."""
        self.is_paused = False

    def toggle_pause(self) -> bool:
        """Toggle pause state."""
        self.is_paused = not self.is_paused
        return self.is_paused

    def reset(self) -> None:
        """Reset simulation to initial state."""
        self.world.clear()
        self.radar.clear_sweep_buffer()
        self.clear_coastlines()
        self.frame_count = 0
        self.is_paused = False
        # Stop any active recording
        if self.exporter.is_active():
            self.exporter.stop_recording()
