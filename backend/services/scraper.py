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

    for keyword in BUFF_KEYWORDS:
        if keyword in desc:
            return BUFF_KEYWORDS[keyword]

    return "unknown"

def parse_values(value_string):
    if not value_string:
        return []
    
    return [
        float(v.replace("%","")) / 100
        for v in value_string.split("/")
    ]

#grabbing just expedition skills and stats for now, will add more later
heroes = {}
for hero in names:
    print(hero)
    hero_name = hero
    hero_url = url+hero_name.lower().replace(" ", "-")
    hero_response = requests.get(hero_url)
    soup = BeautifulSoup(hero_response.text, 'html.parser')

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

        value_tag = card.select_one("strong span")

        values = value_tag.text.strip() if value_tag else None

        skill = {
            "name": name,
            "description": description,
            "buff_type": detect_buff(description),
            "values": parse_values(values)
        }

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
        "class": hero_class,
        "attack": hero_attack,
        "defense": hero_defense,
        "widget": widget_dict,
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