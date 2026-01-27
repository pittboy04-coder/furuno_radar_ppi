"""Preset scenarios for the radar simulator."""
from .scenario_manager import Scenario, VesselConfig
from ..objects.vessel import VesselType
from ..environment.weather import WeatherConditions

# Calm day with light traffic
CALM_TRAFFIC = Scenario(
    name="Calm Traffic",
    description="Light traffic on a calm day. Good for learning basic radar operation.",
    vessels=[
        VesselConfig(
            id="own_ship", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
            x=0, y=0, course=0, speed=12,
            length=100, beam=15, height=20
        ),
        VesselConfig(
            id="cargo_1", name="MV Pacific Star", vessel_type=VesselType.CARGO,
            x=3000, y=5000, course=225, speed=14,
            length=180, beam=25, height=30
        ),
        VesselConfig(
            id="tanker_1", name="MT Ocean Pride", vessel_type=VesselType.TANKER,
            x=-4000, y=6000, course=135, speed=10,
            length=250, beam=40, height=25
        ),
        VesselConfig(
            id="fishing_1", name="FV Morning Catch", vessel_type=VesselType.FISHING,
            x=2000, y=-3000, course=45, speed=6,
            length=25, beam=7, height=8
        ),
    ],
    weather=WeatherConditions(sea_state=2, wind_speed_knots=10, wind_direction=45),
    radar_range_nm=6.0
)

# Busy shipping lane
BUSY_CHANNEL = Scenario(
    name="Busy Channel",
    description="Heavy traffic in a busy shipping channel. Practice target tracking.",
    vessels=[
        VesselConfig(
            id="own_ship", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
            x=0, y=0, course=90, speed=15,
            length=120, beam=18, height=22
        ),
        VesselConfig(
            id="cargo_1", name="MV Atlantic Trader", vessel_type=VesselType.CARGO,
            x=2000, y=1000, course=270, speed=16,
            length=200, beam=30, height=35
        ),
        VesselConfig(
            id="cargo_2", name="MV Northern Star", vessel_type=VesselType.CARGO,
            x=-1500, y=2000, course=90, speed=14,
            length=175, beam=25, height=28
        ),
        VesselConfig(
            id="tanker_1", name="MT Crude Carrier", vessel_type=VesselType.TANKER,
            x=3500, y=-500, course=260, speed=12,
            length=300, beam=50, height=30
        ),
        VesselConfig(
            id="container_1", name="MV Box Express", vessel_type=VesselType.CARGO,
            x=-3000, y=-1500, course=75, speed=18,
            length=350, beam=45, height=50
        ),
        VesselConfig(
            id="tug_1", name="Harbour Tug 5", vessel_type=VesselType.TUG,
            x=500, y=800, course=180, speed=8,
            length=30, beam=10, height=12
        ),
        VesselConfig(
            id="pilot_1", name="Pilot Boat", vessel_type=VesselType.PILOT,
            x=-800, y=-400, course=0, speed=20,
            length=15, beam=5, height=6
        ),
    ],
    weather=WeatherConditions(sea_state=3, wind_speed_knots=15, wind_direction=180),
    radar_range_nm=6.0
)

# Close quarters situation
CLOSE_QUARTERS = Scenario(
    name="Close Quarters",
    description="Multiple vessels in close proximity. Practice collision avoidance.",
    vessels=[
        VesselConfig(
            id="own_ship", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
            x=0, y=0, course=45, speed=10,
            length=80, beam=12, height=15
        ),
        VesselConfig(
            id="crossing_1", name="MV Crossing Ship", vessel_type=VesselType.CARGO,
            x=1500, y=-500, course=315, speed=12,
            length=150, beam=22, height=25
        ),
        VesselConfig(
            id="overtaking_1", name="MV Fast Cargo", vessel_type=VesselType.CARGO,
            x=-200, y=-800, course=40, speed=16,
            length=180, beam=25, height=30
        ),
        VesselConfig(
            id="head_on_1", name="MV Oncoming", vessel_type=VesselType.CARGO,
            x=300, y=2000, course=225, speed=14,
            length=160, beam=23, height=28
        ),
    ],
    weather=WeatherConditions(sea_state=2, wind_speed_knots=8, wind_direction=90),
    radar_range_nm=3.0
)

# Rough weather
STORM_CONDITIONS = Scenario(
    name="Storm Conditions",
    description="Heavy weather with rain and high seas. Practice clutter rejection.",
    vessels=[
        VesselConfig(
            id="own_ship", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
            x=0, y=0, course=180, speed=8,
            length=100, beam=15, height=20
        ),
        VesselConfig(
            id="cargo_1", name="MV Weather Rider", vessel_type=VesselType.CARGO,
            x=-2000, y=3000, course=90, speed=10,
            length=200, beam=30, height=35
        ),
        VesselConfig(
            id="tanker_1", name="MT Storm Runner", vessel_type=VesselType.TANKER,
            x=4000, y=1000, course=270, speed=8,
            length=250, beam=40, height=28
        ),
    ],
    weather=WeatherConditions(
        sea_state=6,
        wind_speed_knots=35,
        wind_direction=225,
        rain_rate_mmh=25,
        visibility_nm=2
    ),
    radar_range_nm=6.0
)

# Coastal navigation with small targets
COASTAL_NAVIGATION = Scenario(
    name="Coastal Navigation",
    description="Coastal waters with buoys and small craft. Practice small target detection.",
    vessels=[
        VesselConfig(
            id="own_ship", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
            x=0, y=0, course=315, speed=10,
            length=60, beam=10, height=12
        ),
        VesselConfig(
            id="buoy_1", name="Fairway Buoy", vessel_type=VesselType.BUOY,
            x=1000, y=1500, course=0, speed=0,
            length=3, beam=3, height=4
        ),
        VesselConfig(
            id="buoy_2", name="Channel Marker", vessel_type=VesselType.BUOY,
            x=-800, y=2000, course=0, speed=0,
            length=2, beam=2, height=3
        ),
        VesselConfig(
            id="buoy_3", name="Hazard Buoy", vessel_type=VesselType.BUOY,
            x=500, y=3000, course=0, speed=0,
            length=3, beam=3, height=5
        ),
        VesselConfig(
            id="sailing_1", name="SY Wind Dancer", vessel_type=VesselType.SAILING,
            x=-1500, y=1000, course=60, speed=6,
            length=12, beam=4, height=18
        ),
        VesselConfig(
            id="sailing_2", name="SY Sea Breeze", vessel_type=VesselType.SAILING,
            x=2000, y=-500, course=300, speed=5,
            length=10, beam=3, height=15
        ),
        VesselConfig(
            id="fishing_1", name="FV Local Fisher", vessel_type=VesselType.FISHING,
            x=-500, y=-1500, course=180, speed=4,
            length=15, beam=5, height=6
        ),
        VesselConfig(
            id="fishing_2", name="FV Day Catch", vessel_type=VesselType.FISHING,
            x=1200, y=-2000, course=45, speed=5,
            length=18, beam=6, height=7
        ),
    ],
    weather=WeatherConditions(sea_state=2, wind_speed_knots=12, wind_direction=270),
    radar_range_nm=3.0
)

# Night navigation - same as calm but implies different conditions
NIGHT_PASSAGE = Scenario(
    name="Night Passage",
    description="Night navigation with multiple targets. Radar is primary navigation aid.",
    vessels=[
        VesselConfig(
            id="own_ship", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
            x=0, y=0, course=270, speed=14,
            length=110, beam=16, height=22
        ),
        VesselConfig(
            id="cargo_1", name="MV Night Hawk", vessel_type=VesselType.CARGO,
            x=5000, y=2000, course=180, speed=16,
            length=200, beam=28, height=32
        ),
        VesselConfig(
            id="passenger_1", name="MV Island Ferry", vessel_type=VesselType.PASSENGER,
            x=-3000, y=4000, course=135, speed=18,
            length=150, beam=25, height=35
        ),
        VesselConfig(
            id="fishing_1", name="FV Night Fisher", vessel_type=VesselType.FISHING,
            x=2000, y=-3000, course=0, speed=3,
            length=20, beam=6, height=7
        ),
        VesselConfig(
            id="sailing_1", name="SY Starlight", vessel_type=VesselType.SAILING,
            x=-1000, y=-2000, course=90, speed=4,
            length=14, beam=4, height=16
        ),
    ],
    weather=WeatherConditions(sea_state=3, wind_speed_knots=15, wind_direction=315,
                             visibility_nm=5),
    radar_range_nm=12.0
)

# Harbor approach with coastline - uses coastline flag
HARBOR_APPROACH = Scenario(
    name="Harbor Approach",
    description="Approaching harbor with coastline, buoys, and traffic. Coastline radar returns enabled.",
    vessels=[
        VesselConfig(
            id="own_ship", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
            x=0, y=0, course=0, speed=8,
            length=80, beam=12, height=15
        ),
        # Channel buoys
        VesselConfig(
            id="buoy_1", name="Port Entry Buoy", vessel_type=VesselType.BUOY,
            x=-500, y=3000, course=0, speed=0,
            length=3, beam=3, height=5
        ),
        VesselConfig(
            id="buoy_2", name="Starboard Entry Buoy", vessel_type=VesselType.BUOY,
            x=500, y=3000, course=0, speed=0,
            length=3, beam=3, height=5
        ),
        VesselConfig(
            id="buoy_3", name="Channel Marker 1", vessel_type=VesselType.BUOY,
            x=-400, y=5000, course=0, speed=0,
            length=2, beam=2, height=4
        ),
        VesselConfig(
            id="buoy_4", name="Channel Marker 2", vessel_type=VesselType.BUOY,
            x=400, y=5000, course=0, speed=0,
            length=2, beam=2, height=4
        ),
        # Traffic
        VesselConfig(
            id="ferry_1", name="Harbor Ferry", vessel_type=VesselType.PASSENGER,
            x=-1500, y=4000, course=90, speed=12,
            length=60, beam=15, height=18
        ),
        VesselConfig(
            id="tug_1", name="Harbor Tug", vessel_type=VesselType.TUG,
            x=800, y=6000, course=180, speed=6,
            length=25, beam=8, height=10
        ),
        VesselConfig(
            id="fishing_1", name="FV Local", vessel_type=VesselType.FISHING,
            x=-2000, y=2000, course=45, speed=5,
            length=15, beam=5, height=6
        ),
        VesselConfig(
            id="sailing_1", name="SY Wanderer", vessel_type=VesselType.SAILING,
            x=2500, y=1500, course=270, speed=4,
            length=12, beam=4, height=15
        ),
    ],
    weather=WeatherConditions(sea_state=2, wind_speed_knots=10, wind_direction=180),
    radar_range_nm=6.0
)

# Collection of all presets
PRESET_SCENARIOS = [
    CALM_TRAFFIC,
    BUSY_CHANNEL,
    CLOSE_QUARTERS,
    STORM_CONDITIONS,
    COASTAL_NAVIGATION,
    NIGHT_PASSAGE,
    HARBOR_APPROACH,
]
