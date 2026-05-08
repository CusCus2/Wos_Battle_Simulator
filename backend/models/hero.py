from backend.services.data_loader import *

MAX_STAR_LEVEL = 5
MAX_WIDGET_LEVEL = 10

class Hero:
    def __init__ (self, name, stars, widget_level = 0):
        
        # validate inputs
        if stars > MAX_STAR_LEVEL or stars <1 or not isinstance(stars, int):
            raise ValueError (f"Stars must be a whole number between 1 and {MAX_STAR_LEVEL}")

        if widget_level > MAX_WIDGET_LEVEL or widget_level <0 or not isinstance(widget_level, int):
            raise ValueError (f"widget level must be a whole number between 0 and {MAX_WIDGET_LEVEL}")
        
        self.name = name
        self.stars = stars
        self.widget_level = widget_level

        hero_data = load_hero_stats(name)

        self.hero_class = hero_data['class']
        self.skills = hero_data['skills']
        self.widget = hero_data['widget']