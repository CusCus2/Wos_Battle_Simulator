from backend.services.data_loader import *
from backend.models.hero import *
from backend.models.troop import *
from backend.models.player import *

data = load_hero_data()
infantry = []
lancer = []
marksmen = []
for hero_name, hero_data in data.items():
    if hero_data["class"] == "infantry":
        infantry.append(hero_name)
    elif hero_data["class"] == "lancer":
        lancer.append(hero_name)
    else:
        marksmen.append(hero_name)

print(infantry)
print(lancer)
print(marksmen)