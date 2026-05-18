import json
from pathlib import Path 

INPUT_FILE = "heroes_updated.json"
OUTPUT_FILE = "heroes_final.json"

INPUT_PATH = Path(__file__).parent.parent.parent / "data" / INPUT_FILE
OUTPUT_PATH = Path(__file__).parent.parent.parent / "data" / OUTPUT_FILE

# statuses that can be applied
STATUSES = [
    "poison",
    "poisoned_target",
    "burn",
    "burning",
    "marked",
    "mark",
    "shield",
    "shielded_target",
    "stun",
    "next_turn"
]

# map old condition names -> clean names
STATUS_CLEANUP = {
    "poisoned_target": "poison",
    "shielded_target": "shield",
    "mark": "marked",
    "burning": "burn"
}


def normalize_status(status):
    if status is None:
        return None

    return STATUS_CLEANUP.get(status, status)


with open(INPUT_PATH, "r", encoding="utf-8") as f:
    heroes = json.load(f)


for hero_name, hero_data in heroes.items():

    for skill in hero_data.get("skills", []):

        for effect in skill.get("effects", []):

            condition = normalize_status(effect.get("condition"))

            # add field if missing
            effect["applied_status"] = None

            # detect status-applying effects from description
            desc = skill.get("description", "").lower()

            applies_status = None

            if "poison" in desc:
                applies_status = "poison"

            elif "burn" in desc or "flame" in desc:
                applies_status = "burn"

            elif "mark" in desc:
                applies_status = "marked"

            elif "shield" in desc:
                applies_status = "shield"

            elif "stun" in desc:
                applies_status = "stun"

            # only apply status to effects that are actually the trigger effect
            # and not the conditional follow-up effect
            if condition is None:
                effect["applied_status"] = applies_status

            # convert old condition names
            effect["condition"] = condition


with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(heroes, f, indent=4)

print(f"Updated file written to: {OUTPUT_FILE}")