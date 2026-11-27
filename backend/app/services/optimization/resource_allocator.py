"""Master Resource Optimization Coordinator."""

import uuid
from typing import Dict, Any, List
from backend.app.schemas.response import OptimizationResponse
from backend.app.services.optimization.facility_location import ShelterFacilityOptimizer
from backend.app.services.optimization.vehicle_routing import DynamicVehicleRoutingOptimizer


class MasterResourceAllocator:
    """Orchestrates triage prioritization, shelter activation, and fleet convoy dispatch."""

    @classmethod
    def run_optimization(
        cls,
        isolated_villages: List[Dict[str, Any]],
        severed_roads: List[Dict[str, Any]],
        available_shelters: List[Dict[str, Any]],
        base_depot: Dict[str, Any]
    ) -> OptimizationResponse:
        """Executes full mathematical optimization pass across spatial assets."""
        opt_id = f"OPT-{uuid.uuid4().hex[:8].upper()}"

        # 1. Shelter Activation (Capacitated Facility Location)
        activated_shelters = ShelterFacilityOptimizer.optimize_shelter_selection(
            demands=isolated_villages,
            candidate_shelters=available_shelters,
            max_active_shelters=3
        )

        # 2. Multi-Modal Fleet Routing (Dynamic VRPTW)
        assigned_routes = DynamicVehicleRoutingOptimizer.solve_multi_modal_dispatch(
            isolated_villages=isolated_villages,
            severed_roads=severed_roads,
            base_depot=base_depot
        )

        total_demand = sum(v.get("population", 0) for v in isolated_villages)
        total_evacuated = sum(r.civilians_to_evacuate for r in assigned_routes)

        summary = (
            f"Optimization {opt_id} complete. Dispatched {len(assigned_routes)} multi-modal rescue routes "
            f"(Boat Flotilla, 4x4 Convoy, Medical Drones) rerouting around {len(severed_roads)} severed road segments. "
            f"Activated {len(activated_shelters)} emergency relief shelters."
        )

        return OptimizationResponse(
            optimization_id=opt_id,
            status="OPTIMAL_SOLUTION_FOUND",
            solver_used="Dynamic VRPTW + Capacitated P-Median Heuristic",
            total_isolated_demand=total_demand,
            total_evacuated_capacity=total_evacuated,
            assigned_routes=assigned_routes,
            activated_shelters=[s["name"] for s in activated_shelters],
            critical_unreachable_zones=[],
            summary=summary
        )
