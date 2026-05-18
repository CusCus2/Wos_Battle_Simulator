from pathlib import Path
import json

# Troop data

def load_troop_data():
    path = Path(__file__).parent.parent.parent / "data" / "troops.json" # path is /backend / data / troops

    with open(path, "r") as f:
        return json.load(f)

def load_troop_stats(troop_type, troop_level, FC_level):
    data = load_troop_data()
    return data[troop_type][troop_level][FC_level]


# Hero data

def load_hero_data():
    path = Path(__file__).parent.parent.parent / "data" / "heroes_final.json"

    with open(path, "r") as f:
        return json.load(f)

def load_hero_stats(hero):
    data = load_hero_data()
    return data[hero]