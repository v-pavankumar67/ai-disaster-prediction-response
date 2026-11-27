"""Resource Optimization and Fleet Routing API routes."""

from fastapi import APIRouter, Body
from backend.app.schemas.response import OptimizationRequest, OptimizationResponse
from backend.app.services.optimization.resource_allocator import MasterResourceAllocator
from backend.app.services.simulation.network_severance import NetworkSeveranceSimulator

router = APIRouter(prefix="/optimization", tags=["Resource Optimization & Fleet Dispatch"])


@router.post("/dispatch-fleet", response_model=OptimizationResponse, summary="Optimize rescue fleet dispatch and shelter assignments")
def optimize_dispatch(req: OptimizationRequest = Body(...)):
    center_lat, center_lon = 9.9312, 76.2673

    # Baseline candidate shelters
    candidate_shelters = [
        {"id": 1, "name": "Aluva St. Xavier Auditorium (Shelter Alpha)", "latitude": center_lat + 0.04, "longitude": center_lon + 0.02, "total_capacity": 2500},
        {"id": 2, "name": "Rajiv Gandhi Indoor Stadium (Shelter Bravo)", "latitude": center_lat - 0.03, "longitude": center_lon - 0.02, "total_capacity": 4000},
        {"id": 3, "name": "Hill Valley Relief Camp (Shelter Charlie)", "latitude": center_lat - 0.07, "longitude": center_lon + 0.06, "total_capacity": 1800}
    ]

    base_depot = {
        "name": "Central Emergency Operations Center & Marine Dock",
        "latitude": center_lat,
        "longitude": center_lon
    }

    # Fetch isolated communities & severed roads
    roads, isolated_villages = NetworkSeveranceSimulator.evaluate_severance(
        center_lat=center_lat,
        center_lon=center_lon,
        hazard_cells=[{"lat": center_lat + 0.01, "lon": center_lon - 0.01}]
    )

    result = MasterResourceAllocator.run_optimization(
        isolated_villages=isolated_villages,
        severed_roads=roads,
        available_shelters=candidate_shelters,
        base_depot=base_depot
    )
    return result


@router.get("/shelters", summary="List designated emergency relief shelters")
def get_shelters():
    center_lat, center_lon = 9.9312, 76.2673
    return [
        {"id": 1, "name": "Aluva St. Xavier Auditorium (Shelter Alpha)", "latitude": center_lat + 0.04, "longitude": center_lon + 0.02, "total_capacity": 2500, "current_occupancy": 320, "has_medical": True},
        {"id": 2, "name": "Rajiv Gandhi Indoor Stadium (Shelter Bravo)", "latitude": center_lat - 0.03, "longitude": center_lon - 0.02, "total_capacity": 4000, "current_occupancy": 840, "has_medical": True},
        {"id": 3, "name": "Hill Valley Relief Camp (Shelter Charlie)", "latitude": center_lat - 0.07, "longitude": center_lon + 0.06, "total_capacity": 1800, "current_occupancy": 150, "has_medical": False}
    ]


@router.get("/rescue-fleet", summary="List available emergency response vehicles")
def get_rescue_fleet():
    center_lat, center_lon = 9.9312, 76.2673
    return [
        {"callsign": "RESCUE-BOAT-FLOTILLA-A", "type": "inflatable_boat", "capacity": 60, "status": "READY_FOR_DISPATCH", "base": "Marine Staging Dock"},
        {"callsign": "TRUCK-CONVOY-BRAVO", "type": "4x4_truck", "capacity": 85, "status": "READY_FOR_DISPATCH", "base": "Logistics Depot"},
        {"callsign": "AERO-DRONE-SQUADRON-X", "type": "drone", "capacity": 12, "status": "READY_FOR_DISPATCH", "base": "Hospital Helipad"},
        {"callsign": "MEDEVAC-HELI-ONE", "type": "helicopter", "capacity": 8, "status": "STANDBY", "base": "Naval Air Station"}
    ]
