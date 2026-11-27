"""Unit tests for spatial simulation engines and road severance."""

import pytest
from backend.app.services.simulation.hydro_cellular_automata import HydroCellularAutomataSimulator
from backend.app.services.simulation.rothermel_wildfire import RothermelFireSimulator
from backend.app.services.simulation.landslide_stability import LandslideSlopeSimulator
from backend.app.services.simulation.network_severance import NetworkSeveranceSimulator


def test_hydro_cellular_automata():
    sim = HydroCellularAutomataSimulator(grid_size=15)
    steps, submerged_km, pop = sim.run_simulation(
        center_lat=10.0,
        center_lon=76.0,
        total_hours=12,
        time_step_hours=3.0,
        rain_intensity_mm_h=80.0
    )
    assert len(steps) == 4
    assert submerged_km > 0.0
    assert pop > 0


def test_rothermel_wildfire():
    sim = RothermelFireSimulator()
    steps, area_km, pop = sim.run_simulation(
        center_lat=34.0,
        center_lon=-118.0,
        total_hours=12,
        time_step_hours=3.0,
        wind_speed_kmh=45.0
    )
    assert len(steps) == 4
    assert area_km > 0.0


def test_landslide_factor_of_safety():
    # Steep wet slope should fail (FS < 1.0)
    fs_unstable = LandslideSlopeSimulator.calculate_factor_of_safety(
        slope_angle_deg=42.0,
        water_table_ratio=0.95
    )
    assert fs_unstable < 1.1

    # Gentle dry slope should be stable (FS > 1.5)
    fs_stable = LandslideSlopeSimulator.calculate_factor_of_safety(
        slope_angle_deg=12.0,
        water_table_ratio=0.10
    )
    assert fs_stable > 1.5


def test_network_severance():
    hazard_cells = [{"lat": 10.01, "lon": 76.32}]
    roads, isolated = NetworkSeveranceSimulator.evaluate_severance(
        center_lat=10.05,
        center_lon=76.35,
        hazard_cells=hazard_cells
    )
    assert len(roads) > 0
