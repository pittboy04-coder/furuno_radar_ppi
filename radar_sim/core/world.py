"""World container for managing simulation state."""
from typing import Dict, List, Optional
from ..objects.vessel import Vessel, VesselType

class World:
    """Container for all simulation objects and state."""

    def __init__(self):
        self.vessels: Dict[str, Vessel] = {}
        self.own_ship: Optional[Vessel] = None
        self.time: float = 0.0  # Simulation time in seconds

    def add_vessel(self, vessel: Vessel) -> None:
        """Add a vessel to the world."""
        self.vessels[vessel.id] = vessel
        if vessel.vessel_type == VesselType.OWN_SHIP:
            self.own_ship = vessel

    def remove_vessel(self, vessel_id: str) -> Optional[Vessel]:
        """Remove a vessel from the world."""
        vessel = self.vessels.pop(vessel_id, None)
        if vessel and vessel == self.own_ship:
            self.own_ship = None
        return vessel

    def get_vessel(self, vessel_id: str) -> Optional[Vessel]:
        """Get a vessel by ID."""
        return self.vessels.get(vessel_id)

    def get_all_vessels(self) -> List[Vessel]:
        """Get all vessels."""
        return list(self.vessels.values())

    def get_targets(self) -> List[Vessel]:
        """Get all vessels except own ship."""
        return [v for v in self.vessels.values() if v != self.own_ship]

    def update(self, dt: float) -> None:
        """Update all vessels in the world.

        Args:
            dt: Time step in seconds
        """
        self.time += dt
        for vessel in self.vessels.values():
            vessel.update(dt)

    def clear(self) -> None:
        """Remove all vessels from the world."""
        self.vessels.clear()
        self.own_ship = None
        self.time = 0.0

    def get_vessels_in_range(self, center_x: float, center_y: float,
                             max_range: float) -> List[Vessel]:
        """Get all vessels within a certain range of a point."""
        import math
        result = []
        for vessel in self.vessels.values():
            dx = vessel.x - center_x
            dy = vessel.y - center_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= max_range:
                result.append(vessel)
        return result
