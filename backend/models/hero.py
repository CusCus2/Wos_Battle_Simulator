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
        self.skills = [Skill(skill, stars)for skill in hero_data['skills']]
        self.widget = hero_data['widget']

class Skill:
    def __init__(self, raw_skill, stars):
        self.name = raw_skill["name"]
        self.description = raw_skill["description"]

        self.activation = raw_skill["activation"]
        self.trigger_count = raw_skill["trigger_count"]
        self.duration_turns = raw_skill["duration_turns"]
        self.chance = raw_skill["chance"]

        self.effects = [
            SkillEffect(effect, stars)
            for effect in raw_skill["effects"]
        ]

class SkillEffect:
    def __init__(self, raw_effect, stars):
        self.buff_type = raw_effect["buff_type"]
        self.modifier = raw_effect["values"][stars - 1]
        self.target = raw_effect["target"]
        self.target_troops = raw_effect["target_troops"]