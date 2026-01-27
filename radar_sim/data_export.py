"""Data export functionality for radar returns.

Supports two CSV formats:
1. radar_plotter format (default) - Compatible with the Rust radar_plotter visualizer
2. detailed format - Full metadata with labeled columns

radar_plotter format:
  - Header row (skipped by visualizer)
  - Data rows: timestamp, unused, range_setting, gain_code, angle_ticks, echo_values...
  - angle_ticks: 8192 ticks = 360 degrees
  - gain_code: integer 0-255
  - range_setting: range in meters
"""
import csv
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

# Conversion constants for radar_plotter compatibility
ANGLE_TICKS_PER_DEGREE = 8192.0 / 360.0  # ~22.756 ticks per degree
NM_TO_METERS = 1852.0

@dataclass
class RadarSweepRecord:
    """A single radar sweep record for export."""
    timestamp: float          # Simulation time in seconds
    bearing_deg: float        # Antenna bearing in degrees
    range_scale_nm: float     # Current range scale
    gain: float              # Receiver gain (0-1)
    sea_clutter: float       # Sea clutter setting (0-1)
    rain_clutter: float      # Rain clutter setting (0-1)
    num_bins: int            # Number of range bins
    echo_values: List[float] # Echo intensity for each bin (0-1)


class RadarDataExporter:
    """Exports radar data to CSV files."""

    def __init__(self, output_dir: str = None):
        """Initialize exporter.

        Args:
            output_dir: Directory for output files. Defaults to current directory.
        """
        self.output_dir = output_dir or os.getcwd()
        self.records: List[RadarSweepRecord] = []
        self.is_recording = False
        self.session_id: Optional[str] = None
        self.max_records = 36000  # ~10 minutes at 60fps

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def start_recording(self) -> str:
        """Start recording radar data.

        Returns:
            Session ID for this recording
        """
        self.records.clear()
        self.is_recording = True
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.session_id

    def stop_recording(self) -> str:
        """Stop recording and save to file.

        Returns:
            Path to the saved file
        """
        self.is_recording = False
        if self.records:
            return self.save_to_csv()
        return ""

    def add_sweep(self, timestamp: float, bearing_deg: float,
                  range_scale_nm: float, gain: float,
                  sea_clutter: float, rain_clutter: float,
                  echo_values: List[float]) -> None:
        """Add a sweep record.

        Args:
            timestamp: Simulation time
            bearing_deg: Current bearing
            range_scale_nm: Range scale in nautical miles
            gain: Gain setting
            sea_clutter: Sea clutter setting
            rain_clutter: Rain clutter setting
            echo_values: List of echo intensities
        """
        if not self.is_recording:
            return

        if len(self.records) >= self.max_records:
            # Auto-save and start new file
            self.save_to_csv()
            self.records.clear()
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        record = RadarSweepRecord(
            timestamp=timestamp,
            bearing_deg=bearing_deg,
            range_scale_nm=range_scale_nm,
            gain=gain,
            sea_clutter=sea_clutter,
            rain_clutter=rain_clutter,
            num_bins=len(echo_values),
            echo_values=echo_values.copy()
        )
        self.records.append(record)

    def save_to_csv(self, filename: str = None, format: str = "radar_plotter") -> str:
        """Save recorded data to CSV file.

        Args:
            filename: Optional custom filename
            format: "radar_plotter" (compatible with visualizer) or "detailed" (full metadata)

        Returns:
            Path to saved file
        """
        if not self.records:
            return ""

        if filename is None:
            filename = f"radar_data_{self.session_id}.csv"

        filepath = os.path.join(self.output_dir, filename)

        if format == "radar_plotter":
            return self._save_radar_plotter_format(filepath)
        else:
            return self._save_detailed_format(filepath)

    def _save_radar_plotter_format(self, filepath: str) -> str:
        """Save in radar_plotter compatible format.

        Format: timestamp, unused, range_setting, gain_code, angle_ticks, echo_values...
        - angle_ticks: bearing * (8192/360), where 8192 = full rotation
        - gain_code: gain * 255 (0-255 integer)
        - range_setting: range in meters
        """
        num_bins = self.records[0].num_bins

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header (will be skipped by radar_plotter)
            header = ['timestamp', 'unused', 'range_m', 'gain_code', 'angle_ticks']
            for i in range(num_bins):
                header.append(f'bin_{i}')
            writer.writerow(header)

            # Write data
            for record in self.records:
                # Convert bearing to angle ticks (8192 ticks = 360 degrees)
                angle_ticks = record.bearing_deg * ANGLE_TICKS_PER_DEGREE

                # Convert gain (0-1) to gain code (0-255)
                gain_code = int(record.gain * 255)

                # Convert range from nm to meters
                range_m = int(record.range_scale_nm * NM_TO_METERS)

                row = [
                    f"{record.timestamp:.3f}",
                    0,  # unused column
                    range_m,
                    gain_code,
                    f"{angle_ticks:.2f}",
                ]
                # Add echo values (keep as floats 0-1)
                for val in record.echo_values:
                    row.append(f"{val:.4f}")

                writer.writerow(row)

        return filepath

    def _save_detailed_format(self, filepath: str) -> str:
        """Save in detailed format with full metadata."""
        num_bins = self.records[0].num_bins
        range_scale = self.records[0].range_scale_nm

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header with descriptive column names
            header = [
                'timestamp_s', 'bearing_deg', 'range_scale_nm',
                'gain', 'sea_clutter', 'rain_clutter'
            ]

            # Add range bin columns with actual range values
            bin_size_nm = range_scale / num_bins
            for i in range(num_bins):
                range_nm = (i + 0.5) * bin_size_nm
                header.append(f'echo_{range_nm:.3f}nm')

            writer.writerow(header)

            # Write data
            for record in self.records:
                row = [
                    f"{record.timestamp:.3f}",
                    f"{record.bearing_deg:.1f}",
                    f"{record.range_scale_nm:.2f}",
                    f"{record.gain:.3f}",
                    f"{record.sea_clutter:.3f}",
                    f"{record.rain_clutter:.3f}",
                ]
                # Add echo values
                for val in record.echo_values:
                    row.append(f"{val:.4f}")

                writer.writerow(row)

        return filepath

    def save_summary_csv(self, filename: str = None) -> str:
        """Save a summary with one row per bearing (averaged).

        Args:
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if not self.records:
            return ""

        if filename is None:
            filename = f"radar_summary_{self.session_id}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # Group by bearing (rounded to integer)
        bearing_data: Dict[int, List[RadarSweepRecord]] = {}
        for record in self.records:
            bearing = int(record.bearing_deg) % 360
            if bearing not in bearing_data:
                bearing_data[bearing] = []
            bearing_data[bearing].append(record)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            num_bins = self.records[0].num_bins
            range_scale = self.records[0].range_scale_nm
            bin_size_nm = range_scale / num_bins

            header = ['bearing_deg', 'num_samples', 'avg_gain']
            for i in range(num_bins):
                range_nm = (i + 0.5) * bin_size_nm
                header.append(f'avg_echo_{range_nm:.3f}nm')
            writer.writerow(header)

            # Write averaged data for each bearing
            for bearing in sorted(bearing_data.keys()):
                records = bearing_data[bearing]
                num_samples = len(records)
                avg_gain = sum(r.gain for r in records) / num_samples

                # Average echo values
                avg_echoes = [0.0] * num_bins
                for record in records:
                    for i, val in enumerate(record.echo_values):
                        if i < num_bins:
                            avg_echoes[i] += val
                avg_echoes = [v / num_samples for v in avg_echoes]

                row = [bearing, num_samples, f"{avg_gain:.3f}"]
                for val in avg_echoes:
                    row.append(f"{val:.4f}")
                writer.writerow(row)

        return filepath

    def export_single_sweep(self, timestamp: float, bearing_deg: float,
                           range_scale_nm: float, gain: float,
                           sea_clutter: float, rain_clutter: float,
                           echo_values: List[float],
                           filename: str = None,
                           format: str = "radar_plotter") -> str:
        """Export a single sweep to CSV (for immediate export).

        Args:
            All radar parameters and echo values
            filename: Optional custom filename
            format: "radar_plotter" (compatible with visualizer) or "detailed"

        Returns:
            Path to saved file
        """
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sweep_{ts}_bearing{int(bearing_deg)}.csv"

        filepath = os.path.join(self.output_dir, filename)
        num_bins = len(echo_values)

        if format == "radar_plotter":
            # radar_plotter compatible format
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)

                # Header (will be skipped by visualizer)
                header = ['timestamp', 'unused', 'range_m', 'gain_code', 'angle_ticks']
                for i in range(num_bins):
                    header.append(f'bin_{i}')
                writer.writerow(header)

                # Single data row
                angle_ticks = bearing_deg * ANGLE_TICKS_PER_DEGREE
                gain_code = int(gain * 255)
                range_m = int(range_scale_nm * NM_TO_METERS)

                row = [f"{timestamp:.3f}", 0, range_m, gain_code, f"{angle_ticks:.2f}"]
                for val in echo_values:
                    row.append(f"{val:.4f}")
                writer.writerow(row)
        else:
            # Detailed format with metadata
            bin_size_nm = range_scale_nm / num_bins

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)

                # Metadata
                writer.writerow(['# Radar Sweep Export'])
                writer.writerow(['timestamp_s', timestamp])
                writer.writerow(['bearing_deg', bearing_deg])
                writer.writerow(['range_scale_nm', range_scale_nm])
                writer.writerow(['gain', gain])
                writer.writerow(['sea_clutter', sea_clutter])
                writer.writerow(['rain_clutter', rain_clutter])
                writer.writerow(['num_bins', num_bins])
                writer.writerow([])

                # Echo data
                writer.writerow(['range_nm', 'range_m', 'echo_intensity'])
                for i, val in enumerate(echo_values):
                    range_nm = (i + 0.5) * bin_size_nm
                    range_m = range_nm * 1852
                    writer.writerow([f"{range_nm:.4f}", f"{range_m:.1f}", f"{val:.4f}"])

        return filepath

    def get_record_count(self) -> int:
        """Get number of recorded sweeps."""
        return len(self.records)

    def is_active(self) -> bool:
        """Check if recording is active."""
        return self.is_recording
