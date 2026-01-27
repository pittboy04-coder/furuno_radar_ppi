"""Tests for vessel module."""
import pytest
import math
from radar_sim.objects.vessel import Vessel, VesselType


class TestVessel:
    def test_create_vessel(self):
        vessel = Vessel(id="test", name="Test Ship")
        assert vessel.id == "test"
        assert vessel.name == "Test Ship"
        assert vessel.vessel_type == VesselType.UNKNOWN

    def test_vessel_type(self):
        vessel = Vessel(id="own", vessel_type=VesselType.OWN_SHIP)
        assert vessel.vessel_type == VesselType.OWN_SHIP

    def test_initial_position(self):
        vessel = Vessel(id="test", x=100, y=200)
        assert vessel.x == 100
        assert vessel.y == 200

    def test_set_position(self):
        vessel = Vessel(id="test")
        vessel.set_position(500, 600)
        assert vessel.x == 500
        assert vessel.y == 600

    def test_set_motion(self):
        vessel = Vessel(id="test")
        vessel.set_motion(90, 15)
        assert vessel.course == 90
        assert vessel.speed == 15

    def test_course_normalization(self):
        vessel = Vessel(id="test")
        vessel.set_motion(450, 10)
        assert vessel.course == 90

    def test_negative_speed(self):
        vessel = Vessel(id="test")
        vessel.set_motion(0, -10)
        assert vessel.speed == 0

    def test_update_position_north(self):
        vessel = Vessel(id="test", x=0, y=0, course=0, speed=10)
        dt = 1.0  # 1 second
        vessel.update(dt)
        # Speed is 10 knots = 5.14444 m/s, heading north
        assert abs(vessel.x) < 0.001  # No east/west movement
        assert vessel.y > 5  # Moved north

    def test_update_position_east(self):
        vessel = Vessel(id="test", x=0, y=0, course=90, speed=10)
        dt = 1.0
        vessel.update(dt)
        assert vessel.x > 5  # Moved east
        assert abs(vessel.y) < 0.001  # No north/south movement

    def test_distance_to(self):
        v1 = Vessel(id="v1", x=0, y=0)
        v2 = Vessel(id="v2", x=100, y=0)
        assert abs(v1.distance_to(v2) - 100) < 0.001

    def test_bearing_to(self):
        v1 = Vessel(id="v1", x=0, y=0)
        v2 = Vessel(id="v2", x=0, y=100)
        assert abs(v1.bearing_to(v2) - 0) < 0.001  # North

    def test_get_velocity(self):
        vessel = Vessel(id="test", course=0, speed=10)
        vx, vy = vessel.get_velocity()
        # At heading 0 (north), vx should be ~0, vy should be positive
        assert abs(vx) < 0.001
        assert vy > 5

    def test_rcs_estimation(self):
        small_boat = Vessel(id="small", length=10, beam=3, height=5)
        large_ship = Vessel(id="large", length=200, beam=30, height=25)
        assert small_boat.rcs < large_ship.rcs

    def test_inactive_vessel_no_update(self):
        vessel = Vessel(id="test", x=0, y=0, course=0, speed=10, is_active=False)
        vessel.update(1.0)
        assert vessel.x == 0
        assert vessel.y == 0
