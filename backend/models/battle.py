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
    defender_troop_status: str | None = None
    event: str = "round_start"
    attack_number: int | None = None
    attack_type: str | None = None
    can_trigger_skills: bool = True
    counts_as_attack: bool = True
    dodged: bool = False
    skip_attack: bool = False
    extra_attack_effects: list = field(default_factory=list)
    direct_damage_effects: list = field(default_factory=list)

@dataclass
class ActiveEffect:
    skill_name: str
    effect: object
    source_player: object
    target_player: object

    start_round: int

    expires_round: int | None = None
    remaining_attacks: int | None = None
    remaining_attacks_received: int | None = None

    current_value: float | None = None
    stacks: int = 1

@dataclass
class SkillState:
    proc_count: int = 0
    stacks: int = 0
    last_proc_round: int | None = None
    last_proc_attack: int | None = None

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
class ArmyModifiers:
    infantry: TroopModifiers = field(default_factory=TroopModifiers)
    lancer: TroopModifiers = field(default_factory=TroopModifiers)
    marksman: TroopModifiers = field(default_factory=TroopModifiers)

    def get(self, troop_type: str):
        return getattr(self, troop_type)

@dataclass
class TroopStatus:
    statuses: set[str] = field(default_factory=set)
    shield: float = 0.0

@dataclass
class ArmyStatuses:
    infantry: TroopStatus = field(default_factory=TroopStatus)
    lancer: TroopStatus = field(default_factory=TroopStatus)
    marksman: TroopStatus = field(default_factory=TroopStatus)

    def get(self, troop_type: str):
        return getattr(self, troop_type)

@dataclass
class ArmyState:
    modifiers: ArmyModifiers = field(default_factory=ArmyModifiers)
    statuses: ArmyStatuses = field(default_factory=ArmyStatuses)
    player: object

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
        attacker_army = ArmyState(player = self.player1)
        defender_army = ArmyState(player = self.player2)
        print("----------Commence Battle----------")
        print(f"player1 attacks player2, it is a {self.type}")

        # round logic
        # want to keep doing rounds untill one side has no troops left
        while self.player1.troops.total_troop_quantity > 0 and self.player2.troops.total_troop_quantity > 0 and self.round_number <= MAX_ROUNDS:
            #new round so increase round counter
            state.round_number +=1
            attacker_context = CombatContext(
                round_number=state.round_number,
                source_player=self.player1,
                target_player=self.player2,
                event="round_start"
            )
            defender_context = CombatContext(
                round_number=state.round_number,
                source_player=self.player2,
                target_player=self.player1,
                event="round_start"
            )
            # we need to determine what skills are activatedd at round start


            # carry out the round
            self.do_round(attacker_army, defender_army, attacker_context, defender_context)

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

    def do_round(self, attacker: ArmyState, defender: ArmyState, attacker_context: CombatContext, defender_context: CombatContext):
        #determine troops alive
        attacker_troops = self.troop_types_alive(attacker.player.troops)
        defender_troops = self.troop_types_alive(defender.player.troops)

        # player 1 attacks
        for troop in attacker_troops:
            attacker_troop = getattr(attacker.player.troops, troop)
            defender_troop = self.select_target(defender.player)
            self.do_attack(attacker_troop, defender_troop, )

        for troop in defender_troops:
            attacker_troop = getattr(defender.player.troops, troop)
            defender_troop = self.select_target(attacker.player)
            self.do_attack(attacker_troop, defender_troop,)

        # do dmg calcs

        #store results of the round

    def do_attack(self, attacker_troop, defender_troop, context : CombatContext):
        # preform troop attack, using host t_types against curr enemy t_type
        # res of attack shud be a dmg cal, which needs to be returned.
        # the skill procs shud be stored in battle dataclass, i think indexed by round number
        context.event = "before_attack"
        self.process_skill_event(context)

        if context.skip_attack:
            return

        context.event = "before_damage"
        self.process_skill_event(context)

        if not context.dodged:
            self.resolve_attack_damage(context)

        context.event = "after_attack"
        self.process_skill_event(context)

    def select_target(self, player):
        # use to determine which defender troop we target
        if player.troops.infantry.quantity > 0:
            return player.troops.infantry
        if player.troops.lancer.quantity > 0:
            return player.troops.lancer
        if player.troops.marksmen.quantity > 0:
            return player.troops.marksmen
        return None

    def troop_types_alive(self, army):
        troop_types = []
        if army.infantry.quantity > 0:
            troop_types.append("infantry")
        if army.lancer.quantity > 0:
            troop_types.append("lancer")
        if army.marksmen.quantity > 0:
            troop_types.append("marksmen")
        return troop_types















#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # Core skill flow
    
    def process_skill_event(self,event, context : CombatContext):
        if context.event == event:
            return True
        return False

    def get_relevant_skills(self, player, event):
        #returns skills whose trigger event matches current event
        relevant_skills = [] 
        for hero in player.heroes:
            for skill in hero.skills:
                if skill.trigger_event == event:
                    relevant_skills.append(skill)
        return relevant_skills
                    
    
    def skill_can_activate(self, skill, context: CombatContext):
        #master check, calls all the helpers
        if self.check_trigger_troop(skill, context):
            if self.check_attack_type(skill, context):
                if self.check_counter_trigger(skill, context):
                    if self.check_required_status(skill, context):
                        if self.roll_skill_chance(skill):
                            return True
        return False
    
    def check_trigger_troop(self, skill, context : CombatContext):
        #checks if attacking/affected troop matches triiger_troop
        if skill.trigger_troop == context.attacker_troop:
            return True
        return False
    
    def check_attack_type(self, skill, context : CombatContext):
        # check normal, skill, all etc
        if skill.trigger_attack_type == context.attack_type:
            return True
        return False
    
    def check_counter_trigger(self, skill, context : CombatContext):
        # handle every 2 attacks / every 4 rounds etc
        if skill.counter == "round":
            if skill.every == context.round_number:
                return True
        if skill.counter == "attack":
            if skill.every == context.attack_number: # generic attack number, may need specific troop attack
                return True
        return False
    
    def check_required_status(self, skill, context : CombatContext):
        #check any status required for the skill to activate
        if skill.trigger_required_status == context.defender_troop_status:
            return True
        return False
    
    def roll_skill_chance(self, skill):
        # determines if chance skill activates
        chance = random.random()
        if chance <= skill.chance:
            return True
        return False

    ### Effect handling

    def resolve_skill(self, skill, combat: CombatContext, host_army: ArmyState, enemy_army: ArmyState):
        for effect in skill.effects:
            target_army = (host_army if effect.target_side == "host" else enemy_army)
            self.resolve_effect(effect, combat, target_army)


    def resolve_effect(self, effect, combat: CombatContext, target_army: ArmyState):
        if effect.effect_type == "modifier":
            self.apply_modifier_effect(effect, combat, target_army.modifiers)

        elif effect.effect_type == "direct_damage":
            self.apply_direct_damage_effect(effect, combat)

        elif effect.effect_type == "shield":
            self.apply_shield_effect(effect, combat, target_army)

        elif effect.effect_type == "extra_attack":
            self.apply_extra_attack_effect(effect, combat)

        elif effect.effect_type == "dodge":
            self.apply_dodge_effect(effect, combat)

        elif effect.effect_type == "skip_attack":
            self.apply_skip_attack_effect(effect, combat)

        if effect.applied_status is not None:
            self.apply_status_effect( effect, combat, target_army.statuses)


    def get_target_troops(self, effect, combat: CombatContext):
        # small little helper for extracting target troop type
        if "attack_target" in effect.target_troops:
            return [combat.defender_troop.t_type] #t_type returns the name not level

        if "all" in effect.target_troops:
            return ["infantry", "lancer", "marksman"]

        return effect.target_troops
    
    def apply_modifier_effect(effect, army_mods: ArmyModifiers):
        troop_targets = effect.target_troops
        if "all" in troop_targets:
            troop_targets = ["infantry", "lancer", "marksman"]
        for troop_type in troop_targets:
            troop_mods = army_mods.get(troop_type)
            current_value = getattr(troop_mods, effect.stat)
            if effect.modifier == "increase":
                new_val = current_value + effect.value
            elif effect.modifier == "decrease":
                new_val = current_value - effect.value
            else:
                continue

            setattr(troop_mods, effect.stat, new_val)

    def apply_status_effect(self, effect, combat: CombatContext, army_statuses : ArmyStatuses):
        if effect.applied_status is None:
            return

        troop_targets = self.get_target_troops(effect, combat)

        for troop_type in troop_targets:
            troop_status = army_statuses.get(troop_type)
            troop_status.statuses.add(effect.applied_status)

    def apply_direct_damage_effect(effect, combat: CombatContext):
        combat.direct_damage_effects.append(effect)

    def apply_shield_effect(self, effect, combat : CombatContext, army: ArmyState):
        troop_targets = self.get_target_troops(effect, combat)

        for troop_type in troop_targets:
            troop_status = army.statuses.get(troop_type)

            if effect.scaling_stat == "attack":
                troop_mods = army.modifiers.get(troop_type)

                # This will later need the troop's actual/base attack too.
                inf_attack = army.player.stats.inf_attack
                scaling_value = getattr(troop_mods, "attack")

                shield_value = inf_attack * effect.value

                troop_status.shield += shield_value

            if effect.applied_status:
                troop_status.statuses.add(effect.applied_status)

    def apply_extra_attack_effect(effect, combat: CombatContext):
        combat.extra_attack_effects.append(effect)

    def apply_dodge_effect(effect, combat: CombatContext):
        combat.dodged = True

    def apply_skip_attack_effect(effect, combat: CombatContext):
        combat.skip_attack = True