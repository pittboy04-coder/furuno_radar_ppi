"""Main control panel for the radar simulator."""
import pygame
from typing import Optional, List
from .widgets import Panel, Button, Slider, Label, DropDown, COLORS
from ..core.simulation import Simulation
from ..scenarios.scenario_manager import ScenarioManager
from ..data_import import CsvPlayer

class ControlPanel:
    """Main control panel containing all radar controls."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.simulation: Optional[Simulation] = None
        self.scenario_manager: Optional[ScenarioManager] = None
        self.csv_player: Optional[CsvPlayer] = None

        # Create panels
        self._create_panels()

    def _create_panels(self) -> None:
        """Create all control panels and widgets."""
        panel_width = self.rect.width - 20
        y_offset = 10

        # Scenario panel
        self.scenario_panel = Panel(10, y_offset, panel_width, 80, "SCENARIO")
        self.scenario_dropdown = DropDown(
            15, 35, panel_width - 30, 25,
            ["Default"],  # Will be populated when scenario manager is set
            selected=0,
            callback=self._on_scenario_change
        )
        self.scenario_panel.add_widget(self.scenario_dropdown)
        y_offset += 90

        # Range control panel
        self.range_panel = Panel(10, y_offset, panel_width, 80, "RANGE")
        self.range_dropdown = DropDown(
            15, 35, panel_width - 30, 25,
            ["0.25 nm", "0.5 nm", "0.75 nm", "1.5 nm", "3 nm", "6 nm", "12 nm", "24 nm", "48 nm"],
            selected=5,  # Default 6nm
            callback=self._on_range_change
        )
        self.range_panel.add_widget(self.range_dropdown)
        y_offset += 90

        # Gain controls panel
        self.gain_panel = Panel(10, y_offset, panel_width, 160, "GAIN CONTROLS")
        self.gain_slider = Slider(
            15, 45, panel_width - 70, 20,
            min_val=0.0, max_val=1.0, value=0.5,
            label="GAIN",
            callback=self._on_gain_change
        )
        self.sea_slider = Slider(
            15, 85, panel_width - 70, 20,
            min_val=0.0, max_val=1.0, value=0.3,
            label="SEA",
            callback=self._on_sea_change
        )
        self.rain_slider = Slider(
            15, 125, panel_width - 70, 20,
            min_val=0.0, max_val=1.0, value=0.3,
            label="RAIN",
            callback=self._on_rain_change
        )
        self.gain_panel.add_widget(self.gain_slider)
        self.gain_panel.add_widget(self.sea_slider)
        self.gain_panel.add_widget(self.rain_slider)
        y_offset += 170

        # Simulation controls panel
        self.sim_panel = Panel(10, y_offset, panel_width, 120, "SIMULATION")
        self.pause_button = Button(
            15, 35, (panel_width - 40) // 2, 30, "PAUSE",
            callback=self._on_pause
        )
        self.reset_button = Button(
            (panel_width - 40) // 2 + 25, 35, (panel_width - 40) // 2, 30, "RESET",
            callback=self._on_reset
        )
        self.speed_slider = Slider(
            15, 85, panel_width - 70, 20,
            min_val=0.1, max_val=5.0, value=1.0,
            label="SPEED",
            callback=self._on_speed_change
        )
        self.sim_panel.add_widget(self.pause_button)
        self.sim_panel.add_widget(self.reset_button)
        self.sim_panel.add_widget(self.speed_slider)
        y_offset += 130

        # Weather panel
        self.weather_panel = Panel(10, y_offset, panel_width, 120, "WEATHER")
        self.sea_state_dropdown = DropDown(
            15, 35, panel_width - 30, 25,
            ["Calm (0)", "Light (2)", "Moderate (4)", "Rough (6)", "Severe (8)"],
            selected=1,
            label="Sea State",
            callback=self._on_sea_state_change
        )
        self.rain_rate_slider = Slider(
            15, 85, panel_width - 70, 20,
            min_val=0.0, max_val=50.0, value=0.0,
            label="RAIN mm/h",
            callback=self._on_rain_rate_change
        )
        self.weather_panel.add_widget(self.sea_state_dropdown)
        self.weather_panel.add_widget(self.rain_rate_slider)
        y_offset += 130

        # Data Export panel
        self.export_panel = Panel(10, y_offset, panel_width, 175, "DATA EXPORT")
        btn_width = (panel_width - 50) // 3
        self.record_button = Button(
            15, 35, btn_width, 28, "RECORD",
            callback=self._on_record
        )
        self.save_button = Button(
            20 + btn_width, 35, btn_width, 28, "SAVE",
            callback=self._on_save
        )
        self.coastline_button = Button(
            25 + btn_width * 2, 35, btn_width, 28, "COAST",
            callback=self._on_coastline_toggle
        )
        self.csv_button = Button(
            15, 68, btn_width, 28, "LOAD CSV",
            callback=self._on_load_csv
        )
        self.record_label = Label(20, 100, "Not recording", 18)
        self.file_label = Label(20, 120, "", 16)
        self.export_panel.add_widget(self.record_button)
        self.export_panel.add_widget(self.save_button)
        self.export_panel.add_widget(self.coastline_button)
        self.export_panel.add_widget(self.csv_button)
        self.export_panel.add_widget(self.record_label)
        self.export_panel.add_widget(self.file_label)
        y_offset += 185

        # Info panel
        self.info_panel = Panel(10, y_offset, panel_width, 80, "INFO")
        self.time_label = Label(20, 35, "Time: 0.0s", 20)
        self.targets_label = Label(20, 55, "Targets: 0", 20)
        self.info_panel.add_widget(self.time_label)
        self.info_panel.add_widget(self.targets_label)

        # Collect all panels
        self.panels = [
            self.scenario_panel,
            self.range_panel,
            self.gain_panel,
            self.sim_panel,
            self.weather_panel,
            self.export_panel,
            self.info_panel
        ]

    def set_simulation(self, sim: Simulation) -> None:
        """Connect to simulation instance."""
        self.simulation = sim

    def set_scenario_manager(self, manager: ScenarioManager) -> None:
        """Connect scenario manager and populate dropdown."""
        self.scenario_manager = manager
        scenario_names = manager.get_scenario_names()
        if scenario_names:
            self.scenario_dropdown.set_options(scenario_names, selected=0)

    def _on_scenario_change(self, index: int, value: str) -> None:
        """Handle scenario selection change."""
        if self.scenario_manager and self.simulation:
            self.scenario_manager.load_scenario(
                value,
                self.simulation.world,
                self.simulation.radar,
                self.simulation.weather
            )
            self.pause_button.text = "PAUSE"

    def _on_range_change(self, index: int, value: str) -> None:
        """Handle range scale change."""
        if self.simulation:
            # Parse range from string like "6 nm"
            range_nm = float(value.split()[0])
            self.simulation.radar.set_range_scale(range_nm)

    def _on_gain_change(self, value: float) -> None:
        """Handle gain change."""
        if self.simulation:
            self.simulation.radar.set_gain(value)

    def _on_sea_change(self, value: float) -> None:
        """Handle sea clutter change."""
        if self.simulation:
            self.simulation.radar.set_sea_clutter(value)

    def _on_rain_change(self, value: float) -> None:
        """Handle rain clutter change."""
        if self.simulation:
            self.simulation.radar.set_rain_clutter(value)

    def _on_pause(self) -> None:
        """Handle pause button."""
        if self.simulation:
            is_paused = self.simulation.toggle_pause()
            self.pause_button.text = "RESUME" if is_paused else "PAUSE"

    def _on_reset(self) -> None:
        """Handle reset button."""
        if self.simulation:
            self.simulation.reset()
            self.simulation.setup_default_scenario()
            self.pause_button.text = "PAUSE"

    def _on_speed_change(self, value: float) -> None:
        """Handle simulation speed change."""
        if self.simulation:
            self.simulation.set_time_scale(value)

    def _on_sea_state_change(self, index: int, value: str) -> None:
        """Handle sea state change."""
        if self.simulation:
            sea_states = [0, 2, 4, 6, 8]
            self.simulation.weather.set_sea_state(sea_states[index])

    def _on_rain_rate_change(self, value: float) -> None:
        """Handle rain rate change."""
        if self.simulation:
            self.simulation.weather.set_rain(value)

    def _on_record(self) -> None:
        """Handle record button."""
        if self.simulation:
            if self.simulation.is_recording():
                filepath = self.simulation.stop_recording()
                self.record_button.text = "RECORD"
                if filepath:
                    # Show just the filename
                    import os
                    filename = os.path.basename(filepath)
                    self.record_label.set_text("Stopped")
                    self.file_label.set_text(f"Saved: {filename}")
                else:
                    self.record_label.set_text("No data recorded")
                    self.file_label.set_text("")
            else:
                session_id = self.simulation.start_recording()
                self.record_button.text = "STOP"
                self.record_label.set_text(f"Recording...")
                self.file_label.set_text(f"Session: {session_id}")

    def _on_save(self) -> None:
        """Handle save button - export current sweep."""
        if self.simulation:
            bearing = self.simulation.radar.get_current_bearing()
            filepath = self.simulation.export_current_sweep(bearing)
            if filepath:
                import os
                filename = os.path.basename(filepath)
                self.file_label.set_text(f"Saved: {filename}")

    def _on_load_csv(self) -> None:
        """Handle LOAD CSV / STOP CSV button."""
        if self.csv_player and self.csv_player.active:
            # Stop playback
            self.csv_player.stop()
            self.csv_player = None
            self.csv_button.text = "LOAD CSV"
            self.file_label.set_text("CSV stopped")
        else:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            folder = filedialog.askdirectory(title="Select CSV Data Folder")
            root.destroy()
            if folder:
                self.csv_player = CsvPlayer(folder)
                if self.csv_player.active:
                    self.csv_button.text = "STOP CSV"
                    import os
                    self.file_label.set_text(f"CSV: {os.path.basename(folder)}")
                else:
                    self.csv_player = None
                    self.file_label.set_text("No CSV files found")

    def _on_coastline_toggle(self) -> None:
        """Handle coastline toggle button."""
        if self.simulation:
            if self.simulation.coastline_enabled:
                self.simulation.clear_coastlines()
            else:
                self.simulation.setup_harbor_coastline()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        # Temporarily offset all widget positions to match screen coordinates
        for panel in self.panels:
            panel.rect.x += self.rect.x
            panel.rect.y += self.rect.y
            for widget in panel.widgets:
                widget.rect.x += self.rect.x
                widget.rect.y += self.rect.y

        # Handle events
        handled = False
        for panel in reversed(self.panels):
            if panel.handle_event(event):
                handled = True
                break

        # Restore original positions
        for panel in self.panels:
            panel.rect.x -= self.rect.x
            panel.rect.y -= self.rect.y
            for widget in panel.widgets:
                widget.rect.x -= self.rect.x
                widget.rect.y -= self.rect.y

        return handled

    def update(self) -> None:
        """Update panel state from simulation."""
        if not self.simulation:
            return

        # Update info labels
        self.time_label.set_text(f"Time: {self.simulation.world.time:.1f}s")
        self.targets_label.set_text(f"Targets: {len(self.simulation.world.get_targets())}")

        # Update recording status
        if self.simulation.is_recording():
            count = self.simulation.get_record_count()
            self.record_label.set_text(f"Recording: {count} sweeps")

        # Update coastline button text
        if self.simulation.coastline_enabled:
            self.coastline_button.text = "COAST OFF"
        else:
            self.coastline_button.text = "COAST ON"

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the control panel."""
        # Update state
        self.update()

        # Draw background
        bg_rect = pygame.Rect(
            self.rect.x - 10, self.rect.y - 10,
            self.rect.width + 20, self.rect.height + 20
        )
        pygame.draw.rect(surface, COLORS['bg'], bg_rect)

        # Draw all panels (offset by control panel position)
        for panel in self.panels:
            # Temporarily offset panel position
            original_x = panel.rect.x
            original_y = panel.rect.y
            panel.rect.x += self.rect.x
            panel.rect.y += self.rect.y

            # Offset all child widgets too
            for widget in panel.widgets:
                widget.rect.x += self.rect.x
                widget.rect.y += self.rect.y

            panel.draw(surface)

            # Restore positions
            panel.rect.x = original_x
            panel.rect.y = original_y
            for widget in panel.widgets:
                widget.rect.x -= self.rect.x
                widget.rect.y -= self.rect.y
