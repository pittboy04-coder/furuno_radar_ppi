#!/usr/bin/env python3
"""Furuno Radar PPI Simulator - Main Entry Point."""
import sys
import os
import pygame
from radar_sim.core.simulation import Simulation
from radar_sim.visualization.ppi_display import PPIDisplay
from radar_sim.visualization.scene_view import SceneView
from radar_sim.ui.control_panel import ControlPanel
from radar_sim.scenarios.scenario_manager import ScenarioManager
from radar_sim.scenarios.presets import PRESET_SCENARIOS

# Window settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
PPI_SIZE = 600
FPS = 60

def main():
    """Main application entry point."""
    pygame.init()
    pygame.display.set_caption("Furuno Radar PPI Simulator")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # Initialize simulation
    sim = Simulation()

    # Set export directory - platform-specific
    import platform
    if platform.system() == 'Windows':
        export_dir = r"C:\Users\Noah\OneDrive - Strategy Communications\Desktop\maritime_radar_sim"
    else:
        export_dir = os.path.expanduser("~/projects/radar-research/Radar Simulator CSV Outputs")
    os.makedirs(export_dir, exist_ok=True)
    sim.exporter.output_dir = export_dir

    # Initialize scenario manager with presets
    scenario_manager = ScenarioManager()
    scenario_manager.register_scenarios(PRESET_SCENARIOS)

    # Load the first scenario
    scenario_manager.load_scenario(
        PRESET_SCENARIOS[0].name,
        sim.world,
        sim.radar,
        sim.weather
    )

    # Layout calculation
    CONTROL_PANEL_WIDTH = 340
    MIN_PPI_SIZE = 300

    def calc_layout(win_w, win_h):
        """Calculate display sizes and positions from window dimensions."""
        # PPI and scene view share the space left of the control panel
        available = win_w - CONTROL_PANEL_WIDTH - 30  # margins
        display_size = min(win_h - 40, (available - 20) // 2)
        display_size = max(MIN_PPI_SIZE, display_size)
        px = 10
        py = (win_h - display_size) // 2
        sx = display_size + 20
        sy = py
        cp_x = display_size * 2 + 30
        cp_w = win_w - cp_x - 10
        return display_size, px, py, sx, sy, cp_x, cp_w, win_h - 40

    display_size, ppi_x, ppi_y, scene_x, scene_y, cp_x, cp_w, cp_h = calc_layout(WINDOW_WIDTH, WINDOW_HEIGHT)

    # Initialize PPI display
    ppi = PPIDisplay(size=display_size)
    ppi.initialize()
    ppi.set_ppi_offset(ppi_x, ppi_y)

    # Initialize scene view
    scene_view = SceneView(size=display_size)

    # Initialize control panel
    control_panel = ControlPanel(
        x=cp_x,
        y=20,
        width=cp_w,
        height=cp_h
    )
    control_panel.set_simulation(sim)
    control_panel.set_scenario_manager(scenario_manager)

    # Range scale indices for mouse wheel zooming
    range_scales = sim.radar.params.range_scales_nm
    current_range_idx = range_scales.index(sim.radar.params.current_range_nm) if sim.radar.params.current_range_nm in range_scales else 5

    # Main loop
    running = True
    last_bearing = 0.0

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    sim.toggle_pause()
                elif event.key == pygame.K_r:
                    sim.reset()
                    sim.setup_default_scenario()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    sim.set_time_scale(sim.time_scale * 1.5)
                elif event.key == pygame.K_MINUS:
                    sim.set_time_scale(sim.time_scale / 1.5)
                elif event.key == pygame.K_F5:
                    # Toggle recording
                    if sim.is_recording():
                        filepath = sim.stop_recording()
                        print(f"Recording saved to: {filepath}")
                    else:
                        session_id = sim.start_recording()
                        print(f"Recording started: {session_id}")
                elif event.key == pygame.K_c:
                    # Toggle coastline
                    if sim.coastline_enabled:
                        sim.clear_coastlines()
                    else:
                        sim.setup_harbor_coastline()
                elif event.key == pygame.K_e:
                    # Export current sweep
                    filepath = sim.export_current_sweep(current_bearing)
                    print(f"Sweep exported to: {filepath}")

            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
                if win_w < 100 or win_h < 100:
                    continue
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                display_size, ppi_x, ppi_y, scene_x, scene_y, cp_x, cp_w, cp_h = calc_layout(win_w, win_h)
                ppi = PPIDisplay(size=display_size)
                ppi.initialize()
                ppi.set_ppi_offset(ppi_x, ppi_y)
                scene_view = SceneView(size=display_size)
                control_panel = ControlPanel(x=cp_x, y=20, width=cp_w, height=cp_h)
                control_panel.set_simulation(sim)
                control_panel.set_scenario_manager(scenario_manager)

            elif event.type == pygame.MOUSEMOTION:
                # Track cursor position for PPI
                ppi.handle_mouse_motion(event.pos[0], event.pos[1])

            elif event.type == pygame.MOUSEWHEEL:
                # Zoom in/out with mouse wheel when over PPI
                mouse_pos = pygame.mouse.get_pos()
                if ppi.screen_to_polar(mouse_pos[0], mouse_pos[1]) is not None:
                    if event.y > 0 and current_range_idx > 0:
                        current_range_idx -= 1
                        sim.radar.set_range_scale(range_scales[current_range_idx])
                    elif event.y < 0 and current_range_idx < len(range_scales) - 1:
                        current_range_idx += 1
                        sim.radar.set_range_scale(range_scales[current_range_idx])

            # Pass events to control panel
            control_panel.handle_event(event)

        # Skip rendering when minimized
        if pygame.display.get_surface().get_size()[0] == 0:
            clock.tick(FPS)
            continue

        # CSV playback mode or normal simulation
        sweep_pairs = None
        if control_panel.csv_player and control_panel.csv_player.active:
            sweep_pairs = control_panel.csv_player.get_next_sweeps()
            for bearing, data in sweep_pairs:
                ppi.draw_sweep_data(bearing, data)
        else:
            # Update simulation
            sim.update()

            # Get current radar state
            current_bearing = sim.radar.get_current_bearing()

            # Update PPI display with new sweep data
            if int(current_bearing) != int(last_bearing):
                sweep_data = sim.get_radar_sweep_data(current_bearing)
                ppi.draw_sweep_data(current_bearing, sweep_data)

                # Update heading display
                if sim.world.own_ship:
                    ppi.set_heading(sim.world.own_ship.course)

            ppi.set_range(sim.radar.params.current_range_nm)
            last_bearing = current_bearing

        # Render
        screen.fill((20, 20, 30))

        # Draw PPI
        ppi_surface = ppi.render()
        screen.blit(ppi_surface, (ppi_x, ppi_y))

        # Draw scene view
        if sweep_pairs is not None:
            scene_surface = scene_view.render_csv(
                sweep_pairs, sim.radar.params.current_range_nm)
        else:
            scene_surface = scene_view.render(
                sim.world.own_ship, sim.world.get_all_vessels(),
                sim.coastlines, sim.radar.params.current_range_nm)
        screen.blit(scene_surface, (scene_x, scene_y))

        # Draw cursor info below PPI
        ppi.draw_cursor_info(screen, ppi_x, ppi_y + PPI_SIZE + 5)

        # Draw control panel
        control_panel.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
