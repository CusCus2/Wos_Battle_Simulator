from fastapi import APIRouter

from backend.schemas.battle import SimulateRequest, SimulateResponse
from backend.services.battle_service import run_simulation

router = APIRouter(tags=["simulation"])


@router.post("/simulate", response_model=SimulateResponse)
def simulate(request: SimulateRequest) -> SimulateResponse:
    return run_simulation(request)
