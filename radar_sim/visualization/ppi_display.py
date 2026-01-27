"""PPI (Plan Position Indicator) radar display."""
import math
from typing import List, Tuple, Optional
import pygame

class PPIDisplay:
    """Renders radar data in classic PPI format."""

    def __init__(self, size: int = 600, center: Tuple[int, int] = None):
        """Initialize PPI display.

        Args:
            size: Display diameter in pixels
            center: Center point (defaults to center of size)
        """
        self.size = size
        self.radius = size // 2 - 20
        self.center = center or (size // 2, size // 2)

        # Colors (Furuno-style green phosphor look)
        self.bg_color = (0, 10, 0)
        self.grid_color = (0, 60, 0)
        self.sweep_color = (0, 255, 0)
        self.echo_color = (0, 255, 0)
        self.text_color = (0, 200, 0)
        self.heading_marker_color = (0, 255, 0)

        # Display settings
        self.num_range_rings = 4
        self.show_range_rings = True
        self.show_bearing_lines = True
        self.show_heading_line = True
        self.trail_persistence = 0.95  # How fast trails fade

        # Surfaces
        self.surface: Optional[pygame.Surface] = None
        self.echo_surface: Optional[pygame.Surface] = None

        # State
        self.current_bearing = 0.0
        self.range_nm = 6.0
        self.heading = 0.0

        # Mouse interaction state
        self.cursor_range_nm: Optional[float] = None
        self.cursor_bearing: Optional[float] = None
        self.ppi_offset = (0, 0)  # Offset of PPI on screen for mouse calculations
        self.font: Optional[pygame.font.Font] = None

    def initialize(self) -> pygame.Surface:
        """Initialize pygame surfaces."""
        self.surface = pygame.Surface((self.size, self.size))
        self.echo_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.echo_surface.fill((0, 0, 0, 0))
        return self.surface

    def _polar_to_screen(self, range_ratio: float, bearing_deg: float) -> Tuple[int, int]:
        """Convert polar coordinates to screen coordinates.

        Args:
            range_ratio: Range as fraction of max range (0-1)
            bearing_deg: Bearing in degrees (0 = up/north)

        Returns:
            Screen (x, y) coordinates
        """
        bearing_rad = math.radians(bearing_deg - 90)  # Convert to math convention
        r = range_ratio * self.radius
        x = self.center[0] + r * math.cos(bearing_rad)
        y = self.center[1] + r * math.sin(bearing_rad)
        return int(x), int(y)

    def draw_background(self) -> None:
        """Draw PPI background with grid."""
        self.surface.fill(self.bg_color)

        # Range rings
        if self.show_range_rings:
            for i in range(1, self.num_range_rings + 1):
                r = int(self.radius * i / self.num_range_rings)
                pygame.draw.circle(self.surface, self.grid_color,
                                 self.center, r, 1)

        # Bearing lines (every 30 degrees)
        if self.show_bearing_lines:
            for bearing in range(0, 360, 30):
                end_x, end_y = self._polar_to_screen(1.0, bearing)
                pygame.draw.line(self.surface, self.grid_color,
                               self.center, (end_x, end_y), 1)

        # Heading marker
        if self.show_heading_line:
            hx, hy = self._polar_to_screen(1.0, self.heading)
            pygame.draw.line(self.surface, self.heading_marker_color,
                           self.center, (hx, hy), 2)

        # Center dot
        pygame.draw.circle(self.surface, self.sweep_color, self.center, 3)

    def draw_sweep_line(self, bearing: float) -> None:
        """Draw the current sweep line.

        Args:
            bearing: Current antenna bearing in degrees
        """
        self.current_bearing = bearing
        end_x, end_y = self._polar_to_screen(1.0, bearing)
        pygame.draw.line(self.surface, self.sweep_color,
                        self.center, (end_x, end_y), 1)

    def draw_sweep_data(self, bearing: float, data: List[float],
                       fade_old: bool = True) -> None:
        """Draw radar returns for a sweep.

        Args:
            bearing: Bearing of this sweep
            data: List of return intensities (0-1) for each range bin
            fade_old: Whether to fade old returns
        """
        if fade_old:
            # Fade the echo surface slightly
            fade_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(255 * (1 - self.trail_persistence))))
            self.echo_surface.blit(fade_surface, (0, 0),
                                  special_flags=pygame.BLEND_RGBA_SUB)

        num_bins = len(data)
        bearing_rad = math.radians(bearing - 90)

        for i, intensity in enumerate(data):
            if intensity < 0.05:
                continue

            range_ratio = (i + 0.5) / num_bins
            r = range_ratio * self.radius

            x = self.center[0] + r * math.cos(bearing_rad)
            y = self.center[1] + r * math.sin(bearing_rad)

            # Color based on intensity
            green = int(min(255, intensity * 255 * 1.5))
            alpha = int(min(255, intensity * 255))

            # Draw echo point
            pygame.draw.circle(self.echo_surface, (0, green, 0, alpha),
                             (int(x), int(y)), 2)

    def draw_detection(self, range_ratio: float, bearing: float,
                      intensity: float = 1.0) -> None:
        """Draw a detected target.

        Args:
            range_ratio: Range as fraction of max range
            bearing: Bearing in degrees
            intensity: Signal intensity (0-1)
        """
        x, y = self._polar_to_screen(range_ratio, bearing)
        size = max(3, int(intensity * 6))
        green = int(min(255, intensity * 255))
        pygame.draw.circle(self.echo_surface, (0, green, 0, 255),
                         (x, y), size)

    def set_range(self, range_nm: float) -> None:
        """Set the display range scale."""
        self.range_nm = range_nm

    def set_heading(self, heading: float) -> None:
        """Set own ship heading for display."""
        self.heading = heading

    def clear_echoes(self) -> None:
        """Clear all echo data."""
        if self.echo_surface:
            self.echo_surface.fill((0, 0, 0, 0))

    def set_ppi_offset(self, x: int, y: int) -> None:
        """Set the offset of PPI on the main screen for mouse calculations."""
        self.ppi_offset = (x, y)

    def screen_to_polar(self, screen_x: int, screen_y: int) -> Optional[Tuple[float, float]]:
        """Convert screen coordinates to polar (range_nm, bearing).

        Args:
            screen_x, screen_y: Screen coordinates

        Returns:
            Tuple of (range in nm, bearing in degrees) or None if outside PPI
        """
        # Adjust for PPI offset on screen
        local_x = screen_x - self.ppi_offset[0] - self.center[0]
        local_y = screen_y - self.ppi_offset[1] - self.center[1]

        # Calculate distance from center
        distance = math.sqrt(local_x * local_x + local_y * local_y)

        if distance > self.radius:
            return None

        # Calculate range
        range_ratio = distance / self.radius
        range_nm = range_ratio * self.range_nm

        # Calculate bearing (0 = up/north, clockwise)
        bearing = math.degrees(math.atan2(local_x, -local_y))
        bearing = (bearing + 360) % 360

        return range_nm, bearing

    def handle_mouse_motion(self, screen_x: int, screen_y: int) -> bool:
        """Handle mouse motion for cursor tracking.

        Args:
            screen_x, screen_y: Screen coordinates

        Returns:
            True if cursor is over PPI
        """
        result = self.screen_to_polar(screen_x, screen_y)
        if result:
            self.cursor_range_nm, self.cursor_bearing = result
            return True
        else:
            self.cursor_range_nm = None
            self.cursor_bearing = None
            return False

    def draw_cursor_info(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw cursor range/bearing information.

        Args:
            surface: Surface to draw on
            x, y: Position to draw at
        """
        if self.font is None:
            self.font = pygame.font.Font(None, 22)

        if self.cursor_range_nm is not None and self.cursor_bearing is not None:
            # Draw cursor info box
            info_lines = [
                f"Cursor:",
                f"  Range: {self.cursor_range_nm:.2f} nm",
                f"  Bearing: {self.cursor_bearing:.1f}°",
            ]

            box_width = 140
            box_height = len(info_lines) * 18 + 10
            box_rect = pygame.Rect(x, y, box_width, box_height)

            pygame.draw.rect(surface, (20, 30, 20), box_rect)
            pygame.draw.rect(surface, (0, 100, 0), box_rect, 1)

            for i, line in enumerate(info_lines):
                text = self.font.render(line, True, self.text_color)
                surface.blit(text, (x + 5, y + 5 + i * 18))

    def draw_cursor_crosshairs(self) -> None:
        """Draw crosshairs at cursor position on PPI."""
        if self.cursor_range_nm is None or self.cursor_bearing is None:
            return

        range_ratio = self.cursor_range_nm / self.range_nm
        if range_ratio > 1.0:
            return

        x, y = self._polar_to_screen(range_ratio, self.cursor_bearing)

        # Draw small crosshairs
        crosshair_size = 8
        crosshair_color = (0, 255, 255)  # Cyan for visibility

        pygame.draw.line(self.surface, crosshair_color,
                        (x - crosshair_size, y), (x + crosshair_size, y), 1)
        pygame.draw.line(self.surface, crosshair_color,
                        (x, y - crosshair_size), (x, y + crosshair_size), 1)

    def render(self) -> pygame.Surface:
        """Render the complete PPI display.

        Returns:
            The rendered surface
        """
        # Draw background
        self.draw_background()

        # Composite echo surface onto main surface
        self.surface.blit(self.echo_surface, (0, 0))

        # Draw cursor crosshairs
        self.draw_cursor_crosshairs()

        # Draw sweep line on top
        self.draw_sweep_line(self.current_bearing)

        # Draw range ring labels
        self._draw_range_labels()

        return self.surface

    def _draw_range_labels(self) -> None:
        """Draw range scale labels on the PPI."""
        if self.font is None:
            self.font = pygame.font.Font(None, 18)

        for i in range(1, self.num_range_rings + 1):
            range_val = self.range_nm * i / self.num_range_rings
            label = f"{range_val:.1f}"

            # Position label at bottom of each ring
            r = int(self.radius * i / self.num_range_rings)
            label_x = self.center[0] + 5
            label_y = self.center[1] + r - 10

            text = self.font.render(label, True, self.grid_color)
            self.surface.blit(text, (label_x, label_y))
