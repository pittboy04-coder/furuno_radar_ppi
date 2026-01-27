"""Tests for world module."""
import pytest
from radar_sim.core.world import World
from radar_sim.objects.vessel import Vessel, VesselType


class TestWorld:
    def test_create_world(self):
        world = World()
        assert len(world.vessels) == 0
        assert world.own_ship is None
        assert world.time == 0.0

    def test_add_vessel(self):
        world = World()
        vessel = Vessel(id="test", name="Test Ship")
        world.add_vessel(vessel)
        assert len(world.vessels) == 1
        assert world.get_vessel("test") == vessel

    def test_add_own_ship(self):
        world = World()
        own = Vessel(id="own", vessel_type=VesselType.OWN_SHIP)
        world.add_vessel(own)
        assert world.own_ship == own

    def test_remove_vessel(self):
        world = World()
        vessel = Vessel(id="test")
        world.add_vessel(vessel)
        removed = world.remove_vessel("test")
        assert removed == vessel
        assert len(world.vessels) == 0

    def test_remove_nonexistent(self):
        world = World()
        result = world.remove_vessel("nonexistent")
        assert result is None

    def test_get_all_vessels(self):
        world = World()
        v1 = Vessel(id="v1")
        v2 = Vessel(id="v2")
        world.add_vessel(v1)
        world.add_vessel(v2)
        all_vessels = world.get_all_vessels()
        assert len(all_vessels) == 2
        assert v1 in all_vessels
        assert v2 in all_vessels

    def test_get_targets(self):
        world = World()
        own = Vessel(id="own", vessel_type=VesselType.OWN_SHIP)
        target = Vessel(id="target")
        world.add_vessel(own)
        world.add_vessel(target)
        targets = world.get_targets()
        assert len(targets) == 1
        assert target in targets
        assert own not in targets

    def test_update(self):
        world = World()
        vessel = Vessel(id="test", x=0, y=0, course=0, speed=10)
        world.add_vessel(vessel)
        world.update(1.0)
        assert world.time == 1.0
        assert vessel.y > 0  # Vessel moved

    def test_clear(self):
        world = World()
        own = Vessel(id="own", vessel_type=VesselType.OWN_SHIP)
        target = Vessel(id="target")
        world.add_vessel(own)
        world.add_vessel(target)
        world.update(10.0)
        world.clear()
        assert len(world.vessels) == 0
        assert world.own_ship is None
        assert world.time == 0.0

    def test_get_vessels_in_range(self):
        world = World()
        v1 = Vessel(id="v1", x=0, y=0)
        v2 = Vessel(id="v2", x=100, y=0)
        v3 = Vessel(id="v3", x=1000, y=0)
        world.add_vessel(v1)
        world.add_vessel(v2)
        world.add_vessel(v3)

        nearby = world.get_vessels_in_range(0, 0, 500)
        assert len(nearby) == 2
        assert v1 in nearby
        assert v2 in nearby
        assert v3 not in nearby
