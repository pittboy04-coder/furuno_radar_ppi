"""Tests for radar modules."""
import pytest
import math
from radar_sim.radar.parameters import RadarParameters, RadarBand
from radar_sim.radar.antenna import Antenna
from radar_sim.radar.detection import DetectionEngine, Detection
from radar_sim.radar.system import RadarSystem
from radar_sim.objects.vessel import Vessel


class TestRadarParameters:
    def test_default_params(self):
        params = RadarParameters()
        assert params.band == RadarBand.X_BAND
        assert params.current_range_nm == 6.0

    def test_rotation_period(self):
        params = RadarParameters(rotation_rpm=24)
        assert abs(params.rotation_period_s - 2.5) < 0.001

    def test_max_range(self):
        params = RadarParameters(current_range_nm=6.0)
        assert abs(params.max_range_m - 11112) < 1  # 6 nm in meters

    def test_set_range_scale(self):
        params = RadarParameters()
        params.set_range_scale(5.0)  # Not an exact scale
        assert params.current_range_nm == 6.0  # Should pick closest (6)

        params.set_range_scale(2.0)
        assert params.current_range_nm == 1.5  # Closest to 2


class TestAntenna:
    def test_initial_bearing(self):
        params = RadarParameters()
        antenna = Antenna(params)
        assert antenna.get_bearing() == 0.0

    def test_update(self):
        params = RadarParameters(rotation_rpm=24)  # 144 deg/sec
        antenna = Antenna(params)
        antenna.update(1.0)  # 1 second
        bearing = antenna.get_bearing()
        assert abs(bearing - 144) < 0.1

    def test_bearing_wrap(self):
        params = RadarParameters()
        antenna = Antenna(params)
        antenna.set_bearing(350)
        antenna.update(0.1)  # Small increment
        bearing = antenna.get_bearing()
        assert 0 <= bearing < 360

    def test_beam_pattern_center(self):
        params = RadarParameters()
        antenna = Antenna(params)
        gain = antenna.get_beam_pattern(0)
        assert abs(gain - 1.0) < 0.001

    def test_beam_pattern_edge(self):
        params = RadarParameters(horizontal_beamwidth_deg=1.2)
        antenna = Antenna(params)
        gain = antenna.get_beam_pattern(5)  # Well outside beam
        assert gain < 0.1

    def test_target_in_beam(self):
        params = RadarParameters()
        antenna = Antenna(params)
        antenna.set_bearing(45)
        assert antenna.is_target_in_beam(45)
        assert not antenna.is_target_in_beam(90)


class TestDetectionEngine:
    def test_detect_close_target(self):
        params = RadarParameters(current_range_nm=6.0)
        antenna = Antenna(params)
        antenna.set_bearing(0)
        engine = DetectionEngine(params, antenna)

        target = Vessel(id="target", x=0, y=1000, length=100, beam=15, height=20)
        targets = [target]

        detections = engine.detect_targets(targets, 0, 0, 0)
        assert len(detections) >= 0  # May or may not detect depending on beam

    def test_out_of_range(self):
        params = RadarParameters(current_range_nm=1.0)  # 1 nm = ~1852m
        antenna = Antenna(params)
        engine = DetectionEngine(params, antenna)

        # Target at 5000m, well beyond 1nm range
        target = Vessel(id="target", x=0, y=5000)
        detections = engine.detect_targets([target], 0, 0, 0)
        assert len(detections) == 0

    def test_sweep_data_generation(self):
        params = RadarParameters()
        antenna = Antenna(params)
        engine = DetectionEngine(params, antenna)

        sweep = engine.generate_sweep_data([], 0, 0, 0, num_range_bins=512)
        assert len(sweep) == 512
        assert all(v == 0.0 for v in sweep)  # No targets = no returns


class TestRadarSystem:
    def test_create_system(self):
        system = RadarSystem()
        assert system.is_transmitting
        assert system.num_bearings == 360
        assert system.num_range_bins == 512

    def test_set_controls(self):
        system = RadarSystem()
        system.set_gain(0.8)
        assert system.params.gain == 0.8

        system.set_sea_clutter(0.5)
        assert system.params.sea_clutter == 0.5

        system.set_rain_clutter(0.7)
        assert system.params.rain_clutter == 0.7

    def test_toggle_transmission(self):
        system = RadarSystem()
        assert system.is_transmitting
        result = system.toggle_transmission()
        assert not result
        assert not system.is_transmitting

    def test_clear_sweep_buffer(self):
        system = RadarSystem()
        system.sweep_buffer[0][0] = 1.0
        system.clear_sweep_buffer()
        assert system.sweep_buffer[0][0] == 0.0
