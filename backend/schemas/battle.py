from typing import Literal

from pydantic import BaseModel, Field


class PlayerStatsSchema(BaseModel):
    # Keep the external API flat.
    # player_factory.py converts this into nested PlayerStats.
    inf_attack: float
    inf_defense: float
    inf_health: float
    inf_lethality: float

    lancer_attack: float
    lancer_defense: float
    lancer_health: float
    lancer_lethality: float

    marks_attack: float
    marks_defense: float
    marks_health: float
    marks_lethality: float


class HeroSchema(BaseModel):
    name: str
    stars: int = Field(ge=1, le=5)
    widget_level: int = Field(default=0, ge=0, le=10)


class TroopSlotSchema(BaseModel):
    level: Literal["T6", "T10", "T11", "T12"]
    fc: int = Field(ge=0, le=10)
    quantity: int = Field(ge=0)

    # General model limit. Battle logic can enforce:
    # solo max = 3, rally max = 24.
    exalted_level: int = Field(default=0, ge=0, le=24)


class TroopsSchema(BaseModel):
    infantry: TroopSlotSchema
    lancer: TroopSlotSchema
    marksmen: TroopSlotSchema


class PlayerSchema(BaseModel):
    stats: PlayerStatsSchema
    heroes: list[HeroSchema] | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )
    troops: TroopsSchema


class SimulateRequest(BaseModel):
    num_sims: int = Field(ge=1, le=100_000)
    battle_type: Literal["rally", "solo attack"] = "solo attack"

    attacker: PlayerSchema
    defender: PlayerSchema

    attacker_joiners: list[HeroSchema] = Field(
        default_factory=list,
        max_length=4,
    )
    defender_joiners: list[HeroSchema] = Field(
        default_factory=list,
        max_length=4,
    )


class SimulateResponse(BaseModel):
    num_sims: int
    attacker_wins: int
    defender_wins: int
    attacker_win_rate: float
    defender_win_rate: float
    average_rounds: float
    average_attacker_survivors: float
    average_defender_survivors: float
