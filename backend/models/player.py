class player:
    def __init__ (self, stats, heroes, troops):
        self.stats = stats
        self.heroes = heroes
        self.troops = troops
    


class player_stats:
    def __init__ (self, inf_attack, inf_defense, inf_health, inf_lethality, lancer_attack, lancer_defense, lancer_health, lancer_lethality, marks_attack,
                   marks_defense, marks_health, marks_lethality):
        self.inf_attack = inf_attack
        self.inf_defense = inf_defense
        self.inf_health = inf_health
        self.inf_lethality = inf_lethality
        self.lancer_attack = lancer_attack
        self.lancer_defense = lancer_defense
        self.lancer_health = lancer_health
        self.lancer_lethality = lancer_lethality
        self.marks_attack = marks_attack
        self.marks_defense = marks_defense
        self.marks_health = marks_health
        self.marks_lethality = marks_lethality
