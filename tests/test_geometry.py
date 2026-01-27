"""Tests for geometry module."""
import pytest
import math
from radar_sim.core.range_bearing import (
    normalize_angle, deg_to_rad, rad_to_deg,
    calculate_range, calculate_bearing,
    polar_to_cartesian, cartesian_to_polar,
    calculate_cpa
)


class TestNormalizeAngle:
    def test_positive_angle(self):
        assert normalize_angle(45) == 45

    def test_negative_angle(self):
        assert normalize_angle(-45) == 315

    def test_large_angle(self):
        assert normalize_angle(720) == 0

    def test_zero(self):
        assert normalize_angle(0) == 0

    def test_360(self):
        assert normalize_angle(360) == 0


class TestDegRadConversion:
    def test_deg_to_rad(self):
        assert abs(deg_to_rad(180) - math.pi) < 1e-10

    def test_rad_to_deg(self):
        assert abs(rad_to_deg(math.pi) - 180) < 1e-10

    def test_round_trip(self):
        angle = 45
        assert abs(rad_to_deg(deg_to_rad(angle)) - angle) < 1e-10


class TestCalculateRange:
    def test_same_point(self):
        assert calculate_range(0, 0, 0, 0) == 0

    def test_horizontal(self):
        assert calculate_range(0, 0, 100, 0) == 100

    def test_vertical(self):
        assert calculate_range(0, 0, 0, 100) == 100

    def test_diagonal(self):
        assert abs(calculate_range(0, 0, 100, 100) - 141.421356) < 0.001


class TestCalculateBearing:
    def test_north(self):
        bearing = calculate_bearing(0, 0, 0, 100)
        assert abs(bearing - 0) < 0.001

    def test_east(self):
        bearing = calculate_bearing(0, 0, 100, 0)
        assert abs(bearing - 90) < 0.001

    def test_south(self):
        bearing = calculate_bearing(0, 0, 0, -100)
        assert abs(bearing - 180) < 0.001

    def test_west(self):
        bearing = calculate_bearing(0, 0, -100, 0)
        assert abs(bearing - 270) < 0.001


class TestPolarCartesian:
    def test_polar_to_cartesian_north(self):
        x, y = polar_to_cartesian(100, 0)
        assert abs(x) < 0.001
        assert abs(y - 100) < 0.001

    def test_polar_to_cartesian_east(self):
        x, y = polar_to_cartesian(100, 90)
        assert abs(x - 100) < 0.001
        assert abs(y) < 0.001

    def test_cartesian_to_polar(self):
        r, b = cartesian_to_polar(100, 0)
        assert abs(r - 100) < 0.001
        assert abs(b - 90) < 0.001

    def test_round_trip(self):
        original_range = 150
        original_bearing = 45
        x, y = polar_to_cartesian(original_range, original_bearing)
        r, b = cartesian_to_polar(x, y)
        assert abs(r - original_range) < 0.001
        assert abs(b - original_bearing) < 0.001


class TestCalculateCPA:
    def test_parallel_courses(self):
        # Two ships on parallel courses, same speed
        cpa, tcpa = calculate_cpa(0, 0, 0, 10, 1000, 0, 0, 10)
        assert abs(cpa - 1000) < 1  # CPA should be constant at 1000m

    def test_converging(self):
        # Ships converging
        cpa, tcpa = calculate_cpa(0, 0, 45, 10, 2000, 0, 225, 10)
        assert tcpa > 0  # Should be in the future
        assert cpa < 2000  # Should get closer

    def test_diverging(self):
        # Ships diverging
        cpa, tcpa = calculate_cpa(0, 0, 180, 10, 0, 1000, 0, 10)
        assert tcpa < 0  # CPA in the past
