"""Spatial Impact Simulation API routes."""

from fastapi import APIRouter, Body
from datetime import datetime
from backend.app.schemas.simulation import SimulationRequest, SimulationResponse, SeveredRoadResponse, SimulationStepData
from backend.app.services.simulation.hydro_cellular_automata import HydroCellularAutomataSimulator
from backend.app.services.simulation.rothermel_wildfire import RothermelFireSimulator
from backend.app.services.simulation.network_severance import NetworkSeveranceSimulator

router = APIRouter(prefix="/simulation", tags=["Physics Spatial Simulation"])
hydro_sim = HydroCellularAutomataSimulator()
fire_sim = RothermelFireSimulator()


@router.post("/run", response_model=SimulationResponse, summary="Execute spatial disaster simulation")
def run_simulation(req: SimulationRequest = Body(...)):
    # Run the appropriate physical simulation
    if req.disaster_type.lower() == "wildfire":
        steps_raw, area_sq_km, affected_pop = fire_sim.run_simulation(
            center_lat=req.center_latitude,
            center_lon=req.center_longitude,
            total_hours=req.total_hours,
            time_step_hours=req.time_step_hours,
            wind_speed_kmh=req.wind_speed_kmh or 45.0
        )
    else:
        # Default: Flood
        steps_raw, area_sq_km, affected_pop = hydro_sim.run_simulation(
            center_lat=req.center_latitude,
            center_lon=req.center_longitude,
            total_hours=req.total_hours,
            time_step_hours=req.time_step_hours,
            rain_intensity_mm_h=75.0 * req.rainfall_multiplier,
            dam_breach=True
        )

    # Intersect with road network and communities
    final_cells = steps_raw[-1]["cells"]
    severed_roads_raw, isolated_villages = NetworkSeveranceSimulator.evaluate_severance(
        center_lat=req.center_latitude,
        center_lon=req.center_longitude,
        hazard_cells=final_cells
    )

    severed_roads = [SeveredRoadResponse(**sr) for sr in severed_roads_raw]

    # Convert steps into schema
    timesteps = []
    for s in steps_raw:
        timesteps.append(SimulationStepData(
            step_index=s["step_index"],
            hour=s["hour"],
            inundation_or_spread_cells=s["cells"],
            newly_severed_roads=[r.road_name for r in severed_roads[:s["step_index"] + 1]],
            newly_isolated_villages=[v["name"] for v in isolated_villages[:s["step_index"] + 1]],
            cumulative_affected_pop=int(affected_pop * ((s["step_index"] + 1) / len(steps_raw)))
        ))

    return SimulationResponse(
        simulation_id=101,
        scenario_name=req.scenario_name,
        disaster_type=req.disaster_type,
        total_hours=req.total_hours,
        status="COMPLETED_SUCCESS",
        submerged_area_sq_km=area_sq_km,
        affected_population_estimate=affected_pop,
        severed_roads_count=len(severed_roads),
        isolated_villages=isolated_villages,
        severed_roads=severed_roads,
        timesteps=timesteps,
        created_at=datetime.utcnow()
    )
