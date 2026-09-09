from backend.services.data_loader import *

MAX_STAR_LEVEL = 5
MAX_WIDGET_LEVEL = 10

class Heroes:
    def __init__(self,hero1, hero2, hero3):
        self.hero1 = hero1
        self.hero2 = hero2
        self.hero3 = hero3

        self.heroes = [
            hero1,
            hero2,
            hero3
        ]
        
    def __iter__(self):
        return iter(self.heroes)
    
    def __len__(self):
        return len(self.heroes)
    
    @property
    def all_skills(self):

        skills = []

        for hero in self.heroes:
            skills.extend(hero.skills)

        return skills

class Joiners:
    MAX_JOINERS = 4

    def __init__ (self, heroes):
        if len(heroes) > self.MAX_JOINERS:
            raise ValueError(f"Cannot have more than 4 joiner heroes")

        self.heroes = heroes

    def __iter__(self):
        return iter(self.heroes)
    
    @property
    def active_skills(self):
        return [hero.skills[0] for hero in self.heroes]

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

        trigger = raw_skill["trigger"]

        # Trigger rules
        self.trigger_event = trigger["event"]
        self.trigger_troop = trigger.get("troop")
        self.counter = trigger.get("counter")
        self.every = trigger.get("every", 1)

        # Chance can either be a fixed float or a star-scaled list
        raw_chance = trigger.get("chance", 1.0)

        if isinstance(raw_chance, list):
            self.chance = raw_chance[stars - 1]
        else:
            self.chance = raw_chance

        self.trigger_attack_type = trigger.get("attack_type", "all")
        self.trigger_required_status = trigger.get("required_status")

        # Effects
        self.effects = [
            SkillEffect(effect, stars)
            for effect in raw_skill["effects"]
        ]


class SkillEffect:
    def __init__(self, raw_effect, stars):
        # What kind of effect this is:
        # modifier, direct_damage, status, extra_attack,
        # shield, dodge, skip_attack, etc.
        self.effect_type = raw_effect.get("effect_type", "modifier")

        # Main stat / value
        self.stat = raw_effect.get("stat")

        values = raw_effect.get("values")

        if values is None:
            self.value = None
        else:
            self.value = values[stars - 1]

        self.modifier = raw_effect.get("modifier") # increase/decrease

        # Targeting
        self.target_side = raw_effect.get("target_side", "host")
        self.target_troops = raw_effect.get("target_troops", ["all"])
        self.enemy_troops = raw_effect.get("enemy_troops", ["all"])

        # What attack type this effect applies to
        self.attack_type = raw_effect.get("attack_type", "all")

        # Status handling
        self.required_status = raw_effect.get("required_status")
        self.applied_status = raw_effect.get("applied_status")
        self.consume_status = raw_effect.get("consume_status")

        # When the effect actually happens relative to the trigger
        self.timing = raw_effect.get("timing", "on_trigger")

        # Duration
        duration = raw_effect.get(
            "duration",
            {
                "type": "current_event",
                "value": None
            }
        )

        self.duration_type = duration.get("type", "current_event")
        self.duration_value = duration.get("value")

        # Optional special behaviour
        self.scaling_stat = raw_effect.get("scaling_stat", None)
        self.decay = raw_effect.get("decay", None)
        self.stackable = raw_effect.get("stackable", False)