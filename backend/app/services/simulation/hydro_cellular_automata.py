"""2D Hydrological Cellular Automata Flood Inundation Simulator."""

import math
import numpy as np
from typing import Dict, List, Any, Tuple


class HydroCellularAutomataSimulator:
    """Simulates 2D overland water runoff and river overflow dynamics across topography."""

    def __init__(self, grid_size: int = 20, cell_spacing_m: float = 250.0):
        self.grid_size = grid_size
        self.cell_spacing_m = cell_spacing_m

    def generate_synthetic_dem(self) -> np.ndarray:
        """Constructs a realistic valley basin with a meandering river channel."""
        x = np.linspace(-3, 3, self.grid_size)
        y = np.linspace(-3, 3, self.grid_size)
        xx, yy = np.meshgrid(x, y)
        # Valley bowl + slight slope southward + river trench down center
        elevation = 25.0 + 8.0 * (xx**2) + 2.0 * yy
        # River trench through center column
        center_col = self.grid_size // 2
        elevation[:, center_col - 1:center_col + 2] -= 4.0
        return elevation

    def run_simulation(
        self,
        center_lat: float,
        center_lon: float,
        total_hours: int = 48,
        time_step_hours: float = 3.0,
        rain_intensity_mm_h: float = 75.0,
        dam_breach: bool = True
    ) -> Tuple[List[Dict[str, Any]], float, int]:
        """Executes hydro CA timesteps and outputs spatial water propagation."""
        dem = self.generate_synthetic_dem()
        water_depth = np.zeros_like(dem)

        steps_data: List[Dict[str, Any]] = []
        num_steps = int(total_hours / time_step_hours)

        lat_step = 0.008  # ~900m per grid cell
        lon_step = 0.008

        for step in range(num_steps):
            current_hour = (step + 1) * time_step_hours

            # Inflow: rain falling uniformly across grid
            rain_depth_m = (rain_intensity_mm_h / 1000.0) * time_step_hours
            water_depth += rain_depth_m * 0.7  # 70% runoff coefficient

            # River/Dam burst surge injected at upper center cells
            if dam_breach and step >= 1:
                water_depth[0:3, self.grid_size // 2 - 1:self.grid_size // 2 + 2] += 1.8

            # Cellular Automata 2D hydraulic head diffusion
            head = dem + water_depth
            diffused_depth = np.copy(water_depth)

            for i in range(1, self.grid_size - 1):
                for j in range(1, self.grid_size - 1):
                    if water_depth[i, j] <= 0.05:
                        continue
                    current_head = head[i, j]
                    neighbors = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
                    lower_neighbors = [(ni, nj) for ni, nj in neighbors if head[ni, nj] < current_head]

                    if lower_neighbors:
                        head_diffs = [current_head - head[ni, nj] for ni, nj in lower_neighbors]
                        sum_diff = sum(head_diffs)
                        transfer_volume = min(water_depth[i, j] * 0.45, sum_diff * 0.25)
                        diffused_depth[i, j] -= transfer_volume
                        for (ni, nj), diff in zip(lower_neighbors, head_diffs):
                            diffused_depth[ni, nj] += transfer_volume * (diff / sum_diff)

            water_depth = np.maximum(0.0, diffused_depth)

            # Extract inundated cells (>0.3m is hazardous)
            inundated_cells = []
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    depth = float(water_depth[i, j])
                    if depth > 0.25:
                        cell_lat = center_lat + (i - self.grid_size // 2) * lat_step
                        cell_lon = center_lon + (j - self.grid_size // 2) * lon_step
                        inundated_cells.append({
                            "grid_i": i,
                            "grid_j": j,
                            "lat": round(cell_lat, 5),
                            "lon": round(cell_lon, 5),
                            "water_depth_m": round(depth, 2),
                            "severity": "critical" if depth > 1.2 else ("high" if depth > 0.6 else "moderate")
                        })

            steps_data.append({
                "step_index": step,
                "hour": current_hour,
                "inundated_count": len(inundated_cells),
                "cells": inundated_cells
            })

        final_inundated_cells = steps_data[-1]["cells"]
        submerged_sq_km = len(final_inundated_cells) * (self.cell_spacing_m / 1000.0) ** 2
        affected_population = int(len(final_inundated_cells) * 280)  # average density multiplier

        return steps_data, round(submerged_sq_km, 2), affected_population
