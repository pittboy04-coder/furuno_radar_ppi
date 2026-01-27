# Furuno Radar PPI Simulator

A Python-based marine radar simulator that generates realistic Plan Position Indicator (PPI) displays with coastline returns, vessel targets, and environmental effects. Designed for developing and testing small object detection algorithms in maritime environments.

## Features

- **Real-time PPI display** with rotating antenna sweep
- **Coastline/landmass simulation** with ray-segment intersection for realistic radar returns
- **Target modeling** for vessels, buoys, and small craft with aspect-dependent RCS
- **Environmental effects**: sea clutter, rain clutter, and thermal noise
- **Adjustable radar parameters**: gain, range scale, sea/rain clutter rejection
- **Scenario presets**: Open ocean, harbor approach, and more
- **CSV data export** compatible with the [radar_plotter](https://github.com/) PPI visualizer
  - Angle in ticks (8192 = 360 degrees)
  - Gain code (0-255)
  - Range in meters
  - Echo bin values per sweep

## Requirements

- Python 3.8+
- pygame >= 2.5.0
- numpy >= 1.24.0

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/furuno_radar_ppi.git
cd furuno_radar_ppi
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| SPACE | Pause/Resume simulation |
| R | Reset scenario |
| C | Toggle coastline display |
| F5 | Start/Stop recording to CSV |
| E | Export current sweep to CSV |
| +/- | Adjust simulation speed |
| Mouse wheel | Zoom in/out |
| ESC | Exit |

## Project Structure

```
furuno_radar_ppi/
├── main.py                         # Application entry point
├── requirements.txt
├── radar_sim/
│   ├── core/
│   │   ├── range_bearing.py        # Geometry utilities
│   │   ├── world.py                # World container
│   │   └── simulation.py           # Main simulation engine
│   ├── objects/
│   │   └── vessel.py               # Vessel class with RCS modeling
│   ├── radar/
│   │   ├── parameters.py           # Radar configuration (DRS-series specs)
│   │   ├── antenna.py              # Antenna rotation and beam pattern
│   │   ├── detection.py            # Target detection logic
│   │   └── system.py               # Integrated radar system
│   ├── environment/
│   │   ├── noise.py                # Thermal noise generation
│   │   ├── clutter.py              # Sea and rain clutter
│   │   ├── coastline.py            # Coastline geometry and returns
│   │   └── weather.py              # Weather effects
│   ├── visualization/
│   │   └── ppi_display.py          # PPI radar display renderer
│   ├── ui/
│   │   ├── widgets.py              # UI components (buttons, sliders, dropdowns)
│   │   └── control_panel.py        # Control panel layout
│   ├── scenarios/
│   │   ├── scenario_manager.py     # Scenario loading
│   │   └── presets.py              # Built-in scenario configurations
│   └── data_export.py              # CSV export (radar_plotter compatible)
└── tests/
    ├── test_geometry.py
    ├── test_vessel.py
    ├── test_world.py
    ├── test_radar.py
    └── test_scenarios.py
```

## CSV Export Format

Exported CSV files are compatible with PPI visualization tools. Format:

```csv
timestamp,unused,range_m,gain_code,angle_ticks,bin_0,bin_1,...
0.000,0,11112,127,0.00,0.0123,0.0456,...
0.017,0,11112,127,22.76,0.0234,0.0567,...
```

- `angle_ticks`: 8192 ticks = 360 degrees
- `gain_code`: 0-255 integer
- `range_m`: range scale in meters
- `bin_N`: echo intensity (0.0 - 1.0)

## License

MIT
