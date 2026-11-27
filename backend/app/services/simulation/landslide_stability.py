"""Landslide and Slope Stability Factor of Safety (FS) Simulator."""

import math
from typing import Dict, List, Any


class LandslideSlopeSimulator:
    """Calculates geotechnical Factor of Safety (FS) for steep terrain sectors."""

    @staticmethod
    def calculate_factor_of_safety(
        slope_angle_deg: float,
        soil_cohesion_kpa: float = 12.0,
        soil_unit_weight_kn_m3: float = 19.0,
        friction_angle_deg: float = 32.0,
        depth_m: float = 2.5,
        water_table_ratio: float = 0.85
    ) -> float:
        """
        Infinite Slope Model Factor of Safety:
        FS = (c' + (gamma - gamma_w * m) * z * cos^2(theta) * tan(phi)) / (gamma * z * sin(theta) * cos(theta))
        FS < 1.0 means imminent failure / landslide.
        """
        theta = math.radians(slope_angle_deg)
        phi = math.radians(friction_angle_deg)
        gamma_w = 9.81  # water unit weight kN/m3
        gamma = soil_unit_weight_kn_m3
        z = depth_m
        m = water_table_ratio

        numerator = soil_cohesion_kpa + (gamma - gamma_w * m) * z * (math.cos(theta)**2) * math.tan(phi)
        denominator = gamma * z * math.sin(theta) * math.cos(theta)

        if denominator <= 0.001:
            return 9.9
        fs = numerator / denominator
        return round(float(fs), 2)
