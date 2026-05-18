
from backend.services.data_loader import load_hero_data


data = load_hero_data()

KEYWORDS = {
    "attack": ["attack"],
    "lethality": ["lethality"],
    "health": ["health"],
    "defense": ["defense"],
    "damage_dealt": ["damage dealt", "extra damage", "more damage", "additional damage"],
    "damage_taken": ["damage taken", "damage received", "reducing damage taken"],
    "crit": ["crit", "critical"],
    "dodge": ["dodge"],
    "stun": ["stun"],
    "shield": ["shield"],
    "extra_attack": ["extra attack"],
}
for hero in data:
    print(hero)
    for skill in data[hero]['skills']:
        description = skill['description'].lower()
        buffs = set()
        for key in KEYWORDS:
            for keyword in KEYWORDS[key]:
                if keyword in description:
                    buffs.add(key)
                    print(f"Found {key} in {skill['name']}")
        skill['effects'] = list(buffs)

print(data['wayne'][ 'skills'][2]['effects'])
