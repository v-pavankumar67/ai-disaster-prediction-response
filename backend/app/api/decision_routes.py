"""Decision Support and Operational Triage API routes."""

from fastapi import APIRouter, Query
from backend.app.services.simulation.network_severance import NetworkSeveranceSimulator

router = APIRouter(prefix="/decision", tags=["Operational Decision & Triage"])


@router.get("/triage-summary", summary="Get triage ranking of affected communities")
def get_triage_summary(lat: float = Query(9.9312), lon: float = Query(76.2673)):
    villages = NetworkSeveranceSimulator.get_regional_villages(lat, lon)
    # Calculate Evacuation Priority Score (EPS)
    scored = []
    for v in villages:
        eps = round(v["population"] * 0.4 + v["vulnerability_score"] * 1000 * 0.6, 1)
        scored.append({
            **v,
            "evacuation_priority_score": eps,
            "priority_tier": "P1 - CRITICAL" if eps > 1000 else "P2 - URGENT"
        })
    scored.sort(key=lambda x: x["evacuation_priority_score"], reverse=True)
    return {
        "region_center": {"lat": lat, "lon": lon},
        "communities_count": len(scored),
        "triage_ranking": scored
    }


@router.get("/infrastructure-status", summary="Get critical bridges, hospitals, and highways status")
def get_infrastructure_status(lat: float = Query(9.9312), lon: float = Query(76.2673)):
    roads = NetworkSeveranceSimulator.get_regional_road_network(lat, lon)
    return {
        "critical_corridors": roads,
        "designated_airfields": [
            {"name": "Cochin Naval Air Station (Relief Hub Alpha)", "lat": lat - 0.03, "lon": lon - 0.05, "status": "OPERATIONAL"}
        ],
        "district_hospitals": [
            {"name": "General Hospital Ernakulam", "lat": lat + 0.01, "lon": lon - 0.02, "status": "ACTIVE_TRIAGE", "bed_capacity": 650}
        ]
    }
