"""Top-down geographic scene view for visualizing radar environment."""
import math
import pygame
from typing import List, Tuple, Optional


# Nautical mile in meters
NM_TO_M = 1852.0

COLORS = {
    'water': (20, 40, 80),
    'land': (120, 100, 60),
    'own_ship': (255, 255, 0),
    'vessel': (255, 100, 100),
    'vessel_label': (255, 180, 180),
    'range_ring': (60, 80, 120),
    'grid': (40, 60, 100),
    'north_arrow': (255, 255, 255),
    'echo': (0, 200, 0),
    'title': (180, 200, 220),
}


class SceneView:
    """Top-down map view showing world objects alongside the PPI."""

    def __init__(self, size: int = 600):
        self.size = size
        self.center = (size // 2, size // 2)
        self.radius = size // 2 - 20
        self.surface = pygame.Surface((size, size))
        # Accumulated echo surface for CSV playback
        self.echo_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        self.echo_surface.fill((0, 0, 0, 0))
        self._font = None
        self._small_font = None

    def _get_font(self, size: int = 16):
        if self._font is None:
            self._font = pygame.font.SysFont('consolas', 16)
            self._small_font = pygame.font.SysFont('consolas', 12)
        if size <= 12:
            return self._small_font
        return self._font

    def _world_to_screen(self, wx: float, wy: float,
                          own_x: float, own_y: float,
                          zoom: float) -> Tuple[int, int]:
        """Convert world coordinates to screen pixels."""
        dx = wx - own_x
        dy = wy - own_y
        # X = east → screen right, Y = north → screen up (flip)
        sx = self.center[0] + dx * zoom
        sy = self.center[1] - dy * zoom
        return int(sx), int(sy)

    def render(self, own_ship, vessels, coastlines, range_nm: float) -> pygame.Surface:
        """Render the scene view for simulation mode."""
        self.surface.fill(COLORS['water'])

        max_range_m = range_nm * NM_TO_M
        zoom = self.radius / max_range_m if max_range_m > 0 else 1.0

        own_x = own_ship.x if own_ship else 0.0
        own_y = own_ship.y if own_ship else 0.0

        # Draw coastline polygons filled
        if coastlines:
            for coastline in coastlines:
                if len(coastline.points) >= 3:
                    screen_pts = []
                    for p in coastline.points:
                        sx, sy = self._world_to_screen(p.x, p.y, own_x, own_y, zoom)
                        screen_pts.append((sx, sy))
                    # Clip check — skip if all points far off screen
                    if any(0 <= x < self.size and 0 <= y < self.size for x, y in screen_pts):
                        pygame.draw.polygon(self.surface, COLORS['land'], screen_pts)

        # Draw range rings
        self._draw_range_rings(range_nm, max_range_m)

        # Draw vessels
        if vessels:
            for vessel in (vessels.values() if isinstance(vessels, dict) else vessels):
                if not vessel.is_active:
                    continue
                if vessel is own_ship:
                    continue
                vx, vy = self._world_to_screen(vessel.x, vessel.y, own_x, own_y, zoom)
                self._draw_vessel_marker(vx, vy, vessel.course, COLORS['vessel'],
                                         getattr(vessel, 'name', ''))

        # Draw own ship
        if own_ship:
            ox, oy = self.center
            self._draw_vessel_marker(ox, oy, own_ship.course, COLORS['own_ship'], 'OWN')

        # North arrow
        self._draw_north_arrow()

        # Title
        font = self._get_font()
        label = font.render("SCENE VIEW", True, COLORS['title'])
        self.surface.blit(label, (self.size // 2 - label.get_width() // 2, 5))

        return self.surface

    def render_csv(self, sweep_pairs: List[Tuple[float, List[float]]],
                    range_nm: float = 6.0) -> pygame.Surface:
        """Render accumulated radar echoes for CSV playback mode."""
        max_range_m = range_nm * NM_TO_M
        zoom = self.radius / max_range_m if max_range_m > 0 else 1.0

        # Accumulate new sweeps onto echo surface
        for bearing, data in sweep_pairs:
            bearing_rad = math.radians(bearing)
            num_bins = len(data)
            for i, intensity in enumerate(data):
                if intensity < 0.05:
                    continue
                dist_m = (i + 0.5) / num_bins * max_range_m
                # World offset from center (north-up)
                dx = dist_m * math.sin(bearing_rad)
                dy = dist_m * math.cos(bearing_rad)
                sx = self.center[0] + dx * zoom
                sy = self.center[1] - dy * zoom
                if 0 <= sx < self.size and 0 <= sy < self.size:
                    green = int(min(255, intensity * 255 * 1.5))
                    alpha = int(min(255, intensity * 255))
                    pygame.draw.circle(self.echo_surface, (0, green, 0, alpha),
                                       (int(sx), int(sy)), 2)

        # Compose
        self.surface.fill(COLORS['water'])
        self.surface.blit(self.echo_surface, (0, 0))
        self._draw_range_rings(range_nm, max_range_m)
        self._draw_north_arrow()

        # Center marker
        pygame.draw.circle(self.surface, COLORS['own_ship'], self.center, 4)

        font = self._get_font()
        label = font.render("SCENE VIEW (CSV)", True, COLORS['title'])
        self.surface.blit(label, (self.size // 2 - label.get_width() // 2, 5))

        return self.surface

    def clear_echoes(self):
        """Clear accumulated CSV echo data."""
        self.echo_surface.fill((0, 0, 0, 0))

    def _draw_range_rings(self, range_nm: float, max_range_m: float):
        num_rings = 4
        font = self._get_font(12)
        for i in range(1, num_rings + 1):
            r = int(self.radius * i / num_rings)
            pygame.draw.circle(self.surface, COLORS['range_ring'], self.center, r, 1)
            ring_nm = range_nm * i / num_rings
            label = font.render(f"{ring_nm:.1f}nm", True, COLORS['range_ring'])
            self.surface.blit(label, (self.center[0] + 4, self.center[1] - r + 2))

    def _draw_vessel_marker(self, x: int, y: int, heading: float,
                             color, name: str = ''):
        """Draw a triangle marker showing vessel position and heading."""
        heading_rad = math.radians(heading)
        size = 8
        # Triangle points: nose forward, two rear corners
        nose_x = x + size * math.sin(heading_rad)
        nose_y = y - size * math.cos(heading_rad)
        left_x = x + size * 0.6 * math.sin(heading_rad + 2.5)
        left_y = y - size * 0.6 * math.cos(heading_rad + 2.5)
        right_x = x + size * 0.6 * math.sin(heading_rad - 2.5)
        right_y = y - size * 0.6 * math.cos(heading_rad - 2.5)

        pts = [(int(nose_x), int(nose_y)),
               (int(left_x), int(left_y)),
               (int(right_x), int(right_y))]
        pygame.draw.polygon(self.surface, color, pts)

        if name:
            font = self._get_font(12)
            label = font.render(name, True, COLORS['vessel_label'])
            self.surface.blit(label, (x + 10, y - 6))

    def _draw_north_arrow(self):
        """Draw a north indicator in the top-right corner."""
        ax, ay = self.size - 30, 30
        pygame.draw.line(self.surface, COLORS['north_arrow'],
                         (ax, ay + 15), (ax, ay - 15), 2)
        pygame.draw.polygon(self.surface, COLORS['north_arrow'],
                            [(ax, ay - 15), (ax - 5, ay - 5), (ax + 5, ay - 5)])
        font = self._get_font(12)
        n_label = font.render("N", True, COLORS['north_arrow'])
        self.surface.blit(n_label, (ax - n_label.get_width() // 2, ay - 30))
