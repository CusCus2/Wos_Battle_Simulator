import io
from contextlib import redirect_stdout

from backend.models.battle_result import Battle
from backend.schemas.battle import SimulateRequest, SimulateResponse
from backend.services.player_factory import build_joiners, build_player


def run_simulation(request: SimulateRequest) -> SimulateResponse:
    attacker = build_player(request.attacker)
    defender = build_player(request.defender)
    attacker_joiners = build_joiners(request.attacker_joiners)
    defender_joiners = build_joiners(request.defender_joiners)

    attacker_wins = 0
    defender_wins = 0
    total_rounds = 0
    total_attacker_survivors = 0
    total_defender_survivors = 0

    for _ in range(request.num_sims):
        with redirect_stdout(io.StringIO()):
            battle = Battle(
                attacker,
                attacker_joiners,
                defender,
                defender_joiners,
                request.battle_type,
            )
            winner, attacker_survivors, defender_survivors = battle.do_battle()
            total_rounds += battle.round_number
            total_attacker_survivors += attacker_survivors
            total_defender_survivors += defender_survivors

        if winner == 1:
            attacker_wins += 1
        else:
            defender_wins += 1

    num_sims = request.num_sims
    return SimulateResponse(
        num_sims=num_sims,
        attacker_wins=attacker_wins,
        defender_wins=defender_wins,
        attacker_win_rate=attacker_wins / num_sims,
        defender_win_rate=defender_wins / num_sims,
        average_rounds=total_rounds / num_sims,
        average_attacker_survivors=total_attacker_survivors / num_sims,
        average_defender_survivors=total_defender_survivors / num_sims,
    )
