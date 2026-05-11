import math

from backend.battle.damage import *
import random

from backend.models import player, troop

class Battle:
    def __init__ (self, attacker, defender, type):
        self.player1 = attacker
        self.player2 = defender
        self.type = type # rally or solo atttack
        self.active_skill_effects = []
        self.round_number = 1
        self.attack_counters = {
            # i need to calculate individually, as the skills can activate every x attacks for a specific troop type.
            'player1': {
                'infantry': 0,
                'lancer': 0,
                'marksman': 0
            },
            'player2': {
                'infantry': 0,
                'lancer': 0,
                'marksman': 0
            }
        }
    
    def do_battle(self):

        # need to add one step here first to determine if it is a rally or solo attack, then factor in joiner skills

        while self.player1.troops.total_troop_quantity > 0 and self.player2.troops.total_troop_quantity > 0:
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

        if P1_target is None or P2_target is None:
            return
        
        if self.player1.troops.infantry.quantity > 0:
            p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.infantry, P1_target)
            print(f"Player 1 infantry attacks Player 2 {P1_target.t_type} for {p1_kills} kills in round {self.round_number}")
            self.attack_counters['player1']['infantry'] += 1
        if self.player1.troops.lancer.quantity > 0:
            p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.lancer, P1_target)
            print(f"Player 1 lancer attacks Player 2 {P1_target.t_type} for {p1_kills} kills in round {self.round_number}")
            self.attack_counters['player1']['lancer'] += 1
        if self.player1.troops.marksmen.quantity > 0:
            p1_kills += self.attack(self.player1, self.player2 ,self.player1.troops.marksmen, P1_target)
            print(f"Player 1 marksman attacks Player 2 {P1_target.t_type} for {p1_kills} kills in round {self.round_number}")
            self.attack_counters['player1']['marksman'] += 1

        if self.player2.troops.infantry.quantity > 0:
            p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.infantry, P2_target)
            print(f"Player 2 infantry attacks Player 1 {P2_target.t_type} for {p2_kills} kills in round {self.round_number}")
            self.attack_counters['player2']['infantry'] += 1
        if self.player2.troops.lancer.quantity > 0:
            p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.lancer, P2_target)
            print(f"Player 2 lancer attacks Player 1 {P2_target.t_type} for {p2_kills} kills in round {self.round_number}")
            self.attack_counters['player2']['lancer'] += 1
        if self.player2.troops.marksmen.quantity > 0:
            p2_kills += self.attack(self.player2, self.player1 ,self.player2.troops.marksmen, P2_target)
            print(f"Player 2 marksman attacks Player 1 {P2_target.t_type} for {p2_kills} kills in round {self.round_number}")
            self.attack_counters['player2']['marksman'] += 1

        # apply losses
        P1_target.quantity = max(0, P1_target.quantity - math.floor(p1_kills+0.5))
        P2_target.quantity = max(0, P2_target.quantity - math.floor(p2_kills+0.5))

    def attack(self, p1, p2, attacker_troop__type, defender_troop_type):
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
            
        # process skills and modifiers
        if self.player1.heroes != None:
            mods_p1 = self.process_skills(p1, attacker_troop__type, self.round_number, self.attack_counters[p1][attacker_troop__type.t_type])
        else:
            mods_p1 = {'attack': 0, 'lethality': 0, 'defense': 0, 'health': 0, 'damage_dealt': 0, 'damage_taken': 0}

        # this needs to be modified, to only take p2 hero skills that apply to the defending troop type, and also to only apply buffs that are active during the round of the attack
        if self.player2.heroes != None:
            mods_p2 = self.process_skills(p2, defender_troop_type, self.round_number, self.attack_counters[p2][defender_troop_type.t_type])
        else:
            mods_p2 = {'attack': 0, 'lethality': 0, 'defense': 0, 'health': 0, 'damage_dealt': 0, 'damage_taken': 0}

        # calculate damage
        attacker_damage = damage(attacker_troop__type.attack, atk_stats[0], attacker_troop__type.lethality, atk_stats[1], mods_p1)
        defender_defense = defense(defender_troop_type.defense, def_stats[2], defender_troop_type.health, def_stats[3], mods_p2)

        fatigue = max(0, 1 - (self.round_number - 1) * 0.0001)

        # clac unit size effectiveness
        unit_size_attacker = self.unit_size(attacker_troop__type.quantity, self.player1.troops.total_troop_quantity, self.player2.troops.total_troop_quantity)

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

    def process_skills(self, player, troop_type, round_number, attack_number):
        modifiers = {
            'attack' : 0,
            'lethality' : 0,
            'defense' : 0,
            'health' : 0,
            'damage_dealt' : 0,
            'damage_taken' : 0
        }

        still_active = []

        for active in self.active_skill_effects:
            effect = active['effect']
            if skill_applies_to_troop(effect, troop_type ):
                modifiers[effect.buff_type] += effect.modifier
            
            active['remaining_turns'] -=1
            if active['remaining_turns'] >0:
                still_active.append(active)

        for hero in player.heroes:
            for skill in hero.skills:
                if not skill_activates(skill, round_number, attack_number):
                        continue
                for i, effect in enumerate(skill.effects):
                    if not skill_applies_to_troop(effect, troop_type):
                        continue

                    if effect.duration_turns:
                        still_active.append({
                            'effect' : effect,
                            'remaining_turns' : skill.duration_turns-1
                        })
                        modifiers[effect.buff_type] += effect.modifier
                    else:
                        modifiers[effect.buff_type] += effect.modifier

        self.active_skill_effects = still_active
        return modifiers
    
    def unit_size(self, troop_quantity, p1_army_size, p2_army_size):
        return math.sqrt(troop_quantity) * math.sqrt(min(p1_army_size, p2_army_size))
    
def skill_activates(skill, round_number, attack_number):
    if skill.activation == 'always':
        return True
    if skill.activation == 'chance':
        return random.random() < skill.chance
    if skill.activation == 'round':
        if skill.trigger_count is None:
            return random.random() < skill.chance if skill.chance else True
        return round_number % skill.trigger_count ==0 
    if skill.activation == 'attack':
        return attack_number == skill.trigger_count
    return False
    
def skill_applies_to_troop(effect, troop_type):
    if effect.target_troops == 'all':
        return True
    return troop_type in effect.target_troops
