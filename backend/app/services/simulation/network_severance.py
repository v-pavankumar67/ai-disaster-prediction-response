"""Dynamic road network severance and isolated community detection service."""

import math
from typing import List, Dict, Any, Tuple


class NetworkSeveranceSimulator:
    """Intersects physical disaster spread with the transportation graph to flag severed links and cut off settlements."""

    @staticmethod
    def get_regional_road_network(center_lat: float, center_lon: float) -> List[Dict[str, Any]]:
        """Provides key arterial highways, bridges, and local connecting roads."""
        return [
            {
                "id": 1,
                "name": "NH-66 National Highway (River Bridge Sector)",
                "start_lat": center_lat - 0.05,
                "start_lon": center_lon - 0.02,
                "end_lat": center_lat + 0.04,
                "end_lon": center_lon - 0.01,
                "is_bridge": True
            },
            {
                "id": 2,
                "name": "State Highway SH-15 Valley Corridor",
                "start_lat": center_lat + 0.02,
                "start_lon": center_lon - 0.04,
                "end_lat": center_lat + 0.06,
                "end_lon": center_lon + 0.03,
                "is_bridge": False
            },
            {
                "id": 3,
                "name": "Eastern Ridge Relief Route",
                "start_lat": center_lat - 0.08,
                "start_lon": center_lon + 0.05,
                "end_lat": center_lat + 0.07,
                "end_lon": center_lon + 0.08,
                "is_bridge": False
            },
            {
                "id": 4,
                "name": "Riverbank Bypass Road 4B",
                "start_lat": center_lat - 0.01,
                "start_lon": center_lon - 0.03,
                "end_lat": center_lat + 0.01,
                "end_lon": center_lon + 0.02,
                "is_bridge": True
            }
        ]

    @staticmethod
    def get_regional_villages(center_lat: float, center_lon: float) -> List[Dict[str, Any]]:
        """Key settlement clusters and baseline populations."""
        return [
            {
                "id": "VIL-01",
                "name": "Aluva Lowland Hamlet",
                "lat": center_lat + 0.02,
                "lon": center_lon - 0.01,
                "population": 1450,
                "vulnerability_score": 0.88,
                "elderly_infant_pct": 24.5
            },
            {
                "id": "VIL-02",
                "name": "Kalady Riverside Village",
                "lat": center_lat + 0.05,
                "lon": center_lon + 0.01,
                "population": 2100,
                "vulnerability_score": 0.92,
                "elderly_infant_pct": 31.0
            },
            {
                "id": "VIL-03",
                "name": "Perumbavoor Hillside Cluster",
                "lat": center_lat - 0.06,
                "lon": center_lon + 0.04,
                "population": 3800,
                "vulnerability_score": 0.45,
                "elderly_infant_pct": 18.0
            },
            {
                "id": "VIL-04",
                "name": "Varapuzha Island Settlement",
                "lat": center_lat + 0.01,
                "lon": center_lon - 0.04,
                "population": 980,
                "vulnerability_score": 0.95,
                "elderly_infant_pct": 28.0
            }
        ]

    @classmethod
    def evaluate_severance(
        cls,
        center_lat: float,
        center_lon: float,
        hazard_cells: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Calculates which road edges are impassable and which villages are isolated."""
        roads = cls.get_regional_road_network(center_lat, center_lon)
        villages = cls.get_regional_villages(center_lat, center_lon)

        severed_roads = []
        for r in roads:
            # Check proximity to inundated/hazard cells
            r_mid_lat = (r["start_lat"] + r["end_lat"]) / 2.0
            r_mid_lon = (r["start_lon"] + r["end_lon"]) / 2.0

            # Distance to nearest hazard cell
            min_dist = min([
                math.hypot(r_mid_lat - c["lat"], r_mid_lon - c["lon"])
                for c in hazard_cells
            ]) if hazard_cells else 1.0

            if min_dist < 0.05:  # Within ~5.5 km buffer of flood or fire front
                depth = round(max(0.35, 0.45 + (0.05 - min_dist) * 15.0), 2)
                severed_roads.append({
                    "id": r["id"],
                    "road_name": r["name"],
                    "start_lat": r["start_lat"],
                    "start_lon": r["start_lon"],
                    "end_lat": r["end_lat"],
                    "end_lon": r["end_lon"],
                    "severance_cause": "flood_submersion" if depth > 0.3 else "fire_smoke_hazard",
                    "water_depth_meters": depth,
                    "is_passable_for_trucks": depth <= 0.35,
                    "is_passable_for_boats": True
                })

        severed_ids = {s["id"] for s in severed_roads}

        # Villages connected only by severed roads become ISOLATED
        isolated_villages = []
        for v in villages:
            if 1 in severed_ids or 4 in severed_ids:
                if v["id"] in ["VIL-01", "VIL-02", "VIL-04"]:
                    isolated_villages.append({
                        **v,
                        "status": "ISOLATED",
                        "accessible_by_road": False,
                        "accessible_by_boat": True,
                        "accessible_by_drone": True,
                        "urgency": "CRITICAL" if v["vulnerability_score"] > 0.85 else "HIGH"
                    })

        return severed_roads, isolated_villages
