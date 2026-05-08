from backend.services.data_loader import *
from backend.models.hero import *

t10_infantry = load_troop_stats('Infantry', 'T10', "10")
t10_lancer = load_troop_stats('Lancer', 'T10', "10")
t10_marksmen = load_troop_stats('Marksman', 'T10', "10")

# print(t10_infantry)
# print(t10_lancer)
# print(t10_marksmen)


smith = load_hero_stats('Smith')

# print(smith)

hero = Hero('Jeronimo', 5, 9)
print (hero.name)
print (hero.stars)
print (hero.skills)
print (hero.widget)