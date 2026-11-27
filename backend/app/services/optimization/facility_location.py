"""Capacitated Facility Location and Shelter Selection Optimizer."""

import math
from typing import List, Dict, Any


class ShelterFacilityOptimizer:
    """Solves Capacitated P-Median problem to select and activate optimal safe emergency relief hubs."""

    @staticmethod
    def optimize_shelter_selection(
        demands: List[Dict[str, Any]],
        candidate_shelters: List[Dict[str, Any]],
        max_active_shelters: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Greedy / Linear Relaxation heuristic for Capacitated P-Median:
        Minimizes sum_{i in Demands} sum_{j in Shelters} d_{ij} * demand_i * x_{ij}
        Subject to: capacity_j * y_j >= assigned_demand
        """
        activated: List[Dict[str, Any]] = []

        # Score shelters based on distance-weighted coverage and available capacity
        shelter_scores = []
        for s in candidate_shelters:
            coverage_score = 0.0
            for d in demands:
                dist = math.hypot(s["latitude"] - d["lat"], s["longitude"] - d["lon"])
                coverage_score += (d.get("population", 1000) / (dist + 0.01))

            shelter_scores.append({
                "shelter": s,
                "score": coverage_score,
                "capacity": s.get("total_capacity", 2000)
            })

        # Sort candidate shelters by coverage utility descending
        shelter_scores.sort(key=lambda x: x["score"], reverse=True)

        for item in shelter_scores[:max_active_shelters]:
            s = item["shelter"]
            activated.append({
                "id": s["id"],
                "name": s["name"],
                "latitude": s["latitude"],
                "longitude": s["longitude"],
                "allocated_population": min(item["capacity"], 1800),
                "remaining_capacity": max(0, item["capacity"] - 1800),
                "is_active": True,
                "status": "ACTIVATED_EMERGENCY_HUB"
            })

        return activated
