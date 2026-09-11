from dataclasses import dataclass, field
import random
import copy
import math
from backend.battle.damage import *

MAX_ROUNDS = 1000
# ---------------------------------------------------------------------------
# Runtime dataclasses
# ---------------------------------------------------------------------------

@dataclass
class TroopModifiers:
    attack: float = 0.0
    defense: float = 0.0
    health: float = 0.0
    lethality: float = 0.0
    damage_dealt: float = 0.0
    damage_taken: float = 0.0
    normal_attack_damage: float = 0.0
    skill_damage: float = 0.0
    crit_rate: float = 0.0

    # Kept separate from percentage damage_taken because troop skills such as
    # Crystal Shield use flat reduction values in the existing troop data.
    flat_damage_reduction: float = 0.0

    # Generic home for "multiply" effects such as Hector Blitz / Philly Dosage Boost.
    # Example: multipliers["damage_dealt"] == 1.8
    multipliers: dict[str, float] = field(default_factory=dict)


@dataclass
class ArmyModifiers:
    infantry: TroopModifiers = field(default_factory=TroopModifiers)
    lancer: TroopModifiers = field(default_factory=TroopModifiers)
    marksman: TroopModifiers = field(default_factory=TroopModifiers)

    def get(self, troop_type: str) -> TroopModifiers:
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

    def get(self, troop_type: str) -> TroopStatus:
        return getattr(self, troop_type)


@dataclass
class ArmyState:
    player: object

    # Reserved for permanent/static modifiers
    modifiers: ArmyModifiers = field(default_factory=ArmyModifiers)

    # Cleared at the beginning of every round. Useful for old troop-skill mechanics.
    round_modifiers: ArmyModifiers = field(default_factory=ArmyModifiers)

    statuses: ArmyStatuses = field(default_factory=ArmyStatuses)


@dataclass
class EffectInstance:
    """A current-event hero effect that belongs to one CombatContext."""
    skill_name: str
    effect: object
    source_army: ArmyState
    target_army: ArmyState
    resolved_target_troops: tuple[str, ...]


@dataclass
class QueuedEffect:
    """An effect whose parent skill already proc'd but whose timing is later this attack."""
    skill: object
    effect: object
    source_army: ArmyState
    target_army: ArmyState
    enemy_army: ArmyState


@dataclass
class PendingEffect:
    """An effect delayed until a future round-start."""
    skill: object
    effect: object
    source_army: ArmyState
    target_army: ArmyState
    enemy_army: ArmyState
    activate_round: int
    attacker_troop: object | None = None
    defender_troop: object | None = None


@dataclass
class ActiveEffect:
    skill_name: str
    effect: object
    source_army: ArmyState
    target_army: ArmyState

    # Important for effects originally targeted at "attack_target".
    # We snapshot the troop type at proc time instead of re-resolving it later.
    resolved_target_troops: tuple[str, ...]

    start_round: int
    expires_round: int | None = None
    remaining_attacks: int | None = None
    remaining_attacks_received: int | None = None

    current_value: float | None = None
    stacks: int = 1


@dataclass
class QueuedDirectDamage:
    """Skill activation is complete; damage.py can resolve this later."""
    skill_name: str
    effect: object
    source_army: ArmyState
    target_army: ArmyState
    resolved_target_troops: tuple[str, ...]
    attacker_troop: object | None = None
    defender_troop: object | None = None


@dataclass
class QueuedExtraAttack:
    """Represents an extra attack without recursively triggering the normal skill pipeline."""
    source_name: str
    source_army: ArmyState
    target_army: ArmyState
    attacker_troop: object
    defender_troop: object | None
    damage_multiplier: float = 1.0
    attack_type: str = "skill"
    can_trigger_skills: bool = False
    counts_as_attack: bool = False


@dataclass
class CombatContext:
    round_number: int
    source_player: ArmyState
    target_player: ArmyState

    attacker_troop: object | None = None
    defender_troop: object | None = None

    event: str = "round_start"
    attack_number: int | None = None
    attack_type: str | None = None

    can_trigger_skills: bool = True
    counts_as_attack: bool = True

    dodged: bool = False
    skip_attack: bool = False

    # Per-attack troop mechanics.
    attacker_troop_modifiers: TroopModifiers = field(default_factory=TroopModifiers)
    defender_troop_modifiers: TroopModifiers = field(default_factory=TroopModifiers)

    # Hero effects that only exist for this combat event.
    current_effects: list[EffectInstance] = field(default_factory=list)

    # Parent skill has already proc'd; resolve after this attack.
    pending_effects: list[QueuedEffect] = field(default_factory=list)


@dataclass
class SkillState:
    proc_count: int = 0
    stacks: int = 0
    last_proc_round: int | None = None
    last_proc_attack: int | None = None


@dataclass
class BattleState:
    round_number: int = 0
    attack_counters: dict = field(default_factory=dict)

    active_effects: list[ActiveEffect] = field(default_factory=list)
    pending_effects: list[PendingEffect] = field(default_factory=list)

    skill_states: dict = field(default_factory=dict)
    skill_procs: dict = field(default_factory=dict)
    kill_remainders: dict = field(default_factory=dict)

    # Damage implementation can drain these later.
    direct_damage_queue: list[QueuedDirectDamage] = field(default_factory=list)
    extra_attack_queue: list[QueuedExtraAttack] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Methods intended to live on Battle
# ---------------------------------------------------------------------------

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

    def battle(self,):

        state = BattleState(
            round_number=0,
            attack_counters={
                self.player1: {
                    "infantry": 0,
                    "lancer": 0,
                    "marksman": 0,
                },
                self.player2: {
                    "infantry": 0,
                    "lancer": 0,
                    "marksman": 0,
                },
            },
            skill_states={
                self.player1: {},
                self.player2: {},
            },
            skill_procs={
                self.player1: {},
                self.player2: {},
            },
            kill_remainders={
                self.player1: 0.0,
                self.player2: 0.0,
            },
        )
        attacker_army = ArmyState(player=self.player1)
        defender_army = ArmyState(player=self.player2)

        self.validate_exalted_levels()
        self.process_battle_start_skills(attacker_army, defender_army, state)

        while (
            attacker_army.player.troops.total_troop_quantity > 0
            and defender_army.player.troops.total_troop_quantity > 0
            and state.round_number < MAX_ROUNDS
        ):
            state.round_number += 1
            self.do_round(attacker_army, defender_army, state)
        
        # handle results being displayed


    def do_round(self, attacker: ArmyState, defender: ArmyState, state: BattleState):

        self.prepare_round(attacker, defender, state)
        round_losses = {
            attacker.player: {
                "infantry": 0.0,
                "lancer": 0.0,
                "marksman": 0.0,
            },
            defender.player: {
                "infantry": 0.0,
                "lancer": 0.0,
                "marksman": 0.0,
            },
        }

        for troop in self.troop_types_alive(attacker.player.troops):
            if troop.quantity <= 0:
                continue

            context = self.build_attack_context(
                attacker,
                defender,
                troop,
                state,
            )
            kills = self.do_attack(context, state)
            # self.do_attack_skill_flow(context, state)
            if (kills and context.defender_troop is not None):
                round_losses [defender.player] [context.defender_troop.t_type] += kills

    # Re-query alive troops after player 1's damage once damage handling exists.
        for troop in self.troop_types_alive(defender.player.troops):
            if troop.quantity <= 0:
                continue

            context = self.build_attack_context(
                defender,
                attacker,
                troop,
                state,
            )
            kills = self.do_attack(context, state)
            # self.do_attack_skill_flow(context, state)
            if (kills and context.defender_troop is not None):
                round_losses [attacker.player] [context.defender_troop.t_type] += kills
            # self.do_attack_skill_flow(context, state)
        
        # round end
        self.apply_round_losses(round_losses, state)
    
    def do_attack(self, context: CombatContext, state: BattleState) -> float:
        total_kills = 0.0
        # --------------------------------------------------
        # TROOP PRE-ATTACK MECHANICS
        # --------------------------------------------------

        # Includes Ambusher first, so actual target is known
        # before hero skills inspect attack_target.
        self.process_before_attack_troop_skills(context, state,)

        # --------------------------------------------------
        # BEFORE ATTACK HERO SKILLS
        # --------------------------------------------------

        context.event = "before_attack"
        self.process_skill_event(context.source_player, context.target_player, context, state,)
        if context.skip_attack:
            return 0.0

        # --------------------------------------------------
        # BEFORE DAMAGE
        # --------------------------------------------------

        context.event = "before_damage"
        self.process_before_damage_troop_skills(context,state,)
        # This time the DEFENDING army owns the
        # before_damage defensive hero skills.
        self.process_skill_event(context.target_player, context.source_player, context, state,)

        # --------------------------------------------------
        # NORMAL ATTACK DAMAGE
        # --------------------------------------------------

        if not context.dodged:
            kills = self.calculate_troop_kills(context.source_player, context.target_player, state, context,)
            total_kills += kills
            # Consume effects such as attacks_received=1
            # only if the hit actually occurred.
            self.update_active_effects("after_damage", context, state,)

        # --------------------------------------------------
        # DELAYED EFFECTS FROM ALREADY-PROCCED SKILLS
        # --------------------------------------------------
        
        self.resolve_pending_attack_effects(context, state,)
        # Existing attack-duration buffs have now been used.
        self.update_active_effects("after_attack", context, state,)

        # --------------------------------------------------
        # AFTER ATTACK HERO SKILLS
        # --------------------------------------------------

        context.event = "after_attack"
        self.process_skill_event(context.source_player, context.target_player, context, state,)

        skill_kills = self.resolve_queued_damage(context, state)
        total_kills += skill_kills

        return total_kills

    def apply_round_losses(self, round_losses, state: BattleState):
        for player, losses  in round_losses.items():
            troop_attr = ("marksmen" if losses == "marksman" else losses)
            player_troop = getattr(player.troops, troop_attr)

            total_kills = ( round_losses[player][losses] + state.kill_remainders[player][losses] )
            remainder , whole_kills  = math.modf(total_kills)

            actual_kills = min(int(whole_kills), player_troop.quantity)

            player_troop.quantity -= actual_kills

            if player_troop.quantity == 0:
                state.kill_remainders[player][losses] = 0.0
            else:
                state.kill_remainders[player][losses] = remainder


        

    # -----------------------------------------------------------------------
    # CALCULATE THE DAMAGE
    # -----------------------------------------------------------------------
    
    def calculate_troop_kills(self, state: BattleState, context: CombatContext,) -> float:
        attacker = context.source_player
        defender = context.target_player
        
        attacker_troop = context.attacker_troop
        defender_troop = context.defender_troop

        attacker_mods = self.get_combined_modifiers(attacker, attacker_troop, context, state, context.attacker_troop_modifiers)
        defender_mods = self.get_combined_modifiers(defender, defender_troop, context, state, context.defender_troop_modifiers)

        dmg = self.troop_damage(attacker_troop, attacker, attacker_mods)
        dfn = self.troop_defense(defender_troop, defender, defender_mods)

        kills = self.calculate_defenders_killed(dmg, dfn, context, state)

        return kills



    def calculate_defenders_killed(self, attacker_damage, defender_defense,  context: CombatContext, state : BattleState) -> float:
        fatigue = max(0, 1 - (state.round_number - 1) * 0.0001)

        # clac unit size effectiveness
        unit_size_attacker = self.unit_size(
            context.attacker_troop.quantity, 
            context.source_player.player.troops.total_troop_quantity, 
            context.target_player.player.troops.total_troop_quantity
        )

        # losses
        defender_dead = (unit_size_attacker * (attacker_damage / defender_defense) * fatigue)/100
        return defender_dead


    
    def unit_size(self, troop_quantity, p1_army_size, p2_army_size):
            return math.sqrt(troop_quantity) * math.sqrt(min(p1_army_size, p2_army_size))



    def resolve_queued_damage(self, context: CombatContext, state: BattleState) -> float:

        total_kills = 0.0

        # direct skill damage
        for damage_event in state.direct_damage_queue:
            ...
            total_kills += self.calculate_skill_kills(damage_event, state)

        # extra attacks
        for extra_attack in state.extra_attack_queue:
            ...
            total_kills += self.calculate_troop_kills(state, extra_context)

        state.direct_damage_queue.clear()
        state.extra_attack_queue.clear()

        return total_kills



    def get_combined_modifiers(self, army: ArmyState, troop, context: CombatContext, state: BattleState, combat_mods: TroopModifiers) -> TroopModifiers:

        return self.combine_modifier_buckets(
            army.modifiers.get(troop.t_type),
            army.round_modifiers.get(troop.t_type),
            self.get_current_modifiers(army, context),
            self.get_active_modifiers(army, context, state),
            combat_mods,
        )


    def troop_damage(self, attacker_troop, attacker, attacker_mods):
        attacker_stats = attacker.player.stats.get(attacker_troop.t_type)

        effective_attack = (attacker_troop.attack* (1 + attacker_stats.attack)* (1 + attacker_mods.attack))
        effective_lethality = (attacker_troop.lethality* (1 + attacker_stats.lethality)* (1 + attacker_mods.lethality))

        raw_damage = (effective_attack* effective_lethality) / 100

        damage = raw_damage * (1 + attacker_mods.normal_attack_damage + attacker_mods.skill_damage)
        damage_multiplier = (attacker_mods.multipliers.get("damage_dealt", 1.0))

        total_damage = damage * (1 + attacker_mods.damage_dealt) * damage_multiplier
        return total_damage



    def troop_defense(self, defender_troop, defender, defender_mods):
        defender_stats = defender.player.stats.get(defender_troop.t_type)
        effective_defense = (defender_troop.defense * (1 + defender_stats.defense) * (1 + defender_mods.defense))
        effective_health = (defender_troop.health * (1 + defender_stats.health) * (1 + defender_mods.health))

        total_defense = (effective_defense * effective_health) / 100
        total_defense /= (1 + defender_mods.damage_taken)
        return total_defense


    # -----------------------------------------------------------------------
    # Battle / round / attack event flow
    # -----------------------------------------------------------------------

    def process_battle_start_skills(self, attacker: ArmyState, defender: ArmyState, state: BattleState,) -> None:
        for host, enemy in ((attacker, defender), (defender, attacker)):
            context = CombatContext(
                round_number=state.round_number,
                source_player=host,
                target_player=enemy,
                event="battle_start",
            )
            self.process_skill_event(host, enemy, context, state)

    def prepare_round( self, attacker: ArmyState, defender: ArmyState, state: BattleState,) -> None:
        # Anything that lasted through the previous round expires first.
        self.update_active_effects("round_start", None, state)

        # Old troop mechanics that are explicitly round-scoped are rebuilt each round.
        attacker.round_modifiers = ArmyModifiers()
        defender.round_modifiers = ArmyModifiers()

        self.process_round_troop_effects(attacker, defender, state)
        self.process_round_troop_effects(defender, attacker, state)

        # Delayed hero effects activate once globally, not once per army attack loop.
        self.resolve_round_start_pending_effects(state)

        for host, enemy in ((attacker, defender), (defender, attacker)):
            context = CombatContext(
                round_number=state.round_number,
                source_player=host,
                target_player=enemy,
                event="round_start",
            )
            self.process_skill_event(host, enemy, context, state)

    def build_attack_context(self,attacker: ArmyState, defender: ArmyState, attacker_troop: object, state: BattleState, *,attack_type: str = "normal",
        can_trigger_skills: bool = True, counts_as_attack: bool = True, count_attack: bool = True, defender_troop: object | None = None, ) -> CombatContext:

        if defender_troop is None:
            defender_troop = self.select_target(defender.player)

        attack_number = None

        if count_attack:
            state.attack_counters[attacker.player][attacker_troop.t_type] += 1
            attack_number = state.attack_counters[attacker.player][attacker_troop.t_type]

        return CombatContext(
            round_number=state.round_number,
            source_player=attacker,
            target_player=defender,
            attacker_troop=attacker_troop,
            defender_troop=defender_troop,
            attack_number=attack_number,
            attack_type=attack_type,
            can_trigger_skills=can_trigger_skills,
            counts_as_attack=counts_as_attack,
        )

    def do_attack_skill_flow(self, context: CombatContext, state: BattleState,):
        """
        Skill/troop-skill lifecycle around one attack.

        Keep your actual normal damage formula inside resolve_attack_damage().
        """
        if context.attacker_troop is None or context.defender_troop is None:
            return None

        # Innate troop targeting (Ambusher) must happen before target-sensitive hero skills.
        self.process_before_attack_troop_skills(context, state)

        context.event = "before_attack"
        self.process_skill_event(context.source_player, context.target_player, context, state,)

        if context.skip_attack:
            return None

        # Defensive troop skills and defensive hero skills belong to the defending army.
        context.event = "before_damage"
        self.process_before_damage_troop_skills(context, state)
        self.process_skill_event(context.target_player, context.source_player, context, state,)

        result = None
        if not context.dodged:
            # YOUR damage implementation plugs in here.
            result = self.resolve_attack_damage(context)

            # "attacks_received" effects tick only when a hit/damage event occurred.
            self.update_active_effects("after_damage", context, state)

        # Effects whose skill proc'd earlier but explicitly says timing="after_attack".
        self.resolve_pending_attack_effects(context, state)

        # Consume attack-duration effects before checking brand-new after_attack skills,
        # otherwise a newly-created effect could immediately lose one charge.
        self.update_active_effects("after_attack", context, state)

        context.event = "after_attack"
        self.process_skill_event(context.source_player, context.target_player, context, state,)

        return result

    # -----------------------------------------------------------------------
    # Hero skill activation
    # -----------------------------------------------------------------------

    def process_skill_event(self, host_army: ArmyState, enemy_army: ArmyState, context: CombatContext, state: BattleState, ) -> None:
        if not context.can_trigger_skills:
            return

        for skill in self.get_relevant_skills(host_army, context.event):
            if self.skill_can_activate(skill, host_army, enemy_army, context):
                self.resolve_skill(skill, context, host_army, enemy_army, state)
                self.record_skill_proc(host_army, skill, context, state)

    def get_relevant_skills(self, army: ArmyState, event: str) -> list:
        relevant = []

        for hero in army.player.heroes:
            for skill in hero.skills:
                if skill.trigger_event == event:
                    relevant.append(skill)

        # Joiners contribute only skill 1 in rally/garrison battles.
        if self.type in ("rally", "garrison"):
            for hero in self.joiners.get(army.player, []):
                if not hero.skills:
                    continue
                skill = hero.skills[0]
                if skill.trigger_event == event:
                    relevant.append(skill)

        return relevant

    def skill_can_activate( self, skill, host_army: ArmyState, enemy_army: ArmyState, context: CombatContext, ) -> bool:
        if not self.check_trigger_troop(skill, context):
            return False

        if not self.check_attack_type(skill, context):
            return False

        if not self.check_counter_trigger(skill, context):
            return False

        if not self.check_required_status(skill, enemy_army, context):
            return False

        # RNG LAST so invalid skills do not consume random rolls.
        return self.roll_skill_chance(skill)

    def check_trigger_troop(self, skill, context: CombatContext) -> bool:
        if skill.trigger_troop in (None, "all"):
            return True

        # Defensive before-damage skills conceptually refer to the troop receiving damage.
        troop = (
            context.defender_troop
            if context.event == "before_damage"
            else context.attacker_troop
        )

        return troop is not None and skill.trigger_troop == troop.t_type

    def check_attack_type(self, skill, context: CombatContext) -> bool:
        if skill.trigger_attack_type in (None, "all"):
            return True

        return context.attack_type == skill.trigger_attack_type

    def check_counter_trigger(self, skill, context: CombatContext) -> bool:
        if skill.counter is None:
            return True

        if skill.every is None or skill.every <= 0:
            return False

        if skill.counter == "round":
            return context.round_number % skill.every == 0

        if skill.counter == "attack":
            if context.attack_number is None:
                return False
            return context.attack_number % skill.every == 0

        return False

    def check_required_status( self, skill, enemy_army: ArmyState, context: CombatContext, ) -> bool:
        if skill.trigger_required_status is None:
            return True

        troop = context.defender_troop
        if troop is None:
            return False

        return self.has_status(
            enemy_army,
            troop.t_type,
            skill.trigger_required_status,
            context,
        )

    def roll_skill_chance(self, skill) -> bool:
        return random.random() <= skill.chance

    def record_skill_proc(self, army: ArmyState, skill, context: CombatContext, state: BattleState, ) -> None:
        proc_dict = state.skill_procs.setdefault(army.player, {})
        proc_dict[skill.name] = proc_dict.get(skill.name, 0) + 1

        player_states = state.skill_states.setdefault(army.player, {})
        skill_state = player_states.setdefault(skill.name, SkillState())

        skill_state.proc_count += 1
        skill_state.last_proc_round = context.round_number
        skill_state.last_proc_attack = context.attack_number

    # -----------------------------------------------------------------------
    # Hero effect timing / resolution
    # -----------------------------------------------------------------------

    def resolve_skill(self, skill, combat: CombatContext, host_army: ArmyState, enemy_army: ArmyState,state: BattleState, ) -> None:
        for effect in skill.effects:
            target_army = (
                host_army
                if effect.target_side == "host"
                else enemy_army
            )

            if effect.timing == "on_trigger":
                self.resolve_effect(
                    skill,
                    effect,
                    combat,
                    host_army,
                    target_army,
                    state,
                )

            elif effect.timing == "after_attack":
                combat.pending_effects.append(
                    QueuedEffect(
                        skill=skill,
                        effect=effect,
                        source_army=host_army,
                        target_army=target_army,
                        enemy_army=enemy_army,
                    )
                )

            elif effect.timing == "next_round_start":
                state.pending_effects.append(
                    PendingEffect(
                        skill=skill,
                        effect=effect,
                        source_army=host_army,
                        target_army=target_army,
                        enemy_army=enemy_army,
                        activate_round=state.round_number + 1,
                        attacker_troop=combat.attacker_troop,
                        defender_troop=combat.defender_troop,
                    )
                )

            else:
                raise ValueError(
                    f"Unknown timing '{effect.timing}' "
                    f"for {skill.name}"
                )

    def resolve_effect(self, skill, effect, combat: CombatContext, source_army: ArmyState, target_army: ArmyState, state: BattleState, ) -> None:
        resolved_targets = tuple(
            self.get_target_troops(effect, combat)
        )

        if effect.effect_type == "modifier":
            if effect.duration_type == "current_event":
                combat.current_effects.append(
                    EffectInstance(
                        skill_name=skill.name,
                        effect=effect,
                        source_army=source_army,
                        target_army=target_army,
                        resolved_target_troops=resolved_targets,
                    )
                )
            else:
                self.create_active_effect(skill,effect,combat,source_army,target_army,state,resolved_targets=resolved_targets,)

        elif effect.effect_type == "status":
            if effect.duration_type == "current_event":
                combat.current_effects.append(
                    EffectInstance(
                        skill_name=skill.name,
                        effect=effect,
                        source_army=source_army,
                        target_army=target_army,
                        resolved_target_troops=resolved_targets,
                    )
                )
            else:
                self.create_active_effect(skill, effect, combat, source_army, target_army, state, resolved_targets=resolved_targets,)

        elif effect.effect_type == "direct_damage":
            state.direct_damage_queue.append(
                QueuedDirectDamage(
                    skill_name=skill.name,
                    effect=effect,
                    source_army=source_army,
                    target_army=target_army,
                    resolved_target_troops=resolved_targets,
                    attacker_troop=combat.attacker_troop,
                    defender_troop=combat.defender_troop,
                )
            )

        elif effect.effect_type == "shield":
            self.apply_shield_effect(effect, combat, target_army,)

            if effect.duration_type != "current_event":
                self.create_active_effect(skill, effect, combat, source_army, target_army,state, resolved_targets=resolved_targets,)

        elif effect.effect_type == "extra_attack":
            self.queue_extra_attack_effect( skill, effect, combat, source_army,target_army, state,)

        elif effect.effect_type == "dodge":
            self.apply_dodge_effect(effect, combat)

        elif effect.effect_type == "skip_attack":
            # Support exists, but this remains disabled by default because the
            # Ahmose wording/mechanic is still uncertain.
            self.apply_skip_attack_effect(effect, combat)

        else:
            raise ValueError(
                f"Unknown effect type '{effect.effect_type}' "
                f"for {skill.name}"
            )

    def get_target_troops(self, effect, combat: CombatContext,) -> list[str]:
        targets = effect.target_troops or ["all"]

        if "attack_target" in targets:
            if combat.defender_troop is None:
                return []
            return [combat.defender_troop.t_type]

        if "all" in targets:
            return ["infantry", "lancer", "marksman"]

        return list(targets)

    # -----------------------------------------------------------------------
    # Pending effects
    # -----------------------------------------------------------------------

    def resolve_pending_attack_effects(self, context: CombatContext, state: BattleState,) -> None:
        pending = list(context.pending_effects)
        context.pending_effects.clear()

        for queued in pending:
            self.resolve_effect(queued.skill, queued.effect, context, queued.source_army, queued.target_army, state,)

    def resolve_round_start_pending_effects(self,state: BattleState,) -> None:
        due = []
        remaining = []

        for pending in state.pending_effects:
            if pending.activate_round <= state.round_number:
                due.append(pending)
            else:
                remaining.append(pending)

        state.pending_effects = remaining

        for pending in due:
            context = CombatContext(
                round_number=state.round_number,
                source_player=pending.source_army,
                target_player=pending.enemy_army,
                attacker_troop=pending.attacker_troop,
                defender_troop=pending.defender_troop,
                event="round_start",
                attack_type="normal" if pending.attacker_troop else None,
            )

            # Renee Nightmare Trace is currently encoded as:
            # timing=next_round_start + duration=current_event.
            # At round-start there is no attack to apply a current-event damage modifier to,
            # so turn that into a one-use active modifier for the next matching attack.
            if (
                pending.effect.effect_type == "modifier"
                and pending.effect.duration_type == "current_event"
            ):
                self.create_active_effect(pending.skill, pending.effect, context, pending.source_army,
                    pending.target_army, state, resolved_targets=tuple(self.get_target_troops(pending.effect, context)),
                    remaining_attacks_override=1,
                )
            else:
                self.resolve_effect(pending.skill, pending.effect, context, pending.source_army, pending.target_army, state, )

    # -----------------------------------------------------------------------
    # Active effects
    # -----------------------------------------------------------------------

    def create_active_effect(self, skill, effect, context: CombatContext, source_army: ArmyState, target_army: ArmyState, state: BattleState, *,
        resolved_targets: tuple[str, ...] | None = None, remaining_attacks_override: int | None = None, ) -> ActiveEffect:

        if resolved_targets is None:
            resolved_targets = tuple(
                self.get_target_troops(effect, context)
            )

        active = ActiveEffect(
            skill_name=skill.name,
            effect=effect,
            source_army=source_army,
            target_army=target_army,
            resolved_target_troops=resolved_targets,
            start_round=state.round_number,
            current_value=effect.value,
        )

        if remaining_attacks_override is not None:
            active.remaining_attacks = remaining_attacks_override

        elif effect.duration_type == "rounds":
            # Round-start buff of 1 round -> active for current round.
            # Mid-round buff of 1 round -> survives through the NEXT full round.
            extra_round = 0 if context.event == "round_start" else 1

            active.expires_round = (state.round_number + effect.duration_value + extra_round)

        elif effect.duration_type == "attacks":
            active.remaining_attacks = effect.duration_value

        elif effect.duration_type == "attacks_received":
            active.remaining_attacks_received = effect.duration_value

        elif effect.duration_type == "battle":
            pass

        elif effect.duration_type != "current_event":
            raise ValueError(
                f"Unknown duration type '{effect.duration_type}' "
                f"for {skill.name}"
            )

        self.add_active_effect(active, state)

        if effect.applied_status:
            self.apply_persistent_status(active)

        return active

    def add_active_effect(self, new_effect: ActiveEffect, state: BattleState,) -> None:
        for active in state.active_effects:
            same_effect = (
                active.skill_name == new_effect.skill_name
                and active.source_army is new_effect.source_army
                and active.target_army is new_effect.target_army
                and active.effect is new_effect.effect
                and active.resolved_target_troops
                == new_effect.resolved_target_troops
            )

            if not same_effect:
                continue

            if new_effect.effect.stackable:
                active.stacks += 1

                if active.current_value is None:
                    active.current_value = new_effect.current_value
                elif new_effect.current_value is not None:
                    active.current_value += new_effect.current_value

                return

            # Non-stackable re-proc refreshes duration rather than duplicating.
            active.current_value = new_effect.current_value
            active.expires_round = new_effect.expires_round
            active.remaining_attacks = new_effect.remaining_attacks
            active.remaining_attacks_received = ( new_effect.remaining_attacks_received )
            return

        state.active_effects.append(new_effect)

    def update_active_effects(self, event: str, context: CombatContext | None, state: BattleState, ) -> None:
        expired: list[ActiveEffect] = []

        for active in list(state.active_effects):

            if (
                event == "round_start"
                and active.expires_round is not None
                and state.round_number >= active.expires_round
            ):
                expired.append(active)
                continue

            if (
                event == "after_attack"
                and context is not None
                and active.remaining_attacks is not None
                and self.attack_consumes_effect(active, context)
            ):
                active.remaining_attacks -= 1

                if active.effect.decay is not None:
                    active.current_value *= active.effect.decay

                if active.effect.consume_status:
                    self.consume_effect_required_status(active, context)

                if active.remaining_attacks <= 0:
                    expired.append(active)

            if (
                event == "after_damage"
                and context is not None
                and active.remaining_attacks_received is not None
                and self.hit_consumes_effect(active, context)
            ):
                active.remaining_attacks_received -= 1

                if active.effect.consume_status:
                    self.consume_effect_required_status(active, context)

                if active.remaining_attacks_received <= 0:
                    expired.append(active)

        for active in expired:
            self.remove_active_effect(active, state)

    def attack_consumes_effect( self, active: ActiveEffect, context: CombatContext, ) -> bool:
        if active.target_army is not context.source_player:
            return False

        return self.active_effect_applies(active, context.source_player, context,)

    def hit_consumes_effect(self, active: ActiveEffect, context: CombatContext,) -> bool:
        if active.target_army is not context.target_player:
            return False

        return self.active_effect_applies(
            active,
            context.target_player,
            context,
        )

    def remove_active_effect(self, active: ActiveEffect, state: BattleState,) -> None:
        if active not in state.active_effects:
            return

        state.active_effects.remove(active)

        if active.effect.applied_status:
            status = active.effect.applied_status

            for troop_type in active.resolved_target_troops:
                still_supplied = any(
                    other.target_army is active.target_army
                    and other.effect.applied_status == status
                    and troop_type in other.resolved_target_troops
                    for other in state.active_effects
                )

                if not still_supplied:
                    active.target_army.statuses.get(troop_type).statuses.discard(status)

        # Only one current hero shield mechanic exists in heroes.json (Gatot).
        # This avoids leaving stale shield state after its duration ends.
        if active.effect.effect_type == "shield":
            for troop_type in active.resolved_target_troops:
                still_shielded = any(
                    other.target_army is active.target_army
                    and other.effect.effect_type == "shield"
                    and troop_type in other.resolved_target_troops
                    for other in state.active_effects
                )

                if not still_shielded:
                    active.target_army.statuses.get(troop_type).shield = 0.0

    # -----------------------------------------------------------------------
    # Modifier querying
    # -----------------------------------------------------------------------

    def get_current_modifiers(self, army: ArmyState, context: CombatContext,) -> TroopModifiers:
        mods = TroopModifiers()

        for instance in context.current_effects:
            if instance.effect.effect_type != "modifier":
                continue

            if not self.effect_instance_applies(instance, army, context, ):
                continue

            self.apply_modifier_value( mods, instance.effect, instance.effect.value, )

        return mods

    def get_active_modifiers(self, army: ArmyState, context: CombatContext, state: BattleState, ) -> TroopModifiers:
        mods = TroopModifiers()

        for active in state.active_effects:
            if active.effect.effect_type != "modifier":
                continue

            if not self.active_effect_applies( active, army, context,):
                continue

            self.apply_modifier_value( mods, active.effect, active.current_value,)

        return mods

    def active_effect_applies( self, active: ActiveEffect, army: ArmyState, context: CombatContext,) -> bool:
        return self.effect_applies(
            effect=active.effect,
            source_army=active.source_army,
            target_army=active.target_army,
            resolved_target_troops=active.resolved_target_troops,
            army=army,
            context=context,
        )

    def effect_instance_applies( self, instance: EffectInstance, army: ArmyState, context: CombatContext,) -> bool:
        return self.effect_applies(
            effect=instance.effect,
            source_army=instance.source_army,
            target_army=instance.target_army,
            resolved_target_troops=instance.resolved_target_troops,
            army=army,
            context=context,
        )

    def effect_applies( self, *, effect, source_army: ArmyState, target_army: ArmyState, resolved_target_troops: tuple[str, ...], army: ArmyState, context: CombatContext, ) -> bool:
        if target_army is not army:
            return False

        target_troop = self.get_context_troop_for_army( army, context, )

        if target_troop is None:
            return False

        if ( resolved_target_troops and target_troop.t_type not in resolved_target_troops ):
            return False

        if ( effect.attack_type not in (None, "all") and context.attack_type != effect.attack_type):
            return False

        enemy_targets = effect.enemy_troops or ["all"]

        if "all" not in enemy_targets:
            opposing_troop = self.get_opposing_troop( army, context,)

            if opposing_troop is None:
                return False

            if ( "attack_target" not in enemy_targets and opposing_troop.t_type not in enemy_targets):
                return False

        if effect.required_status:
            if not self.effect_required_status_present( effect, source_army, target_army, context,):
                return False

        return True

    def apply_modifier_value( self, mods: TroopModifiers, effect, value: float | None ) -> None:
        if effect.stat is None or value is None:
            return

        if effect.modifier == "multiply":
            current = mods.multipliers.get(effect.stat, 1.0)
            mods.multipliers[effect.stat] = current * value
            return

        if not hasattr(mods, effect.stat):
            raise ValueError(
                f"Unknown modifier stat '{effect.stat}'"
            )

        current = getattr(mods, effect.stat)

        if effect.modifier == "increase":
            value_to_add = value
        elif effect.modifier == "decrease":
            value_to_add = -value
        else:
            return

        setattr( mods, effect.stat, current + value_to_add,)

    def combine_modifier_buckets( self, *buckets: TroopModifiers, ) -> TroopModifiers:
        combined = TroopModifiers()

        additive_fields = (
            "attack",
            "defense",
            "health",
            "lethality",
            "damage_dealt",
            "damage_taken",
            "normal_attack_damage",
            "skill_damage",
            "crit_rate",
            "flat_damage_reduction",
        )

        for bucket in buckets:
            for stat in additive_fields:
                setattr( combined,  stat,  getattr(combined, stat)  + getattr(bucket, stat) )

            for stat, multiplier in bucket.multipliers.items():
                current = combined.multipliers.get(stat, 1.0)
                combined.multipliers[stat] = current * multiplier

        return combined

    # -----------------------------------------------------------------------
    # Status handling
    # -----------------------------------------------------------------------

    def apply_persistent_status( self, active: ActiveEffect,) -> None:
        status = active.effect.applied_status
        if not status:
            return

        for troop_type in active.resolved_target_troops:
            active.target_army.statuses.get( troop_type).statuses.add(status)

    def has_status( self, army: ArmyState, troop_type: str, status: str, context: CombatContext | None = None,) -> bool:
        if status in army.statuses.get(troop_type).statuses:
            return True

        if context is None:
            return False

        # Current-event statuses never enter persistent ArmyStatuses.
        for instance in context.current_effects:
            if (
                instance.target_army is army
                and instance.effect.applied_status == status
                and troop_type in instance.resolved_target_troops
            ):
                return True

        return False

    def effect_required_status_present( self, effect, source_army: ArmyState, target_army: ArmyState, context: CombatContext,) -> bool:
        required = effect.required_status
        if required is None:
            return True

        # Current heroes.json uses:
        # - host buff conditioned on enemy target status (Renee)
        # - enemy effect conditioned on that enemy troop's status (Fred)
        if effect.target_side == "host":
            status_army = ( context.target_player if source_army is context.source_player else context.source_player)
        else:
            status_army = target_army

        status_troop = self.get_context_troop_for_army( status_army, context,)

        if status_troop is None:
            return False

        return self.has_status( status_army, status_troop.t_type, required, context,)

    def consume_effect_required_status( self, active: ActiveEffect, context: CombatContext ) -> None:
        status = active.effect.consume_status
        if not status:
            return

        if active.effect.target_side == "host":
            status_army = (
                context.target_player
                if active.source_army is context.source_player
                else context.source_player
            )
        else:
            status_army = active.target_army

        troop = self.get_context_troop_for_army(status_army, context )

        if troop is not None:
            status_army.statuses.get(troop.t_type).statuses.discard(status)

    # -----------------------------------------------------------------------
    # Special hero effects
    # -----------------------------------------------------------------------

    def apply_shield_effect( self, effect, combat: CombatContext, army: ArmyState,) -> None:
        for troop_type in self.get_target_troops(effect, combat):
            troop_status = army.statuses.get(troop_type)

            if effect.scaling_stat == "attack":
                # Current heroes.json shield is Gatot Infantry -> player inf_attack.
                # Keep player stats separate from ArmyModifiers as discussed.
                stat_name = self.player_stat_name( troop_type, "attack" )
                scaling_value = getattr(army.player.stats, stat_name )
                troop_status.shield += scaling_value * effect.value

            if effect.applied_status:
                troop_status.statuses.add(effect.applied_status)

    def apply_dodge_effect(self, effect, combat: CombatContext ) -> None:
        combat.dodged = True

    def apply_skip_attack_effect( self, effect, combat: CombatContext ) -> None:
        # You previously flagged Ahmose's wording as uncertain.
        # Set self.enable_skip_attack_effects = True only once verified.
        if getattr(self, "enable_skip_attack_effects", False):
            combat.skip_attack = True

    def queue_extra_attack_effect( self, skill, effect, combat: CombatContext, source_army: ArmyState, target_army: ArmyState, state: BattleState,) -> None:
        # For current hero schema, target_troops on an extra_attack identifies
        # which HOST troop(s) launch the bonus strike.
        troop_types = self.get_target_troops(effect, combat)

        for troop_type in troop_types:
            attacker_troop = self.get_formation_troop(
                source_army.player.troops,
                troop_type,
            )

            if attacker_troop is None or attacker_troop.quantity <= 0:
                continue

            defender_troop = combat.defender_troop

            state.extra_attack_queue.append(
                QueuedExtraAttack(
                    source_name=skill.name,
                    source_army=source_army,
                    target_army=(
                        combat.target_player
                        if source_army is combat.source_player
                        else combat.source_player
                    ),
                    attacker_troop=attacker_troop,
                    defender_troop=defender_troop,
                    damage_multiplier=effect.value or 1.0,
                    attack_type=( effect.attack_type if effect.attack_type not in (None, "all") else "skill"),
                    can_trigger_skills=False,
                    counts_as_attack=False,
                )
            )

    # -----------------------------------------------------------------------
    # Context / targeting helpers
    # -----------------------------------------------------------------------

    def get_context_troop_for_army( self, army: ArmyState, context: CombatContext,):
        if army is context.source_player:
            return context.attacker_troop

        if army is context.target_player:
            return context.defender_troop

        return None

    def get_opposing_troop( self, army: ArmyState, context: CombatContext,):
        if army is context.source_player:
            return context.defender_troop

        if army is context.target_player:
            return context.attacker_troop

        return None

    def get_formation_troop(self, formation, troop_type: str ):
        attr = ( "marksmen" if troop_type == "marksman" else troop_type)
        return getattr(formation, attr, None)

    def player_stat_name(self, troop_type: str, stat: str,) -> str:
        prefix = {
            "infantry": "inf",
            "lancer": "lancer",
            "marksman": "marks",
        }[troop_type]

        return f"{prefix}_{stat}"

    # -----------------------------------------------------------------------
    # Troop skills
    # -----------------------------------------------------------------------

    def validate_exalted_levels(self):
        max_level = 3 if self.type == "solo" else 24

        for player in (self.player1, self.player2):

            for troop in (
                player.troops.infantry,
                player.troops.lancer,
                player.troops.marksmen,
            ):
                if troop.exalted_level > max_level:
                    raise ValueError(
                        f"{self.type} battles allow a maximum "
                        f"Exalted level of {max_level}"
                    )

    def process_round_troop_effects(self, host: ArmyState, enemy: ArmyState, state: BattleState ) -> None:
        """
        Handles T12 'exalted' effects from the existing troops.json.

        They are evaluated into round_modifiers rather than forced through the
        hero SkillEffect schema.
        """
        formation = host.player.troops

        # Infantry T12 Exalted:
        # enemy damage dealt reduced for first N rounds.
        infantry = formation.infantry
        infantry_exalted = (infantry.skills or {}).get("exalted")

        if infantry_exalted:
            max_round = infantry_exalted.get("max_round", 5)

            if state.round_number <= max_round:
                self.apply_round_modifier(enemy, ["infantry", "lancer", "marksman"], "damage_dealt", infantry_exalted["value"]*infantry.exalted_level, "decrease" )

        # Lancer T12 Exalted:
        lancer = formation.lancer
        lancer_exalted = (lancer.skills or {}).get("exalted")

        if lancer_exalted:
            # Existing old pipeline treated it as first-five-round behaviour.
            max_round = lancer_exalted.get("max_round", 5)

            if state.round_number <= max_round:
                for buff in ("buff1", "buff2"):
                    data = lancer_exalted.get(buff)
                    if not data:
                        continue

                    troop_type = data.get("troop_type")
                    stat = data.get("buff")
                    value = data.get("value", 0.0)
                    value = value * lancer.exalted_level

                    if troop_type and stat:
                        # damage_taken in this legacy data is beneficial when lowered;
                        # damage_dealt is beneficial when raised.
                        direction = (
                            "decrease"
                            if stat == "damage_taken"
                            else "increase"
                        )

                        self.apply_round_modifier( host, [troop_type], stat, value, direction,)

        # Marksman T12 Exalted:
        marksman = formation.marksmen
        marksman_exalted = (marksman.skills or {}).get("exalted")

        if marksman_exalted:
            trigger = marksman_exalted.get("round_trigger", 5)
            stacks = state.round_number // trigger

            if stacks > 0:
                self.apply_round_modifier( host, ["marksman"], "damage_dealt", (marksman_exalted["value"] * marksman.exalted_level) * stacks, "increase" )

    def process_before_attack_troop_skills(self, context: CombatContext, state: BattleState ) -> None:
        if ( context.attack_type != "normal" or context.attacker_troop is None ):
            return

        # Ambusher first because hero skills using attack_target must see
        # the redirected target, not the original infantry-front target.
        self.process_ambusher(context, state)

        self.apply_troop_matchup_modifiers(context)

        troop = context.attacker_troop
        skills = troop.skills or {}

        if troop.t_type == "lancer":
            crystal_lance = skills.get("Crystal Lance")

            if (crystal_lance and random.random() < crystal_lance["chance"] ):
                context.attacker_troop_modifiers.skill_damage += (crystal_lance["value"])
                self.record_troop_proc(context.source_player, "Crystal Lance", state)

                incandescent = skills.get("Incadescent Field")

                if ( incandescent and random.random() < incandescent["chance"]):
                    # Existing data says reduce_damage with a flat value.
                    # Keep it separate from percentage damage_taken.
                    context.source_player.round_modifiers.lancer.flat_damage_reduction += (incandescent["value"])
                    self.record_troop_proc(context.source_player, "Incadescent Field", state)

        elif troop.t_type == "marksman":
            gunpowder = skills.get("Crystal Gunpowder")

            if (gunpowder and random.random() < gunpowder["chance"]):
                context.attacker_troop_modifiers.damage_dealt += (gunpowder["value"])
                self.record_troop_proc(context.source_player, "Crystal Gunpowder", state )

                flame_charge = skills.get("Flame Charge")

                if flame_charge:
                    buff1 = flame_charge.get("buff1")
                    buff2 = flame_charge.get("buff2")

                    if buff1:
                        context.attacker_troop_modifiers.attack += ( buff1["value"])

                    if buff2:
                        context.attacker_troop_modifiers.damage_dealt += ( buff2["value"])

            # Innate Marksman Volley from the old battle implementation.
            if random.random() < 0.10:
                state.extra_attack_queue.append(
                    QueuedExtraAttack(
                        source_name="Volley",
                        source_army=context.source_player,
                        target_army=context.target_player,
                        attacker_troop=context.attacker_troop,
                        defender_troop=context.defender_troop,
                        damage_multiplier=1.0,
                        attack_type="troop_skill",
                        can_trigger_skills=False,
                        counts_as_attack=False,
                    )
                )
                self.record_troop_proc( context.source_player, "Volley", state )

    def process_before_damage_troop_skills(self, context: CombatContext, state: BattleState,) -> None:
        """
        Defensive troop skills. Currently the existing troop data only needs
        Infantry Crystal Shield (+ Body of Light when present).
        """
        defender = context.defender_troop

        if defender is None or defender.t_type != "infantry":
            return

        skills = defender.skills or {}
        crystal_shield = skills.get("Crystal Shield")

        if (crystal_shield and random.random() < crystal_shield["chance"] ):
            context.defender_troop_modifiers.flat_damage_reduction += ( crystal_shield["value"] )

            self.record_troop_proc(context.target_player, "Crystal Shield", state,)

            body_of_light = skills.get("Body of light")

            if body_of_light:
                buff1 = body_of_light.get("buff1")
                buff2 = body_of_light.get("buff2")

                if buff1:
                    context.defender_troop_modifiers.defense += ( buff1["value"])

                if buff2:
                    # Data says reduce_damage by a percentage.
                    context.defender_troop_modifiers.damage_taken -= (buff2["value"])

    def process_ambusher(self, context: CombatContext, state: BattleState,) -> None:
        if context.attacker_troop.t_type != "lancer":
            return

        marksman = context.target_player.player.troops.marksmen

        if marksman.quantity <= 0:
            return

        if random.random() < 0.20:
            context.defender_troop = marksman
            self.record_troop_proc(
                context.source_player,
                "Ambusher",
                state,
            )

    def apply_troop_matchup_modifiers( self, context: CombatContext,) -> None:
        attacker = context.attacker_troop
        defender = context.defender_troop

        if attacker is None or defender is None:
            return

        matchup = (attacker.t_type, defender.t_type)

        if matchup == ("infantry", "lancer"):
            context.attacker_troop_modifiers.normal_attack_damage += 0.10

            # Preserves the old pipeline's Infantry-vs-Lancer defense bonus
            # for the remainder of the round.
            context.source_player.round_modifiers.infantry.defense += 0.10

        elif matchup == ("lancer", "marksman"):
            context.attacker_troop_modifiers.normal_attack_damage += 0.10

        elif matchup == ("marksman", "infantry"):
            context.attacker_troop_modifiers.normal_attack_damage += 0.10

    def apply_round_modifier(self, army: ArmyState, troop_types: list[str], stat: str, value: float, direction: str,) -> None:
        for troop_type in troop_types:
            mods = army.round_modifiers.get(troop_type)

            if not hasattr(mods, stat):
                raise ValueError(
                    f"Unknown troop modifier stat '{stat}'"
                )

            current = getattr(mods, stat)

            if direction == "increase":
                current += value
            elif direction == "decrease":
                current -= value
            else:
                raise ValueError(
                    f"Unknown modifier direction '{direction}'"
                )

            setattr(mods, stat, current)

    def record_troop_proc( self, army: ArmyState, skill_name: str, state: BattleState,) -> None:
        proc_dict = state.skill_procs.setdefault(army.player, {})
        proc_dict[skill_name] = proc_dict.get(skill_name, 0) + 1


# ---------------------------------------------------------------------------
# Integration notes for your existing Battle methods
# ---------------------------------------------------------------------------
