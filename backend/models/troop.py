from backend.services.data_loader import *

MAX_FC_LEVEL = 10

class Formation:
    def __init__ (self, infantry, lancer, marksmen):
        self.infantry = infantry
        self.lancer = lancer
        self.marksmen = marksmen

    @property
    def total_troop_quantity(self):
        return self.infantry.quantity + self.lancer.quantity + self.marksmen.quantity

class Troop:
    def __init__ (self, t_type, level, fc, quantity):

        if quantity < 0 or not isinstance(quantity, int):
            raise ValueError ("Quantity must be a non-negative whole number")
        
        if not isinstance(level, str) or not level in ['T11', 'T10', 'T6']:
            raise ValueError ("Level must be a string of either 'T6', 'T10' or 'T11'")

        if fc <0 or fc > MAX_FC_LEVEL or not isinstance(fc, int):
            raise ValueError (f"FC must be a whole number between 0 and {MAX_FC_LEVEL}")
        
        if t_type.lower() not in ['infantry', 'lancer', 'marksman']:
            raise ValueError ("Troop type must be either 'Infantry', 'Lancer', or 'Marksman'")

        self.t_type = t_type.lower()
        self.level = level
        self.fc = fc
        self.quantity = quantity

        # troop stats
        stats = load_troop_stats(t_type.lower(), level, str(fc))
        self.attack = stats['attack']
        self.defense = stats['defense']
        self.health = stats['health']
        self.lethality = stats['lethality']
        self.skills = stats['skills']