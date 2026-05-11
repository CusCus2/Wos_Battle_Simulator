from backend.services.data_loader import *
from backend.models.hero import *
from backend.models.troop import *
from backend.models.player import *

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

inf_troop = Troop('Infantry', 'T11', 10, 45000)
lcr_troop = Troop('lanCer', 'T11', 10, 45000)
mrk_troop = Troop('Marksman', 'T11', 10, 45000)

army = Formation(inf_troop, lcr_troop, mrk_troop)
print(army.infantry.quantity)
print(army.infantry.t_type)
print(army.infantry.level)
print(army.infantry.fc)

print(army.lancer.quantity)
print(army.lancer.t_type)
print(army.lancer.level)
print(army.lancer.fc)

print(army.marksmen.quantity)
print(army.marksmen.t_type)
print(army.marksmen.level)
print(army.marksmen.fc)