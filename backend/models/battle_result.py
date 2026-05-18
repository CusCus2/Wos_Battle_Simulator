import math

from backend.battle.damage import *
import random

from backend.models import player, troop
MAX_ROUNDS = 1000

class Battle:
    def __init__ (self, attacker, attacker_joiners,  defender, defender_joiners, type):
        self.player1 = attacker
        self.player2 = defender
        self.type = type # rally or solo atttack
        self.joiners = {
            self.player1: attacker_joiners or [],
            self.player2: defender_joiners or []
        }
        self.active_skill_effects = []
        self.round_number = 1
        self.attack_counters = {
            # i need to calculate individually, as the skills can activate every x attacks for a specific troop type.
            self.player1: {
                'infantry': 0,
                'lancer': 0,
                'marksman': 0
            },
            self.player2: {
                'infantry': 0,
                'lancer': 0,
                'marksman': 0
            }
        }
        self.kill_remainders = {
            "player1": 0.0,
            "player2": 0.0
        }
    
    def do_battle(self):

        # need to add one step here first to determine if it is a rally or solo attack, then factor in joiner skills

        while self.player1.troops.total_troop_quantity > 0 and self.player2.troops.total_troop_quantity > 0 and self.round_number <= MAX_ROUNDS:
            self.do_round()
            self.round_number +=1
        print(f"Battle ended in {self.round_number} rounds")
        print(f"Player 1 troops remaining: {self.player1.troops.total_troop_quantity}")
        print(f"Player 2 troops remaining: {self.player2.troops.total_troop_quantity}")
        winner = 1 if self.player1.troops.total_troop_quantity > 0 else 2
        print(f"Player {winner} wins!")

    def do_round(self):
        # Determine target for both players
        P1_target = self.select_target(self.player2)
        P2_target = self.select_target(self.player1)

        p1_kills = 0
        p2_kills = 0

        #get the mods
        mods_p1 , mods_p2 = self.get_mods(P1_target, P2_target)

        #handle troop type skills

        if P1_target is None or P2_target is None:
            return
        
        if self.player1.troops.infantry.quantity > 0:
            troop_skills = self.process_troop_skills(self.player1.troops.infantry, P1_target, mods_p1)
            p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.infantry, P1_target, mods_p1, mods_p2, troop_skills)
            print(f"Player 1 infantry attacks Player 2 {P1_target.t_type} for {p1_kills} kills in round {self.round_number}")
            self.attack_counters[self.player1]['infantry'] += 1

        if self.player1.troops.lancer.quantity > 0:
            troop_skills = self.process_troop_skills(self.player1.troops.lancer, P1_target, mods_p1)
            if troop_skills[0] == True and self.player2.troops.marksmen.quantity > 0:
                p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.lancer, self.player2.troops.marksmen, mods_p1, mods_p2, troop_skills)
                print(f"Player 1 lancer attacks Player 2 {self.player2.troops.marksmen} for {p1_kills} kills in round {self.round_number}")
            else:
                p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.lancer, P1_target, mods_p1, mods_p2, troop_skills)
                print(f"Player 1 lancer attacks Player 2 {P1_target.t_type} for {p1_kills} kills in round {self.round_number}")
            self.attack_counters[self.player1]['lancer'] += 1

        if self.player1.troops.marksmen.quantity > 0:
            troop_skills = self.process_troop_skills(self.player1.troops.marksmen, P1_target, mods_p1)
            p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.marksmen, P1_target, mods_p1, mods_p2, troop_skills)
            # attack twice
            if troop_skills[1] == True and self.player1.troops.marksmen.quantity > 0:
                 p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.marksmen, P1_target, mods_p1, mods_p2, troop_skills)
            print(f"Player 1 marksman attacks Player 2 {P1_target.t_type} for {p1_kills} kills in round {self.round_number}")
            self.attack_counters[self.player1]['marksman'] += 1


        if self.player2.troops.infantry.quantity > 0:
            troop_skills = self.process_troop_skills(self.player2.troops.infantry, P2_target, mods_p2)
            p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.infantry, P2_target, mods_p1, mods_p2, troop_skills)
            print(f"Player 2 infantry attacks Player 1 {P2_target.t_type} for {p2_kills} kills in round {self.round_number}")
            self.attack_counters[self.player2]['infantry'] += 1

        if self.player2.troops.lancer.quantity > 0:
            troop_skills = self.process_troop_skills(self.player2.troops.lancer, P2_target, mods_p2)
            if troop_skills[0] == True:
                p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.lancer, self.player1.troops.marksmen, mods_p1, mods_p2, troop_skills)
                print(f"Player 2 lancer attacks Player 1 {self.player1.troops.marksmen.t_type} for {p2_kills} kills in round {self.round_number}")
            else:
                p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.lancer, P2_target, mods_p1, mods_p2, troop_skills)
                print(f"Player 2 lancer attacks Player 1 {P2_target.t_type} for {p2_kills} kills in round {self.round_number}")
            self.attack_counters[self.player2]['lancer'] += 1

        if self.player2.troops.marksmen.quantity > 0:
            troop_skills = self.process_troop_skills(self.player2.troops.marksmen, P2_target, mods_p2)
            p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.marksmen, P2_target, mods_p1, mods_p2, troop_skills)
            # attack twice
            if troop_skills[1] == True:
                p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.marksmen, P2_target, mods_p1, mods_p2, troop_skills)
            print(f"Player 2 marksman attacks Player 1 {P2_target.t_type} for {p2_kills} kills in round {self.round_number}")
            self.attack_counters[self.player2]['marksman'] += 1

        # apply losses
        p1_total = p1_kills + self.kill_remainders["player1"]
        p2_total = p2_kills + self.kill_remainders["player2"]

        p1_dead = math.floor(p1_total + 0.5)
        p2_dead = math.floor(p2_total + 0.5)

        self.kill_remainders["player1"] = p1_total - p1_dead
        self.kill_remainders["player2"] = p2_total - p2_dead

        P1_target.quantity = max(0, P1_target.quantity - p1_dead)
        P2_target.quantity = max(0, P2_target.quantity - p2_dead)

    def attack(self, p1, p2, attacker_troop__type, defender_troop_type, mods_p1, mods_p2, troop_skills):
        # get stats
        #attacker = attacker troops, 
        if attacker_troop__type.t_type == 'infantry':
            atk_stats = p1.stats.inf_attack, p1.stats.inf_lethality, p1.stats.inf_defense, p1.stats.inf_health
        elif attacker_troop__type.t_type == 'lancer':
            atk_stats = p1.stats.lancer_attack, p1.stats.lancer_lethality, p1.stats.lancer_defense, p1.stats.lancer_health
        elif attacker_troop__type.t_type == 'marksman':
            atk_stats = p1.stats.marks_attack, p1.stats.marks_lethality, p1.stats.marks_defense, p1.stats.marks_health

        # defffender = defender troop type
        if defender_troop_type.t_type == 'infantry':
            def_stats = p2.stats.inf_attack, p2.stats.inf_lethality, p2.stats.inf_defense, p2.stats.inf_health  
        elif defender_troop_type.t_type == 'lancer':
            def_stats = p2.stats.lancer_attack, p2.stats.lancer_lethality, p2.stats.lancer_defense, p2.stats.lancer_health
        elif defender_troop_type.t_type == 'marksman':
            def_stats = p2.stats.marks_attack, p2.stats.marks_lethality, p2.stats.marks_defense, p2.stats.marks_health

        # calculate damage
        troop_base_attack = attacker_troop__type.attack * (1 + troop_skills[2])
        attacker_mods = combine_modifiers(mods_p1, mods_p2, attacker_troop__type.t_type)
        defender_mods = combine_modifiers(mods_p2, mods_p1, defender_troop_type.t_type)

        if mods_p2["host"]["infantry"]["Crystal Shield"] == True and defender_troop_type.t_type == 'infantry': 
            attacker_damage = max(0, damage(troop_base_attack, atk_stats[0], attacker_troop__type.lethality, atk_stats[1], attacker_mods, defender_mods)-36)
        else:
            attacker_damage = damage(troop_base_attack, atk_stats[0], attacker_troop__type.lethality, atk_stats[1], attacker_mods, defender_mods)
        defender_defense = defense(defender_troop_type.defense, def_stats[2], defender_troop_type.health, def_stats[3], defender_mods, attacker_mods)

        fatigue = max(0, 1 - (self.round_number - 1) * 0.0001)

        # clac unit size effectiveness
        unit_size_attacker = self.unit_size(attacker_troop__type.quantity, p1.troops.total_troop_quantity, p2.troops.total_troop_quantity)

        # losses
        defender_dead = (unit_size_attacker * (attacker_damage / defender_defense) * fatigue)/100

        return defender_dead

    def select_target(self, player):
        if player.troops.infantry.quantity > 0:
            return player.troops.infantry
        if player.troops.lancer.quantity > 0:
            return player.troops.lancer
        if player.troops.marksmen.quantity > 0:
            return player.troops.marksmen
        return None

    def get_mods(self, attacker_target_troop, defender_target_troop):
        # process skills and modifiers
        Round_decrement = False
        if self.player1.heroes != None:
            mods_p1 = self.process_skills(self.player1, attacker_target_troop, self.round_number, self.attack_counters[self.player1][attacker_target_troop.t_type], Round_decrement)
        else:
            mods_p1 = {
            # these are buffs
            "host" : {
                "infantry" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set(), "Crystal Shield" : False  },
                "lancer" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "marksman" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "all" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() }
            },
            # these are debufs to enemy
            "enemy" : {
                "infantry" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set()  },
                "lancer" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "marksman" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "all" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() }
            }
        }
            
        Round_decrement = True
        # this needs to be modified, to only take p2 hero skills that apply to the defending troop type, and also to only apply buffs that are active during the round of the attack
        if self.player2.heroes != None:
            mods_p2 = self.process_skills(self.player2, defender_target_troop, self.round_number, self.attack_counters[self.player2][defender_target_troop.t_type], Round_decrement)
        else:
            mods_p2 = {
            # these are buffs
            "host" : {
                "infantry" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set(), "Crystal Shield" : False  },
                "lancer" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "marksman" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "all" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() }
            },
            # these are debufs to enemy
            "enemy" : {
                "infantry" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set()  },
                "lancer" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "marksman" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "all" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() }
            }
        }
        
        return mods_p1, mods_p2

    def process_troop_skills(self, attacker_troop, defender_type, modifiers):
        skills = attacker_troop.skills or {}
        ambusher = False
        volley = False
        bonus_damage = 0
        if attacker_troop.t_type == "infantry":
            chance = random.random()
            crystal_shield = skills.get("Crystal Shield")
            if crystal_shield:
                if chance < skills["Crystal Shield"]["chance"]:
                    modifiers["host"]["infantry"]["Crystal Shield"] = True
                    if "Body of light" in skills:
                        modifiers["host"]["infantry"]["defense"] += skills["Body of light"]["buff1"]["value"]
                        modifiers["host"]["infantry"]["damage_taken"] += skills["Body of light"]["buff2"]["value"]
            if defender_type.t_type == "lancer":
                modifiers["host"]["infantry"]["normal_attack_damage"] += 0.1
                modifiers["host"]["infantry"]["defense"] += 0.1
        
        if attacker_troop.t_type == "lancer":
            if defender_type.t_type == "marksman":
                modifiers["host"]["lancer"]["normal_attack_damage"] += 0.1
            #ambusher -> attack marksmen 
            if random.random() < 0.2:
                ambusher = True
            crystal_lance = skills.get("Crystal Lance")
            if crystal_lance:
                if random.random() < skills["Crystal Lance"]["chance"]:
                    modifiers["host"]["lancer"]["skill_damage"] += skills["Crystal Lance"]["value"]
                    if "Incadescent Field" in skills:
                        if random.random() < skills["Incadescent Field"]["chance"]:
                            modifiers["host"]["lancer"]["damage_taken"] += skills["Incadescent Field"]["value"]
        
        if attacker_troop.t_type == "marksman":
            if defender_type.t_type == "infantry":
                modifiers["host"]["marksman"]["normal_attack_damage"] += 0.1
            # volley skill .. chance to hit twice ... second strike will not count as a nomal attack nor trigger other skills
            if random.random() < 0.1:
                volley = True
        
            crystal_gunpowder = skills.get("Crystal Gunpowder")
            if crystal_gunpowder:
                if random.random() < skills["Crystal Gunpowder"]["chance"]:
                    modifiers["host"]["marksman"]["damage_dealt"] += skills["Crystal Gunpowder"]["value"]
                    if "Flame Charge" in skills:
                        modifiers["host"]["marksman"]["damage_dealt"] += skills["Flame Charge"]["value"]
                        #increase marksmen basic attack by 4%
                        bonus_damage += 0.04

        return [ambusher, volley, bonus_damage]

            
    def process_skills(self, player, target_troop_type, round_number, attack_number, Round_decrement):
        modifiers = {
            # these are buffs
            "host" : {
                "infantry" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set(), "Crystal Shield" : False  },
                "lancer" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "marksman" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "all" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() }
            },
            # these are debufs to enemy
            "enemy" : {
                "infantry" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set()  },
                "lancer" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "marksman" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() },
                "all" : { 'attack' : 0, 'lethality' : 0, 'defense' : 0, 'health' : 0, 'damage_dealt' : 0, 'damage_taken' : 0, "normal_attack_damage" : 0, "skill_damage" : 0, "condition" : set() }
            }
        }

        # process still active effects
        self.process_active_effects(
            player,
            modifiers,
            target_troop_type,
            round_number,
            attack_number, 
            Round_decrement
        )

        # process hero skills
        self.process_hero_skills(
            player,
            modifiers,
            target_troop_type,
            target_troop_type,
            round_number,
            attack_number
        )

        # adding joiner skills
        if self.type == "rally" or self.type == "garrison":
            for hero in self.joiners[player]:
                skill = hero.skills[0]
                for effect in skill.effects:
                    self.apply_skill_effect(
                        skill=skill,
                        effect=effect,
                        player=player,
                        modifiers=modifiers,
                        host_troop_type=target_troop_type,
                        target_troop_type=target_troop_type,
                        round_number=round_number,
                        attack_number=self.attack_counters[player][hero.hero_class],
                        still_active=self.active_skill_effects,
                        hero_class = hero.hero_class,
                        from_active_effect=True
                    )

        return modifiers
    
    def process_active_effects(self, player, modifiers, target_troop_type, round_number, attack_number, Round_decrement):
        still_active = []

        for active in self.active_skill_effects:
            if player != active["source_player"]:
                continue
            effect = active["effect"]
            skill = active["skill"]
            player = active["source_player"]
            hero_class = active["class"]

            self.apply_skill_effect(
                skill=skill,
                effect=effect,
                player=player,
                modifiers=modifiers,
                host_troop_type=active["host_troop_type"],
                target_troop_type=target_troop_type,
                round_number=round_number,
                attack_number=self.attack_counters[player][hero_class],
                still_active=still_active,
                hero_class = hero_class,
                from_active_effect=True
            )
            if Round_decrement:
                # round durations
                if active.get("remaining_turns") is not None:
                    active["remaining_turns"] -= 1
                    if active["remaining_turns"] > 0:
                        still_active.append(active)

                # attack durations
                if active.get("remaining_attacks") is not None:
                    active["remaining_attacks"] -= 1
                    if active["remaining_attacks"] > 0:
                        still_active.append(active)

        self.active_skill_effects = still_active

    def process_hero_skills(self, player, modifiers, host_troop_type, target_troop_type, round_number, attack_number):
        for hero in player.heroes:
            for skill in hero.skills:
                if not skill_activates(skill, round_number, attack_number):
                    continue

                for effect in skill.effects:
                    self.apply_skill_effect(
                    skill=skill,
                    effect=effect,
                    player=player,
                    modifiers=modifiers,
                    host_troop_type=host_troop_type,
                    target_troop_type=target_troop_type,
                    round_number=round_number,
                    attack_number=self.attack_counters[player][hero.hero_class],
                    still_active=self.active_skill_effects,
                    hero_class = hero.hero_class,
                    from_active_effect=False
                )

    def apply_skill_effect(self, skill, effect, player, modifiers, host_troop_type, target_troop_type, round_number, attack_number, still_active, hero_class, from_active_effect=False):
        modifier_sign = {
            "increase": 1,
            "decrease": -1
        }

        # troop targeting
        if not skill_applies_to_enemy_troop(effect,target_troop_type):
            return

        sign = modifier_sign.get(effect.modifier)
        if sign is None:
            raise ValueError(f"Unknown modifier type: {effect.modifier}")
        buff_type = effect.buff_type
        value = effect.value

        # convert proc damage into skill damage
        if (buff_type == "damage" and skill.activation in ["chance", "periodic"] and effect.attack_type == "skill"):
            buff_type = "skill_damage"

        # decay handling
        if skill.decay:
            if (skill.max_triggers and attack_number > skill.max_triggers):
                return
            decay_multiplier = (skill.decay ** (attack_number - 1))
            value *= decay_multiplier

        # check for condition based skill procs
        if effect.condition:
            valid = False
            for troop_target in effect.troop_target:
                if (effect.condition in modifiers[effect.target][troop_target]["condition"]):
                    valid = True
            if not valid:
                return

        # special case skill .... need to test to verify this scales correctly, may need this to be a special additive case
        if skill.name == "King's Bestowal":
            mod = player.stats.inf_attack * value
            for troop_target in effect.troop_target:
                modifiers[effect.target][troop_target][buff_type] += (mod * sign)
            return

        if skill.name == "Swift Jive":
            # this is a dodge for normal attcks, im not sure what way im going to handle this yet
            return
        
        # stackable handling
        if skill.stackable:
            still_active.append({
                "skill": skill,
                "effect": effect,
                "source_player": player,
                "host_troop_type": host_troop_type,
                "target": effect.target,
                "troop_target": effect.troop_target,
                "enemy_troop_target": effect.enemy_troop_target,
                "remaining_turns": (
                    skill.duration_turns - 1
                    if skill.duration_turns is not None
                    else None
                ),
                "remaining_attacks": (
                    skill.max_triggers
                    if skill.trigger_unit == "attack"
                    else None
                ),
                "class" : hero_class
            })

        # duration handling
        elif (skill.duration_turns is not None and not from_active_effect):
            still_active.append({
                "skill": skill,
                "effect": effect,
                "source_player": player,
                "host_troop_type": host_troop_type,
                "target": effect.target,
                "troop_target": effect.troop_target,
                "enemy_troop_target": effect.enemy_troop_target,
                "remaining_turns": skill.duration_turns - 1,
                "remaining_attacks": None,
                "class" : hero_class
            })

        # apply modifier
        for troop_target in effect.troop_target:
            modifiers[effect.target][troop_target][buff_type] += (value * sign)

        # handling a status, done last, as it only effects skill procs used on next attack or round
        if effect.applied_status:
            for troop_target in effect.troop_target:
                modifiers[effect.target][troop_target]["condition"].add(effect.applied_status)
    
    def unit_size(self, troop_quantity, p1_army_size, p2_army_size):
        return math.sqrt(troop_quantity) * math.sqrt(min(p1_army_size, p2_army_size))
    
def skill_activates(skill, round_number, attack_number):
    if skill.activation == 'always':
        return True
    if skill.activation == 'chance':
        return random.random() < skill.chance
    if skill.activation == "periodic":
        if skill.trigger_unit == 'round':
            if skill.trigger_count is None:
                return random.random() < skill.chance if skill.chance else True
            return round_number % skill.trigger_count ==0 
        if skill.trigger_unit == 'attack':
            return attack_number % skill.trigger_count == 0
    return False
    
def skill_applies_to_troop(effect, troop_type):
    if effect.troop_target == 'all':
        return True
    return troop_type in effect.troop_target

def skill_applies_to_enemy_troop(effect, troop_type):
    if effect.enemy_troop_target == 'all':
        return True
    return troop_type in effect.enemy_troop_target
