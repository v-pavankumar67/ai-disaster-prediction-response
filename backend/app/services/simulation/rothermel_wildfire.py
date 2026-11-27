"""Rothermel Wildfire Surface Rate of Spread Simulation."""

import math
from typing import Dict, List, Any, Tuple


class RothermelFireSimulator:
    """Simulates dynamic wildfire front expansion based on wind direction, velocity, and fuel aridity."""

    def __init__(self):
        pass

    def run_simulation(
        self,
        center_lat: float,
        center_lon: float,
        total_hours: int = 48,
        time_step_hours: float = 3.0,
        wind_speed_kmh: float = 40.0,
        wind_direction_deg: float = 225.0  # coming from SW blowing NE
    ) -> Tuple[List[Dict[str, Any]], float, int]:
        """Propagates an elliptical fire perimeter over time."""
        steps_data: List[Dict[str, Any]] = []
        num_steps = int(total_hours / time_step_hours)

        # Wind drift angle in radians
        rad = math.radians((wind_direction_deg + 180) % 360)
        drift_x = math.sin(rad)
        drift_y = math.cos(rad)

        base_spread_km_per_hour = 0.35 + (wind_speed_kmh / 50.0) * 0.45

        for step in range(num_steps):
            current_hour = (step + 1) * time_step_hours
            major_radius_km = base_spread_km_per_hour * current_hour * 1.4
            minor_radius_km = major_radius_km * 0.45

            # Center shifts in direction of wind
            shift_lat = (drift_y * major_radius_km * 0.4) / 111.0
            shift_lon = (drift_x * major_radius_km * 0.4) / (111.0 * math.cos(math.radians(center_lat)))

            fire_perimeter_cells = []
            num_perimeter_points = 16
            for p in range(num_perimeter_points):
                angle = 2.0 * math.pi * (p / num_perimeter_points)
                # Ellipse point
                px = math.cos(angle) * minor_radius_km
                py = math.sin(angle) * major_radius_km
                # Rotate ellipse to match wind angle
                rot_x = px * math.cos(rad) - py * math.sin(rad)
                rot_y = px * math.sin(rad) + py * math.cos(rad)

                plat = center_lat + shift_lat + (rot_y / 111.0)
                plon = center_lon + shift_lon + (rot_x / (111.0 * math.cos(math.radians(center_lat))))

                fire_perimeter_cells.append({
                    "lat": round(plat, 5),
                    "lon": round(plon, 5),
                    "fire_intensity_kw_m": round(1200.0 + current_hour * 80.0, 1),
                    "severity": "critical" if current_hour > 12 else "high"
                })

            steps_data.append({
                "step_index": step,
                "hour": current_hour,
                "inundated_count": len(fire_perimeter_cells),
                "cells": fire_perimeter_cells
            })

        final_area_sq_km = math.pi * (major_radius_km) * (minor_radius_km)
        affected_pop = int(final_area_sq_km * 45)

        return steps_data, round(final_area_sq_km, 2), affected_pop
