class Player:
    def __init__ (self, stats, heroes, troops):
        self.stats = stats
        self.heroes = heroes
        self.troops = troops
    


class player_stats:
    def __init__ (self, inf_attack, inf_defense, inf_health, inf_lethality, lancer_attack, lancer_defense, lancer_health, lancer_lethality, marks_attack,
                   marks_defense, marks_health, marks_lethality):
        # divide by 100 to convert to decimal
        self.inf_attack = inf_attack/100
        self.inf_defense = inf_defense/100
        self.inf_health = inf_health/100
        self.inf_lethality = inf_lethality/100
        self.lancer_attack = lancer_attack/100
        self.lancer_defense = lancer_defense/100
        self.lancer_health = lancer_health/100
        self.lancer_lethality = lancer_lethality/100
        self.marks_attack = marks_attack/100
        self.marks_defense = marks_defense/100
        self.marks_health = marks_health/100
        self.marks_lethality = marks_lethality/100
