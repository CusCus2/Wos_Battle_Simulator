from backend.services.data_loader import *

MAX_FC_LEVEL = 10

class Formation:
    def __init__ (self, infantry, lancer, marksmen):
        self.infantry = infantry
        self.lancer = lancer
        self.marksmen = marksmen

class Troop:
    def __init__ (self, t_type, level, fc, quantity):

        if quantity < 0 or not isinstance(quantity, int):
            raise ValueError ("Quantity must be a non-negative whole number")
        
        if not isinstance(level, str) or not level in ['T11', 'T10']:
            raise ValueError ("Level must be a string of either 'T10' or 'T11'")

        if fc <0 or fc > MAX_FC_LEVEL or not isinstance(fc, int):
            raise ValueError (f"FC must be a whole number between 0 and {MAX_FC_LEVEL}")
        
        if t_type.lower() not in ['infantry', 'lancer', 'marksman']:
            raise ValueError ("Troop type must be either 'Infantry', 'Lancer', or 'Marksman'")

        self.t_type = t_type
        self.level = level
        self.fc = fc
        self.quantity = quantity