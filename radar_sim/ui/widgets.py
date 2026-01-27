"""UI widget components for the radar control panel."""
import pygame
from typing import Callable, Optional, Tuple, List
from dataclasses import dataclass

# Color scheme (Furuno-style)
COLORS = {
    'bg': (20, 25, 30),
    'panel': (30, 35, 40),
    'border': (60, 70, 80),
    'text': (0, 200, 0),
    'text_dim': (0, 120, 0),
    'highlight': (0, 255, 0),
    'button': (40, 50, 60),
    'button_hover': (50, 65, 80),
    'button_active': (0, 100, 0),
    'slider_track': (40, 50, 60),
    'slider_fill': (0, 150, 0),
    'slider_knob': (0, 200, 0),
}

class Widget:
    """Base class for UI widgets."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event. Returns True if event was consumed."""
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the widget."""
        pass

    def set_position(self, x: int, y: int) -> None:
        """Set widget position."""
        self.rect.x = x
        self.rect.y = y


class Label(Widget):
    """Text label widget."""

    def __init__(self, x: int, y: int, text: str, font_size: int = 20,
                 color: Tuple[int, int, int] = None):
        self.text = text
        self.font_size = font_size
        self.color = color or COLORS['text']
        self.font = pygame.font.Font(None, font_size)
        text_surface = self.font.render(text, True, self.color)
        super().__init__(x, y, text_surface.get_width(), text_surface.get_height())

    def set_text(self, text: str) -> None:
        """Update label text."""
        self.text = text

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.rect.x, self.rect.y))


class Button(Widget):
    """Clickable button widget."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 callback: Callable[[], None] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 22)
        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                self.is_pressed = False
                return True
            self.is_pressed = False

        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # Background color based on state
        if self.is_pressed:
            bg_color = COLORS['button_active']
        elif self.is_hovered:
            bg_color = COLORS['button_hover']
        else:
            bg_color = COLORS['button']

        # Draw button
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, COLORS['border'], self.rect, 1)

        # Draw text centered
        text_color = COLORS['highlight'] if self.is_hovered else COLORS['text']
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Slider(Widget):
    """Horizontal slider widget."""

    def __init__(self, x: int, y: int, width: int, height: int = 20,
                 min_val: float = 0.0, max_val: float = 1.0, value: float = 0.5,
                 label: str = "", callback: Callable[[float], None] = None):
        super().__init__(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self.callback = callback
        self.font = pygame.font.Font(None, 18)
        self.is_dragging = False
        self.knob_radius = height // 2

    def _value_to_x(self, value: float) -> int:
        """Convert value to x position."""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + self.knob_radius + ratio * (self.rect.width - 2 * self.knob_radius))

    def _x_to_value(self, x: int) -> float:
        """Convert x position to value."""
        ratio = (x - self.rect.x - self.knob_radius) / (self.rect.width - 2 * self.knob_radius)
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def set_value(self, value: float) -> None:
        """Set slider value."""
        self.value = max(self.min_val, min(self.max_val, value))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self.value = self._x_to_value(event.pos[0])
                if self.callback:
                    self.callback(self.value)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.value = self._x_to_value(event.pos[0])
            if self.callback:
                self.callback(self.value)
            return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # Draw label
        if self.label:
            label_surface = self.font.render(self.label, True, COLORS['text_dim'])
            surface.blit(label_surface, (self.rect.x, self.rect.y - 15))

        # Draw track
        track_rect = pygame.Rect(
            self.rect.x + self.knob_radius,
            self.rect.y + self.rect.height // 2 - 2,
            self.rect.width - 2 * self.knob_radius,
            4
        )
        pygame.draw.rect(surface, COLORS['slider_track'], track_rect)

        # Draw filled portion
        knob_x = self._value_to_x(self.value)
        fill_rect = pygame.Rect(
            track_rect.x,
            track_rect.y,
            knob_x - track_rect.x,
            track_rect.height
        )
        pygame.draw.rect(surface, COLORS['slider_fill'], fill_rect)

        # Draw knob
        pygame.draw.circle(surface, COLORS['slider_knob'],
                          (knob_x, self.rect.y + self.rect.height // 2),
                          self.knob_radius)

        # Draw value
        value_text = f"{self.value:.2f}"
        value_surface = self.font.render(value_text, True, COLORS['text'])
        surface.blit(value_surface, (self.rect.right + 5, self.rect.y + 2))


class DropDown(Widget):
    """Dropdown selection widget."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 options: List[str], selected: int = 0,
                 label: str = "", callback: Callable[[int, str], None] = None):
        super().__init__(x, y, width, height)
        self.options = options
        self.selected = selected
        self.label = label
        self.callback = callback
        self.font = pygame.font.Font(None, 20)
        self.is_open = False
        self.hover_index = -1

    def set_options(self, options: List[str], selected: int = 0) -> None:
        """Set dropdown options."""
        self.options = options
        self.selected = min(selected, len(options) - 1)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            elif self.is_open:
                # Check if clicking on an option
                dropdown_rect = pygame.Rect(
                    self.rect.x, self.rect.bottom,
                    self.rect.width, len(self.options) * self.rect.height
                )
                if dropdown_rect.collidepoint(event.pos):
                    index = (event.pos[1] - self.rect.bottom) // self.rect.height
                    if 0 <= index < len(self.options):
                        self.selected = index
                        if self.callback:
                            self.callback(index, self.options[index])
                self.is_open = False
                return True

        elif event.type == pygame.MOUSEMOTION and self.is_open:
            dropdown_rect = pygame.Rect(
                self.rect.x, self.rect.bottom,
                self.rect.width, len(self.options) * self.rect.height
            )
            if dropdown_rect.collidepoint(event.pos):
                self.hover_index = (event.pos[1] - self.rect.bottom) // self.rect.height
            else:
                self.hover_index = -1

        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # Draw label
        if self.label:
            label_surface = self.font.render(self.label, True, COLORS['text_dim'])
            surface.blit(label_surface, (self.rect.x, self.rect.y - 15))

        # Draw main button
        pygame.draw.rect(surface, COLORS['button'], self.rect)
        pygame.draw.rect(surface, COLORS['border'], self.rect, 1)

        # Draw selected text
        if self.options:
            text = self.options[self.selected]
            text_surface = self.font.render(text, True, COLORS['text'])
            surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

        # Draw dropdown arrow
        arrow_x = self.rect.right - 15
        arrow_y = self.rect.centery
        pygame.draw.polygon(surface, COLORS['text'], [
            (arrow_x - 4, arrow_y - 2),
            (arrow_x + 4, arrow_y - 2),
            (arrow_x, arrow_y + 4)
        ])

        # Draw dropdown list if open
        if self.is_open:
            for i, option in enumerate(self.options):
                opt_rect = pygame.Rect(
                    self.rect.x, self.rect.bottom + i * self.rect.height,
                    self.rect.width, self.rect.height
                )
                bg_color = COLORS['button_hover'] if i == self.hover_index else COLORS['panel']
                pygame.draw.rect(surface, bg_color, opt_rect)
                pygame.draw.rect(surface, COLORS['border'], opt_rect, 1)

                text_surface = self.font.render(option, True, COLORS['text'])
                surface.blit(text_surface, (opt_rect.x + 5, opt_rect.y + 5))


class Panel(Widget):
    """Container panel for grouping widgets."""

    def __init__(self, x: int, y: int, width: int, height: int, title: str = ""):
        super().__init__(x, y, width, height)
        self.title = title
        self.widgets: List[Widget] = []
        self.font = pygame.font.Font(None, 22)

    def add_widget(self, widget: Widget) -> None:
        """Add a widget to this panel."""
        # Offset widget position relative to panel
        widget.rect.x += self.rect.x
        widget.rect.y += self.rect.y
        self.widgets.append(widget)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        for widget in reversed(self.widgets):  # Handle top widgets first
            if widget.handle_event(event):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # Draw panel background
        pygame.draw.rect(surface, COLORS['panel'], self.rect)
        pygame.draw.rect(surface, COLORS['border'], self.rect, 1)

        # Draw title
        if self.title:
            title_surface = self.font.render(self.title, True, COLORS['highlight'])
            surface.blit(title_surface, (self.rect.x + 10, self.rect.y + 5))
            # Separator line
            pygame.draw.line(surface, COLORS['border'],
                           (self.rect.x + 5, self.rect.y + 25),
                           (self.rect.right - 5, self.rect.y + 25))

        # Draw child widgets
        for widget in self.widgets:
            widget.draw(surface)
