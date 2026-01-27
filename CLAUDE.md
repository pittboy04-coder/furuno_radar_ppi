# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Furuno Radar PPI Simulator - A Python application for simulating and displaying marine radar data in a Plan Position Indicator (PPI) format. Uses pygame for real-time visualization.

## Build Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the simulator
python main.py

# Run tests
python -m pytest tests/

# Run a single test
python -m pytest tests/test_file.py::test_name
```

## Architecture

```
radar_sim/
├── core/
│   ├── range_bearing.py    # Geometry utilities
│   ├── world.py            # World container for vessels
│   └── simulation.py       # Main simulation engine
├── objects/
│   └── vessel.py           # Vessel class
├── radar/
│   ├── parameters.py       # Radar configuration
│   ├── antenna.py          # Antenna simulation
│   ├── detection.py        # Target detection
│   └── system.py           # Integrated radar system
├── environment/
│   ├── noise.py            # Noise generation
│   ├── clutter.py          # Sea/rain clutter
│   └── weather.py          # Weather effects
├── visualization/
│   └── ppi_display.py      # PPI radar display
└── ui/
    ├── widgets.py          # UI components
    └── control_panel.py    # Control panel

main.py                     # Application entry point
```

## Key Controls

- **SPACE**: Pause/Resume simulation
- **R**: Reset scenario
- **+/-**: Adjust simulation speed
- **C**: Toggle coastline/landmass
- **F5**: Start/Stop recording radar data to CSV
- **E**: Export current sweep to CSV
- **ESC**: Exit
- **Mouse wheel**: Zoom in/out on PPI

## Data Export

CSV files are saved to the current working directory with:
- Timestamp, bearing, range scale, gain, clutter settings
- Echo values for each range bin (0-1 intensity)

Files:
- `radar_data_YYYYMMDD_HHMMSS.csv` - Full recording
- `sweep_YYYYMMDD_HHMMSS_bearingXXX.csv` - Single sweep export
