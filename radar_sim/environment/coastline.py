"""Coastline and landmass simulation for radar returns."""
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CoastlinePoint:
    """A point defining the coastline."""
    x: float  # meters, East positive
    y: float  # meters, North positive

class Coastline:
    """Represents a coastline that generates radar returns."""

    def __init__(self, points: List[Tuple[float, float]] = None):
        """Initialize coastline with a list of (x, y) points."""
        self.points: List[CoastlinePoint] = []
        if points:
            for x, y in points:
                self.points.append(CoastlinePoint(x, y))

        # Radar reflection characteristics
        self.reflectivity = 0.9  # High reflectivity for land
        self.roughness = 0.3    # Surface roughness affects return spread

    def add_point(self, x: float, y: float) -> None:
        """Add a point to the coastline."""
        self.points.append(CoastlinePoint(x, y))

    def clear(self) -> None:
        """Clear all coastline points."""
        self.points.clear()

    def generate_returns(self, own_x: float, own_y: float,
                        bearing: float, beamwidth: float,
                        max_range: float, num_bins: int) -> List[float]:
        """Generate radar returns for the coastline at a given bearing.

        Uses filled-polygon ray-casting with even-odd rule to produce
        solid landmass returns matching real radar output.

        Args:
            own_x, own_y: Own ship position
            bearing: Current antenna bearing in degrees
            beamwidth: Antenna beamwidth in degrees
            max_range: Maximum radar range in meters
            num_bins: Number of range bins

        Returns:
            List of intensities for each range bin
        """
        returns = [0.0] * num_bins
        bin_size = max_range / num_bins
        half_beam = beamwidth / 2

        if len(self.points) < 3:
            return returns

        # Cast multiple rays across beamwidth for smooth edges
        num_rays = 5
        for ray_idx in range(num_rays):
            offset = -half_beam + (2 * half_beam * ray_idx / (num_rays - 1)) if num_rays > 1 else 0
            ray_bearing = bearing + offset
            ray_weight = 1.0 - 0.3 * abs(offset) / (half_beam + 0.01)

            # Find all intersections of this ray with polygon edges
            hits = self._ray_polygon_intersections(own_x, own_y, ray_bearing, max_range)
            hits.sort()

            # Even-odd fill: between pairs of intersections, ray is inside land
            i = 0
            while i < len(hits):
                enter_dist = hits[i]
                if i + 1 < len(hits):
                    exit_dist = hits[i + 1]
                else:
                    # Odd count — ray enters land and doesn't exit before max_range
                    exit_dist = max_range
                i += 2

                start_bin = max(0, int(enter_dist / bin_size))
                end_bin = min(num_bins, int(exit_dist / bin_size) + 1)

                for b in range(start_bin, end_bin):
                    # Strong return inside land, slight edge effect at boundaries
                    if b == start_bin or b == end_bin - 1:
                        intensity = self.reflectivity * 0.75 * ray_weight
                    else:
                        intensity = self.reflectivity * ray_weight
                    returns[b] = max(returns[b], intensity)

        return returns

    def _ray_polygon_intersections(self, ox: float, oy: float,
                                    bearing: float, max_range: float) -> List[float]:
        """Find all distances where a ray intersects the polygon edges."""
        ray_rad = math.radians(bearing)
        dx = math.sin(ray_rad)
        dy = math.cos(ray_rad)

        distances = []
        n = len(self.points)
        for i in range(n - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]

            sx = p2.x - p1.x
            sy = p2.y - p1.y

            denom = dx * sy - dy * sx
            if abs(denom) < 1e-10:
                continue

            t = ((p1.x - ox) * sy - (p1.y - oy) * sx) / denom
            u = ((p1.x - ox) * dy - (p1.y - oy) * dx) / denom

            if t > 0 and 0 <= u <= 1 and t <= max_range:
                distances.append(t)

        return distances

    def is_point_on_land(self, x: float, y: float) -> bool:
        """Check if a point is on land (inside the coastline polygon)."""
        if len(self.points) < 3:
            return False

        # Ray casting algorithm
        inside = False
        j = len(self.points) - 1

        for i in range(len(self.points)):
            pi = self.points[i]
            pj = self.points[j]

            if ((pi.y > y) != (pj.y > y) and
                x < (pj.x - pi.x) * (y - pi.y) / (pj.y - pi.y) + pi.x):
                inside = not inside
            j = i

        return inside


def create_harbor_coastline(center_x: float = 0, center_y: float = 8000,
                           width: float = 15000, depth: float = 4000) -> Coastline:
    """Create a harbor-shaped coastline ahead of own ship.

    Args:
        center_x: X coordinate of harbor center
        center_y: Y coordinate of harbor entrance (distance ahead)
        width: Total width of the coastline
        depth: How far back the harbor goes
    """
    coastline = Coastline()

    # Create a harbor shape (U-shaped indentation in coastline)
    points = [
        # Left coast going north
        (center_x - width/2, center_y - depth),
        (center_x - width/2, center_y),
        # Harbor entrance left
        (center_x - width/6, center_y),
        (center_x - width/6, center_y + depth/2),
        # Harbor back
        (center_x + width/6, center_y + depth/2),
        # Harbor entrance right
        (center_x + width/6, center_y),
        (center_x + width/2, center_y),
        # Right coast
        (center_x + width/2, center_y - depth),
    ]

    for x, y in points:
        coastline.add_point(x, y)

    # Close the polygon (far land boundary)
    coastline.add_point(center_x + width/2, center_y + depth * 2)
    coastline.add_point(center_x - width/2, center_y + depth * 2)
    coastline.add_point(center_x - width/2, center_y - depth)

    return coastline


def create_island_coastline(center_x: float, center_y: float,
                           radius: float, num_points: int = 24) -> Coastline:
    """Create a roughly circular island.

    Args:
        center_x, center_y: Island center
        radius: Approximate radius
        num_points: Number of points to define the island
    """
    import random
    coastline = Coastline()

    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Add some randomness to make it look natural
        r = radius * (0.8 + 0.4 * random.random())
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        coastline.add_point(x, y)

    # Close the polygon
    if coastline.points:
        coastline.add_point(coastline.points[0].x, coastline.points[0].y)

    return coastline


def create_straight_coastline(start_x: float, start_y: float,
                             end_x: float, end_y: float,
                             land_depth: float = 5000) -> Coastline:
    """Create a straight coastline with land behind it.

    Args:
        start_x, start_y: Start point of coastline
        end_x, end_y: End point of coastline
        land_depth: How far the land extends behind the coastline
    """
    coastline = Coastline()

    # Calculate perpendicular direction (into land)
    dx = end_x - start_x
    dy = end_y - start_y
    length = math.sqrt(dx*dx + dy*dy)

    # Perpendicular unit vector (pointing "inland")
    px = -dy / length
    py = dx / length

    # Create polygon: coastline + land behind
    coastline.add_point(start_x, start_y)
    coastline.add_point(end_x, end_y)
    coastline.add_point(end_x + px * land_depth, end_y + py * land_depth)
    coastline.add_point(start_x + px * land_depth, start_y + py * land_depth)
    coastline.add_point(start_x, start_y)  # Close polygon

    return coastline
