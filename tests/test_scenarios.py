"""Tests for scenario module."""
import pytest
from radar_sim.scenarios.scenario_manager import ScenarioManager, Scenario, VesselConfig
from radar_sim.scenarios.presets import PRESET_SCENARIOS
from radar_sim.objects.vessel import VesselType
from radar_sim.core.world import World
from radar_sim.radar.system import RadarSystem
from radar_sim.environment.weather import WeatherEffects, WeatherConditions


class TestScenarioManager:
    def test_register_scenario(self):
        manager = ScenarioManager()
        scenario = Scenario(
            name="Test",
            description="Test scenario",
            vessels=[
                VesselConfig(id="own", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
                            x=0, y=0, course=0, speed=10)
            ]
        )
        manager.register_scenario(scenario)
        assert "Test" in manager.get_scenario_names()

    def test_get_scenario(self):
        manager = ScenarioManager()
        scenario = Scenario(name="Test", description="Test", vessels=[])
        manager.register_scenario(scenario)
        retrieved = manager.get_scenario("Test")
        assert retrieved == scenario

    def test_get_nonexistent(self):
        manager = ScenarioManager()
        assert manager.get_scenario("NonExistent") is None

    def test_load_scenario(self):
        manager = ScenarioManager()
        scenario = Scenario(
            name="Test",
            description="Test scenario",
            vessels=[
                VesselConfig(id="own", name="Own Ship", vessel_type=VesselType.OWN_SHIP,
                            x=0, y=0, course=0, speed=10),
                VesselConfig(id="target", name="Target", vessel_type=VesselType.CARGO,
                            x=1000, y=1000, course=180, speed=12)
            ],
            radar_range_nm=12.0
        )
        manager.register_scenario(scenario)

        world = World()
        radar = RadarSystem()
        weather = WeatherEffects()

        success = manager.load_scenario("Test", world, radar, weather)
        assert success
        assert len(world.vessels) == 2
        assert world.own_ship is not None
        assert radar.params.current_range_nm == 12.0

    def test_load_nonexistent_scenario(self):
        manager = ScenarioManager()
        world = World()
        radar = RadarSystem()
        weather = WeatherEffects()

        success = manager.load_scenario("NonExistent", world, radar, weather)
        assert not success


class TestPresetScenarios:
    def test_presets_exist(self):
        assert len(PRESET_SCENARIOS) > 0

    def test_presets_have_vessels(self):
        for scenario in PRESET_SCENARIOS:
            assert len(scenario.vessels) > 0

    def test_presets_have_own_ship(self):
        for scenario in PRESET_SCENARIOS:
            own_ship_configs = [v for v in scenario.vessels
                               if v.vessel_type == VesselType.OWN_SHIP]
            # Own ship is set by index, not by type in config
            assert scenario.own_ship_index < len(scenario.vessels)

    def test_presets_load(self):
        manager = ScenarioManager()
        manager.register_scenarios(PRESET_SCENARIOS)

        for scenario in PRESET_SCENARIOS:
            world = World()
            radar = RadarSystem()
            weather = WeatherEffects()

            success = manager.load_scenario(scenario.name, world, radar, weather)
            assert success, f"Failed to load scenario: {scenario.name}"
            assert world.own_ship is not None, f"No own ship in: {scenario.name}"

    def test_scenario_names(self):
        expected_names = ["Calm Traffic", "Busy Channel", "Close Quarters",
                        "Storm Conditions", "Coastal Navigation", "Night Passage"]
        actual_names = [s.name for s in PRESET_SCENARIOS]
        for name in expected_names:
            assert name in actual_names
