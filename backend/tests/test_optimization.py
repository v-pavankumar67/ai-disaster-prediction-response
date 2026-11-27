"""Unit tests for facility location and dynamic vehicle routing."""

import pytest
from backend.app.services.optimization.facility_location import ShelterFacilityOptimizer
from backend.app.services.optimization.vehicle_routing import DynamicVehicleRoutingOptimizer
from backend.app.services.optimization.resource_allocator import MasterResourceAllocator


def test_shelter_optimization():
    demands = [
        {"lat": 10.05, "lon": 76.35, "population": 1500},
        {"lat": 10.08, "lon": 76.38, "population": 2200}
    ]
    candidates = [
        {"id": 1, "name": "Shelter A", "latitude": 10.06, "longitude": 76.36, "total_capacity": 3000},
        {"id": 2, "name": "Shelter B", "latitude": 10.20, "longitude": 76.50, "total_capacity": 1000}
    ]
    activated = ShelterFacilityOptimizer.optimize_shelter_selection(demands, candidates, max_active_shelters=1)
    assert len(activated) == 1
    assert activated[0]["id"] == 1  # Closer shelter should be prioritized


def test_multi_modal_routing():
    isolated = [
        {"id": "VIL-01", "name": "Aluva Lowland", "lat": 10.07, "lon": 76.34, "population": 1200},
        {"id": "VIL-02", "name": "Kalady Riverside", "lat": 10.10, "lon": 76.36, "population": 1800}
    ]
    severed = [{"id": 1, "road_name": "NH-66 Bridge", "water_depth_meters": 0.8}]
    base = {"name": "Central Depot", "latitude": 10.05, "longitude": 76.35}

    routes = DynamicVehicleRoutingOptimizer.solve_multi_modal_dispatch(isolated, severed, base)
    assert len(routes) >= 2  # Should generate both watercraft and road/drone routes
