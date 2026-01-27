"""Geometry utilities for range and bearing calculations."""
import math
from typing import Tuple

def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 degrees."""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle

def deg_to_rad(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0

def rad_to_deg(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi

def calculate_range(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate distance between two points in meters."""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)

def calculate_bearing(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate bearing from point 1 to point 2 in degrees (0=North, 90=East)."""
    dx = x2 - x1
    dy = y2 - y1
    bearing = math.atan2(dx, dy)  # Note: atan2(x, y) for navigation convention
    return normalize_angle(rad_to_deg(bearing))

def calculate_relative_bearing(own_heading: float, target_bearing: float) -> float:
    """Calculate relative bearing from own ship heading."""
    rel_bearing = target_bearing - own_heading
    return normalize_angle(rel_bearing)

def polar_to_cartesian(range_m: float, bearing_deg: float) -> Tuple[float, float]:
    """Convert polar coordinates to cartesian (x=East, y=North)."""
    bearing_rad = deg_to_rad(bearing_deg)
    x = range_m * math.sin(bearing_rad)
    y = range_m * math.cos(bearing_rad)
    return x, y

def cartesian_to_polar(x: float, y: float) -> Tuple[float, float]:
    """Convert cartesian to polar (range, bearing)."""
    range_m = math.sqrt(x * x + y * y)
    bearing_deg = normalize_angle(rad_to_deg(math.atan2(x, y)))
    return range_m, bearing_deg

def calculate_cpa(own_x: float, own_y: float, own_course: float, own_speed: float,
                  tgt_x: float, tgt_y: float, tgt_course: float, tgt_speed: float) -> Tuple[float, float]:
    """Calculate Closest Point of Approach (CPA) and Time to CPA (TCPA).

    Returns:
        Tuple of (CPA distance in meters, TCPA in seconds).
        Negative TCPA means CPA is in the past.
    """
    # Convert speeds from knots to m/s
    own_speed_ms = own_speed * 0.514444
    tgt_speed_ms = tgt_speed * 0.514444

    # Calculate velocity components
    own_vx = own_speed_ms * math.sin(deg_to_rad(own_course))
    own_vy = own_speed_ms * math.cos(deg_to_rad(own_course))
    tgt_vx = tgt_speed_ms * math.sin(deg_to_rad(tgt_course))
    tgt_vy = tgt_speed_ms * math.cos(deg_to_rad(tgt_course))

    # Relative position and velocity
    rel_x = tgt_x - own_x
    rel_y = tgt_y - own_y
    rel_vx = tgt_vx - own_vx
    rel_vy = tgt_vy - own_vy

    # Calculate TCPA
    rel_v_sq = rel_vx * rel_vx + rel_vy * rel_vy
    if rel_v_sq < 1e-10:  # Essentially stationary relative to each other
        return calculate_range(own_x, own_y, tgt_x, tgt_y), 0.0

    tcpa = -(rel_x * rel_vx + rel_y * rel_vy) / rel_v_sq

    # Calculate CPA
    cpa_x = rel_x + rel_vx * tcpa
    cpa_y = rel_y + rel_vy * tcpa
    cpa = math.sqrt(cpa_x * cpa_x + cpa_y * cpa_y)

    return cpa, tcpa
