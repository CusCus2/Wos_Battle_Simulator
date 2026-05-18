import requests
from bs4 import BeautifulSoup
names = [ "Smith", "Eugene", "Charlie", "Cloris", "Lumak Bokan", "Jasser", 
         "Seo-yoon", "Norah", "Edith", "Gordon", "Bradley", "Gatot", "Sonya", 
         "Hendrik", "Magnus", "Fred", "Xura", "Gregory", "Freya", "Blanchette", 
         "Eleonora", "Lloyd", "Rufus", "Hervor", "Karol", "Ligeia", "Gisela", 
         "Flora", "Vulcanus", "Elif", "Dominic", "Cara", "Hank", "Estrella", 
         "Viveca", "Alonso", "Flint", "Philly", "Greg", "Mia", "Logan", 
         "Lynn", "Reina", "Hector", "Gwen", "Renee", "Wayne", 
         "Wu Ming", "Zinman", "Molly", "Jeronimo", "Natalia" ]
# names = ["Jeronimo", "Natalia"]

url = "https://www.whiteoutsurvival.wiki/heroes/"

session = requests.Session()
headers = {
    "User-Agent" : "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}
cookies = {
    "pll_language": "en"
}

def get_english_soup(hero_name):
    guessed_url = url + hero_name.lower().replace(" ", "-") + "/"

    response = session.get(guessed_url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    english_link = soup.select_one('link[rel="alternate"][hreflang="en"]')

    if english_link and english_link.get("href") != response.url:
        english_url = english_link["href"]
        response = session.get(english_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

    return soup

# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'html.parser')

stat_types = ["Lethality", "Attack", "Defense", "Health"]

BUFF_KEYWORDS = {
    "attack": "attack",
    "damage dealt": "damage",
    "damage taken": "damage_taken", 
    "defense": "defense",
    "health": "health",
    "lethality": "lethality",
    "crit": "crit",
    "skill damage": "skill_damage",
    "troops' attack": "attack",
}
def detect_buff(description):

    desc = description.lower()
    keys = []
    for keyword in BUFF_KEYWORDS:
        if keyword in desc:
            keys.append(BUFF_KEYWORDS[keyword])
    if len(keys) >0:       
        return keys
    else:
        return "unknown"

def parse_values(value_string):
    if not value_string:
        return []
    
    return [
        float(v.replace("%","")) / 100
        for v in value_string.split("/")
    ]
import re

# regex functions for extracting the number of rounds, attacks or % chance skills
def extract_duration(description):
    match = re.search(r"for (\d+) turns?", description.lower())
    return int(match.group(1)) if match else None

def extract_trigger_count(description):
    match = re.search(r"every (\d+) (attacks|strikes|rounds|turns)", description.lower())
    return int(match.group(1)) if match else None

def extract_chance(description):
    match = re.search(r"(\d+)% chance", description.lower())
    return int(match.group(1)) / 100 if match else None

# buffing all troops or specific type
def extract_trigger_troops(description):
    text = description.lower()
    target = []
    if "by infantry" in text or "infantry" in text:
        target.append( "infantry" )
    if "by lancers" in text or "lancers" in text:
        target.append( "lancer" )
    if "by marksmen" in text or "marksmen" in text:
        target.append( "marksman" )

    return target if target else "all"

# buffing enemy or hot troops
def extract_target(description):
    text = description.lower()
    if "enemy" in text:
        return "enemy"
    return "host" 

# this determines activation type, so flat buff or round based etc
def extract_activation(description):
    text = description.lower()
    if "every" in text and ("attack" in text or "strike" in text):
        return "attack"
    if "round" in text or "turn" in text:
        return "round"
    if "chance" in text:
        return "chance"
    return "always"

def normalise_troop_target(target):
    if target is None:
        return ["all"]

    if isinstance(target, str):
        target = target.lower()

        if target in ["all", "all troops", "troops"]:
            return ["all"]

        if target in ["marksman", "marksmen", "ranged"]:
            return ["marksmen"]

        return [target]

    return target


def normalise_class(hero_class):
    hero_class = hero_class.lower()

    mapping = {
        "infantry": "infantry",
        "lancer": "lancer",
        "marksman": "marksmen",
        "marksmen": "marksmen"
    }

    return mapping.get(hero_class, hero_class)


def parse_percent(text):
    if text is None:
        return None

    text = text.replace("+", "").replace("%", "").replace(",", ".").strip()
    return float(text) / 100

def extract_activation(description):
    text = description.lower()

    if "every" in text:
        if any(word in text for word in ["attack", "attacks", "strike", "strikes"]):
            return "periodic", "attack"

        if any(word in text for word in ["turn", "turns", "round", "rounds"]):
            return "periodic", "round"

    if "chance" in text:
        return "chance", "attack"

    return "always", None

def extract_modifier(description, buff_type):
    text = description.lower()

    decrease_words = [
        "reduce", "reducing", "decrease", "decreasing",
        "less", "lower", "lowering"
    ]

    increase_words = [
        "increase", "increasing", "boost", "boosting",
        "grant", "granting", "more", "additional", "extra"
    ]

    if any(word in text for word in decrease_words):
        return "decrease"

    if any(word in text for word in increase_words):
        return "increase"

    return "increase"

def extract_condition(description):
    text = description.lower()

    conditions = {
        "marked_target": [
            "marked target",
            "dream mark",
            "dream marks"
        ],

        "poisoned_target": [
            "poison",
            "poisoned"
        ],

        "normal_attack": [
            "normal attack",
            "normal attacks"
        ],

        "skill_damage": [
            "skill damage",
            "from skills"
        ],

        "shielded_target": [
            "shield"
        ]
    }

    for condition, keywords in conditions.items():
        if any(keyword in text for keyword in keywords):
            return condition

    return None

import re


def extract_stackable(description):
    text = description.lower()

    stack_keywords = [
        "stackable",
        "stacks",
        "stacking"
    ]

    return any(word in text for word in stack_keywords)


def extract_max_stacks(description):
    text = description.lower()

    # Example future phrasing:
    # "can stack up to 5 times"

    match = re.search(r"stack up to (\d+)", text)

    if match:
        return int(match.group(1))

    return None


def extract_decay(description):
    text = description.lower()

    # Hector:
    # "each attack's damage boost being 85% of the previous one"

    match = re.search(r"(\d+)% of the previous", text)

    if match:
        return int(match.group(1)) / 100

    return None


def extract_max_triggers(description):
    text = description.lower()

    # Hector:
    # "effective for 10 attacks"

    match = re.search(r"for (\d+) attacks", text)

    if match:
        return int(match.group(1))

    return None


def extract_damage_source(description):
    text = description.lower()

    if "normal attack" in text or "normal attacks" in text:
        return "normal"

    if "skill damage" in text or "from skills" in text:
        return "skill"

    return "all"

def build_effect(description, buff_type, values):
    return {
        "buff_type": buff_type,
        "target": extract_target(description).lower(),
        "troop_target": normalise_troop_target(extract_trigger_troops(description)),
        "modifier": extract_modifier(description, buff_type),
        "values": values,
        "condition": extract_condition(description),
        "damage_source": extract_damage_source(description)
    }


def build_skill(name, description, effects):
    activation, trigger_unit = extract_activation(description)

    return {
        "name": name,
        "description": description,
        "activation": activation,
        "trigger_unit": trigger_unit,
        "trigger_count": extract_trigger_count(description),
        "duration_turns": extract_duration(description),
        "chance": extract_chance(description),
        "stackable": extract_stackable(description),
        "max_stacks": extract_max_stacks(description),
        "decay": extract_decay(description),
        "max_triggers": extract_max_triggers(description),
        "condition": extract_condition(description),
        "effects": effects
    }


#grabbing just expedition skills and stats for now, will add more later
heroes = {}
for hero in names:
    print(hero)
    hero_name = hero
    # hero_url = url+hero_name.lower().replace(" ", "-")
    # # hero_response = requests.get(hero_url)
    # hero_response = session.get(
    #     hero_url,
    #     headers = headers,
    #     cookies = cookies,
    #     timeout = 10
    # )
    # print(hero_url)
    # soup = BeautifulSoup(hero_response.text, 'html.parser')
    # print(soup)
    soup = get_english_soup(hero)

    #basic info
    hero_info = soup.find_all("div", class_="hero-attr-item")
    hero_class_section = hero_info[1] if len(hero_info) > 0 else None
    hero_class_line = hero_class_section.find("div", class_="hero-attr-value")
    hero_class = hero_class_line.find("span").text.strip() if hero_class_line else "Unknown"


    #stats
    hero_attack = soup.select("div.hero-stats-value")[3].text.strip()
    hero_defense = soup.select("div.hero-stats-value")[4].text.strip()

    #skills
    skills = []
    skills_section = soup.find_all("div", class_="vstack gap-3")
    expedition_skills_section = skills_section[1] if len(skills_section) > 1 else None
    cards = expedition_skills_section.find_all("div", class_="bg-dark rounded p-3 text-light position-relative")

    for card in cards:
        name = card.find("h5").text.strip()
        description = card.find("p", class_="mt-2").text.strip()

        buffs_values = card.select("strong span")
        keys = detect_buff(description)

        if isinstance(keys, str):
            keys = [keys]

        effects = []

        for i, buff in enumerate(buffs_values):
            buff_text = buff.text.strip()
            values = parse_values(buff_text)

            buff_type = keys[i] if i < len(keys) else "unknown"

            effect = build_effect(
                description=description,
                buff_type=buff_type,
                values=values
            )

            effects.append(effect)

        skill = build_skill(
            name=name,
            description=description,
            effects=effects
        )

        skills.append(skill)
    
    #widget
    widget_dict = None
    hero_section = soup.find("div", class_="bak-col align-self-center")
    if hero_section:
        widget = hero_section.find_all("p", class_="mt-2")
        if len(widget) > 1:
            hero_widget = widget[1].text.strip()
            widget_stat = None
            if 'Defender' in hero_widget:
                widget_type = "Defender"
            else:
                widget_type = "Attacker"
            for stat in stat_types:
                if stat.lower() in hero_widget.lower():
                    widget_stat = stat
                    break
            widget_dict = {
                "type": widget_type,
                "stat": widget_stat
            }

    hero_data = {
        "class": normalise_class(hero_class),
        "attack": parse_percent(hero_attack),
        "defense": parse_percent(hero_defense),
        "widget": widget_dict["type"] if widget_dict else None,
        "widget_buff": widget_dict["stat"].lower() if widget_dict and widget_dict["stat"] else None,
        "skills": skills
    }

    heroes[hero_name] = hero_data
# print(heroes)
import json
from pathlib import Path
path = Path(__file__).parent.parent.parent / "data" / "heroes.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(heroes, f, indent=4)

print("Saved", len(heroes), "heroes to heroes.json")