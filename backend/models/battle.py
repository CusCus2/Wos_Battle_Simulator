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
    pending_effects: list = field(default_factory=list)

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
    crit_rate: float = 0.0

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
    player: object
    modifiers: ArmyModifiers = field(default_factory=ArmyModifiers)
    statuses: ArmyStatuses = field(default_factory=ArmyStatuses)

@dataclass
class PendingEffect:
    skill: object
    effect: object
    target_army: ArmyState
    activate_round: int

    attacker_troop: object | None = None
    defender_troop: object | None = None

@dataclass
class BattleState: # overall battle state
    round_number: int = 1
    attack_counters: dict = field(default_factory=dict)
    active_effects: list[ActiveEffect] = field(default_factory=list)
    skill_states: dict = field(default_factory=dict)
    kill_remainders: dict = field(default_factory=dict)
    skill_procs : dict = field(default_factory=dict)
    pending_effects: list[PendingEffect] = field(default_factory=list)


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
            # we need to determine what skills are activatedd at round start


            # carry out the round
            self.do_round(attacker_army, defender_army, state)

        #result logic
        print("-----------------------------------")
        print(f"Battle ended in {state.round_number} rounds")
        print(f"Player 1 troops remaining: {attacker_army.player.troops.total_troop_quantity}")
        print(f"Player 2 troops remaining: {defender_army.player.troops.total_troop_quantity}")
        winner = 1 if attacker_army.player.troops.total_troop_quantity > 0 else 2
        attacker_survivors = attacker_army.player.troops.total_troop_quantity
        defender_survivors = defender_army.player.troops.total_troop_quantity
        print(f"Player {winner} wins!")
        
        print("-------------------------------------")
        print("Skill procs")
        print("Player 1 skill procs: ", state.skill_procs[self.player1])
        print("Player 2 skill procs: ", state.skill_procs[self.player2])
        return winner, attacker_survivors, defender_survivors

    def do_round(self, attacker: ArmyState, defender: ArmyState, state: BattleState):
        #attacker set up
        attacker_troops = self.troop_types_alive(attacker.player.troops)
        attacker_round_context = CombatContext(
            round_number=state.round_number,
            source_player=attacker,
            target_player=defender,
            event="round_start"
        )

        self.resolve_round_start_pending_effects(state, attacker_round_context) # applys any pending effects
        self.process_skill_event(attacker_round_context) # procs any skills that apply at round start

        # defender set up
        defender_troops = self.troop_types_alive(defender.player.troops)
        defender_round_context = CombatContext(
            round_number=state.round_number,
            source_player=defender,
            target_player=attacker,
            event="round_start"
        )
        self.resolve_round_start_pending_effects(state, defender_round_context) # applys any pending effects
        self.process_skill_event(defender_round_context) # procs any skills that apply at round start
        
        #initialise context at round start
        # player 1 attacks
        for troop in attacker_troops:
            attacker_troop = troop
            state.attack_counters[attacker.player][attacker_troop.t_type] += 1
            defender_troop = self.select_target(defender.player)
            attacker_context = CombatContext(
                round_number=state.round_number,
                source_player=attacker,
                target_player=defender,
                attacker_troop=attacker_troop,
                defender_troop=defender_troop,
                attack_number=state.attack_counters[attacker.player][attacker_troop.t_type],
                attack_type="normal"
            )

            # preform attack
            kills = self.do_attack(attacker, defender, attacker_context)

        for troop in defender_troops:
            attacker_troop = troop
            state.attack_counters[defender.player][attacker_troop.t_type] += 1
            defender_troop = self.select_target(attacker.player)
            # update attacker context
            defender_context = CombatContext(
                round_number=state.round_number,
                source_player=defender,
                target_player=attacker,
                attacker_troop=attacker_troop,
                defender_troop=defender_troop,
                attack_number=state.attack_counters[defender.player][attacker_troop.t_type],
                attack_type="normal"
            )
            # handle pending
            # resolve round skills, round number wont change, so itll proc on first attack in round then removed so no dupes
            kills = self.do_attack(defender, attacker, defender_context)

        # do dmg calcs

        #store results of the round

    def do_attack(self, attacker_troop, defender_troop, context : CombatContext, state: BattleState):
        # preform troop attack, using host t_types against curr enemy t_type
        # res of attack shud be a dmg cal, which needs to be returned.
        # the skill procs shud be stored in battle dataclass, i think indexed by round number

        context.event = "before_attack"
        self.process_skill_event(context) # procs the skills that activate at start of attack

        if context.skip_attack:
            return

        context.event = "before_damage"
        self.process_skill_event(context)

        if not context.dodged:
            self.resolve_attack_damage(context)

        #resolve affects proc'd earlier but happen after attack
        self.resolve_pending_attack_effects(context) # of skills procd, some have a second affect thats timing only triggers after atttacking
        # The attack has now consumed any attack-based active effects
        self.update_active_effects("after_attack", context, state)
        # increment the attack counter

        context.event = "after_attack"
        self.process_skill_event(context) # skills that only activate after an attack has occured eg freya, her reap can proc after lancers attack, not before. if before cud proc for any t type

        return kills

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
            troop_types.append(getattr(army, "infantry"))
        if army.lancer.quantity > 0:
            troop_types.append(getattr(army, "lancer"))
        if army.marksmen.quantity > 0:
            troop_types.append(getattr(army, "marksmen"))
        return troop_types





    def resolve_attack_damage(self, context) -> float:
        # this calcs the damage dealt for an attack based on context
        # it should return a float value
        # calculate damage
        troop_base_attack = context.attacker_troop.attack #* (1 + context.attacker_troop.skills) # need to think about FC skills
        attacker_mods = getattr(context.atttacker.modifiers, context.attacker_troop.t_type) # can i do this?
        # print(f" Attacker mods: {attacker_mods}")
        defender_mods = getattr(context.defender.modifiers, str(context.defender_troop))
        # print(f"Defender Mods: {defender_mods}")

        active_mods = self.get_active_modifiers(context,army)

        if mods_p2["host"]["infantry"]["Crystal Shield"] == True and defender_troop_type.t_type == 'infantry': 
            attacker_damage = max(0, damage(troop_base_attack, atk_stats[0], attacker_troop__type.lethality, atk_stats[1], attacker_mods, defender_mods)-36)
        else:
            attacker_damage = damage(troop_base_attack, atk_stats[0], attacker_troop__type.lethality, atk_stats[1], attacker_mods, defender_mods)
        defender_defense = defense(defender_troop_type.defense, def_stats[2], defender_troop_type.health, def_stats[3], defender_mods, attacker_mods)

        fatigue = max(0, 1 - (self.round_number - 1) * 0.0001)

        # clac unit size effectiveness
        unit_size_attacker = self.unit_size(context.attacker_troop.quantity, context.source_player.troops.total_troop_quantity, context.target_player.troops.total_troop_quantity)

        # losses
        defender_dead = (unit_size_attacker * (attacker_damage / defender_defense) * fatigue)/100


    def unit_size(self, troop_quantity, attacker_army_size, defender_army_size):
            return math.sqrt(troop_quantity) * math.sqrt(min(attacker_army_size, defender_army_size))

    def get_active_modifiers(self, context: CombatContext, state:BattleState):
        active_mods = TroopModifiers()

        for active_effect in state.active_effects:

            if not self.active_effect_applies(active_effect, context):
                continue

            effect = active_effect.effect

            current = getattr(active_mods, effect.stat)
            value = active_effect.current_value
            if effect.modifier == "decrease":
                value = -active_effect.current_value

            setattr(
                active_mods,
                effect.stat,
            current + value
            )
        return active_mods







#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # Core skill flow
    
    def process_skill_event(self, host_army: ArmyState, enemy_army: ArmyState, context : CombatContext, state : BattleState):
        skills = self.get_relevant_skills(host_army, context.event)
        for skill in skills:
            if self.skill_can_activate(skill, context):
                self.resolve_skill(skill, context, host_army, enemy_army)
        # need to record the procs, not currently implemented this

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
        if skill.trigger_troop in (None, "all"):
            return True
        return skill.trigger_troop == context.attacker_troop.t_type
    
    def check_attack_type(self, skill, context : CombatContext):
        # check normal, skill, all etc
        if skill.trigger_attack_type == context.attack_type:
            return True
        return False
    
    def check_counter_trigger(self, skill, context : CombatContext):
        # handle every 2 attacks / every 4 rounds etc
        if skill.counter == "round":
            if context.round_number % skill.every == 0:
                return True
        if skill.counter == "attack":
            if context.attack_number % skill.every == 0: # generic attack number, may need specific troop attack
                return True
        if skill.counter is None:
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

    def resolve_skill(self, skill, combat: CombatContext, host_army: ArmyState, enemy_army: ArmyState, state: BattleState):
        for effect in skill.effects:
            target_army = (host_army if effect.target_side == "host" else enemy_army)
            # lets handle the timing
            if effect.timing == "on_trigger":
                self.resolve_effect(skill, effect, combat, target_army, state)

            elif effect.timing == "after_attack":
                combat.pending_effects.append(skill, effect, target_army)

            elif effect.timing == "next_round_start":
                state.pending_effects.append(
                    PendingEffect(skill= skill, effect=effect, target_army =  target_army, 
                        activate_round = state.round_number + 1, attacker_troop=combat.attacker_troop, defender_troop=combat.defender_troop
                    )
                )


    def resolve_effect(self, skill, effect, combat: CombatContext, target_army: ArmyState, state: BattleState):
        if effect.effect_type == "modifier":
            if effect.duration_type == "current_event":
                self.apply_modifier_effect(effect, combat, target_army.modifiers)
            else:
                self.create_active_effect(skill, effect, combat, target_army, state)

        elif effect.effect_type == "direct_damage":
            self.apply_direct_damage_effect(effect, combat)
            if effect.duration_type != "current_event":
                self.create_active_effect(skill, effect, combat, target_army, state)

        elif effect.effect_type == "shield":
            self.apply_shield_effect(effect, combat, target_army)
            if effect.duration_type != "current_event":
                self.create_active_effect(skill, effect, combat, target_army, state)

        elif effect.effect_type == "extra_attack":
            self.apply_extra_attack_effect(effect, combat)
            if effect.duration_type != "current_event":
                self.create_active_effect(skill, effect, combat, target_army, state)

        elif effect.effect_type == "dodge":
            self.apply_dodge_effect(effect, combat)
            if effect.duration_type != "current_event":
                self.create_active_effect(skill, effect, combat, target_army, state)

        elif effect.effect_type == "skip_attack":
            self.apply_skip_attack_effect(effect, combat)
            if effect.duration_type != "current_event":
                self.create_active_effect(skill, effect, combat, target_army, state)

        if effect.applied_status is not None:
            self.apply_status_effect( effect, combat, target_army.statuses)
            if effect.duration_type != "current_event":
                self.create_active_effect(skill, effect, combat, target_army, state)


    def get_target_troops(self, effect, combat: CombatContext):
        # small little helper for extracting target troop type
        if "attack_target" in effect.target_troops:
            return [combat.defender_troop.t_type] #t_type returns the name not level

        if "all" in effect.target_troops:
            return ["infantry", "lancer", "marksman"]

        return effect.target_troops
    
    def apply_modifier_effect(self, effect,combat : CombatContext, army_mods: ArmyModifiers):
        troop_targets = self.get_target_troops(effect, combat)
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

    def apply_direct_damage_effect(self, effect, combat: CombatContext):
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

    def apply_extra_attack_effect(self, effect, combat: CombatContext):
        combat.extra_attack_effects.append(effect)

    def apply_dodge_effect(self, effect, combat: CombatContext):
        combat.dodged = True

    def apply_skip_attack_effect(self, effect, combat: CombatContext):
        combat.skip_attack = True




    # tackling Pending skill procs / duration effects section
    def resolve_pending_attack_effects(self, context: CombatContext):
        # we need to check firstly is there any pending effects
        if context.pending_effects is not None:
            #now we loop throught the pending effects for curr round, then clear
            for skill, effect, target_army in context.pending_effects:
                self.resolve_effect(skill, effect, context, target_army)
            context.pending_effects.clear()

            # note, we handle skill that activate on next round in the state context not combat

    def resolve_round_start_pending_effects(self, state: BattleState, combat: CombatContext):#
        remaining = []
        # check round activation
        for pending in state.pending_effects:
            # check effect procs this round
            if pending.activate_round == state.round_number:
                self.resolve_effect(pending.skill, pending.effect, combat, pending.target_army)
            else:
                remaining.append(pending)

        # update the list to remove proc'd ones
        state.pending_effects = remaining


    def create_active_effect(self, skill, effect, context: CombatContext, army: ArmyState, state: BattleState):
        active = ActiveEffect(
            skill_name= skill.name,
            effect=effect,
            source_player=context.source_player,
            target_player=army,
            start_round=state.round_number,
            current_value=effect.value
        )

        if effect.duration_type == "rounds":
            active.expires_round = (state.round_number + effect.duration_value)

        if effect.duration_type == "attacks":
            active.remaining_attacks = (effect.duration_value)

        elif effect.duration_type == "attacks_received":
            active.remaining_attacks_received = (effect.duration_value)

        state.active_effects.append(active)

    def update_active_effects(self, event: str, context: CombatContext, state: BattleState):
        for active in state.active_effects:

            if (
                event == "after_attack"
                and active.remaining_attacks is not None
                and self.attack_consumes_effect(active, context)
            ):
                active.remaining_attacks -= 1

                if active.effect.decay is not None:
                    active.current_value *= active.effect.decay

            if (
                event == "after_damage"
                and active.remaining_attacks_received is not None
                and self.hit_consumes_effect(active, context)
            ):
                active.remaining_attacks_received -= 1



    def add_active_effect(self, new_effect: ActiveEffect, state: BattleState):
        if new_effect.effect.stackable:

            for active in state.active_effects:

                same_effect = (
                    active.skill_name == new_effect.skill_name
                    and active.source_player is new_effect.source_player
                    and active.target_player is new_effect.target_player
                    and active.effect is new_effect.effect
                )

                if same_effect:
                    active.stacks += 1
                    active.current_value += new_effect.effect.value
                    return

        state.active_effects.append(new_effect)
            
            






    # Troop skills processing