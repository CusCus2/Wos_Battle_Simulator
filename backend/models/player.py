from dataclasses import dataclass

class Player:
    def __init__ (self, stats, heroes, troops):
        self.stats = stats
        self.heroes = heroes
        self.troops = troops
    

@dataclass
class TroopStats:
    attack: float
    defense: float
    health: float
    lethality: float


@dataclass
class PlayerStats:
    infantry: TroopStats
    lancer: TroopStats
    marksman: TroopStats

    def get(self, troop_type: str) -> TroopStats:
        return getattr(self, troop_type)
    
# class player_stats:
#     def __init__ (self, inf_attack, inf_defense, inf_health, inf_lethality, lancer_attack, lancer_defense, lancer_health, lancer_lethality, marks_attack,
#                    marks_defense, marks_health, marks_lethality):
#         # divide by 100 to convert to decimal
#         self.breakdown = PlayerStats(
#             infantry = TroopStats(
#                 attack = inf_attack/100,
#                 defense = inf_defense/100,
#                 health = inf_health/100,
#                 lethality = inf_lethality/100,
#             ),
#             lancer = TroopStats(
#                 attack = lancer_attack/100,
#                 defense = lancer_defense/100,
#                 health = lancer_health/100,
#                 lethality = lancer_lethality/100,
#             ),
#             marksman = TroopStats(
#                 attack = marks_attack/100,
#                 defense = marks_defense/100,
#                 health = marks_health/100,
#                 lethality = marks_lethality/100,
#             )
#         )
