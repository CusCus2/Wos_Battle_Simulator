import math

from backend.battle.damage import *
import random
import copy

from backend.models import player, troop
MAX_ROUNDS = 1000
from dataclasses import dataclass, field


@dataclass
class CombatContext: # current battle context for determining skill activation
    round_number: int
    source_player: object
    target_player: object
    attacker_troop: object | None = None
    defender_troop: object | None = None
    event: str = "round_start"
    attack_number: int | None = None
    attack_type: str | None = None
    can_trigger_skills: bool = True
    counts_as_attack: bool = True

@dataclass
class SkillDefinition: # how skill activates 
    name: str
    trigger_event: str
    trigger_troop: str | None = None
    trigger_every: int | None = None
    chance: float = 1.0
    duration_rounds: int | None = None
    required_condition: str | None = None
    effects: list["SkillEffect"]

@dataclass
class SkillEffect: # what the skill does
    stat: str
    value: float
    modifier: str # increase / decrease
    target_side: str  # host / enemy
    target_troops: tuple[str, ...]
    attack_type: str = "all"
    required_status: str | None = None
    applied_status: str | None = None

@dataclass
class ActiveEffect: # used to store skills that have duration, store in state
    skill_name: str
    source_player: object
    target_player: object
    effect: SkillEffect
    start_round: int
    expires_after_round: int | None = None
    start_attack: int | None = None
    expires_after_attack: int | None = None
    stacks: int = 1

@dataclass
class SkillState:
    proc_count: int = 0
    stacks: int = 0

@dataclass
class TroopModifiers: # skill effects will increase/decrease these vals
    attack: float = 0.0
    defense: float = 0.0
    health: float = 0.0
    lethality: float = 0.0
    damage_dealt: float = 0.0
    damage_taken: float = 0.0
    normal_attack_damage: float = 0.0
    skill_damage: float = 0.0

@dataclass
class TroopStatus:
    statuses: set[str] = field(default_factory=set)

@dataclass
class ArmyModifiers: # clean dataclass to track a players army mods
    infantry: TroopModifiers = field(default_factory=TroopModifiers)
    lancer: TroopModifiers = field(default_factory=TroopModifiers)
    marksman: TroopModifiers = field(default_factory=TroopModifiers)

@dataclass
class BattleState: # overall battle state
    round_number: int = 1
    attack_counters: dict = field(default_factory=dict)
    active_effects: list[ActiveEffect] = field(default_factory=list)
    skill_states: dict = field(default_factory=dict)
    kill_remainders: dict = field(default_factory=dict)
    skill_procs : dict = field(default_factory=dict)


class Battle:
    def __init__ (self, attacker, attacker_joiners,  defender, defender_joiners, type):
        self.player1 = copy.deepcopy(attacker)
        self.player2 = copy.deepcopy(defender)
        self.type = type # rally or solo atttack
        self.joiners = {
            self.player1: attacker_joiners or [],
            self.player2: defender_joiners or []
        }
        self.skill_procs = {
            self.player1 : {},
            self.player2 : {}
        }

    def battle(self):
        # set up logic
        state = BattleState(
            round_number = 0,
            attack_counters= {
                self.player1: {'infantry': 0, 'lancer': 0, 'marksman': 0 },
                self.player2: {'infantry': 0, 'lancer': 0, 'marksman': 0 }
            },
            active_effects = [],
            skill_states= {
                self.player1 : {},
                self.player2 : {}
            },
            kill_remainders= {
                "player1": 0.0,
                "player2": 0.0
            },
            skill_procs = {
                self.player1 : {},
                self.player2 : {}
            }
        )
        print("----------Commence Battle----------")
        print(f"player1 attacks player2, it is a {self.type}")

        # round logic
        # want to keep doing rounds untill one side has no troops left
        while self.player1.troops.total_troop_quantity > 0 and self.player2.troops.total_troop_quantity > 0 and self.round_number <= MAX_ROUNDS:
            #new round so increase round counter
            state.round_number +=1
            # we need to determine what skills are activatedd at round start

            # carry out the round
            self.do_round()

        #result logic
        print("-----------------------------------")
        print(f"Battle ended in {self.round_number} rounds")
        print(f"Player 1 troops remaining: {self.player1.troops.total_troop_quantity}")
        print(f"Player 2 troops remaining: {self.player2.troops.total_troop_quantity}")
        winner = 1 if self.player1.troops.total_troop_quantity > 0 else 2
        attacker_survivors = self.player1.troops.total_troop_quantity
        defender_survivors = self.player2.troops.total_troop_quantity
        print(f"Player {winner} wins!")
        
        print("-------------------------------------")
        print("Skill procs")
        print("Player 1 skill procs: ", state.skill_procs[self.player1])
        print("Player 2 skill procs: ", state.skill_procs[self.player2])
        return winner, attacker_survivors, defender_survivors
    
    def round_start_skills(self, attacker_heroes, defender_heroes):
        # is there any always skill procs
        test = 0