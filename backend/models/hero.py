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
        self.effect_timing = raw_skill["effect_timing"]
        self.trigger_unit = raw_skill["trigger_unit"]
        self.stackable = raw_skill["stackable"]
        self.max_stacks = raw_skill["max_stacks"]
        self.decay = raw_skill["decay"]
        self.max_triggers = raw_skill["max_triggers"]
        self.condition = raw_skill["condition"]

        self.effects = [
            SkillEffect(effect, stars)
            for effect in raw_skill["effects"]
        ]

class SkillEffect:
    def __init__(self, raw_effect, stars):
        self.buff_type = raw_effect["buff_type"]
        self.value = raw_effect["values"][stars - 1]/100 # convert the percentage to decimal
        self.target = raw_effect["target"]
        self.troop_target = raw_effect["troop_target"]
        self.modifier = raw_effect["modifier"]
        self.target = raw_effect["target_troops"]
        self.damage_source = raw_effect["damage_source"]
        self.attack_type = raw_effect["attack_type"]
        self.condition = raw_effect["condition"]
        self.applied_status = raw_effect["applied_status"]