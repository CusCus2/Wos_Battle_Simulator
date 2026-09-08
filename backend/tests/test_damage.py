from backend.services.data_loader import *
from backend.models.hero import *
from backend.models.troop import *
from backend.models.player import *
from backend.models.battle_result import *
from backend.battle.simulator import *

# test without heroes
# stats_p1 = player_stats(22.9, 22.9, 11.5, 11.5, 22.9, 22.9, 11.5, 11.5, 22.9, 22.9, 11.5, 11.5)
# stats_p2 = player_stats(14.8, 13.3, 5.5, 5.5, 13.1, 13.3, 5.5, 5.5, 13.1, 13.3, 5.5, 5.5)

# inf_troop1 = Troop('Infantry', 'T11', 10, 100)
# lcr_troop1 = Troop('lanCer', 'T10', 9, 100)
# mrk_troop1 = Troop('Marksman', 'T11', 9, 100)
# troops_p1 = Formation(inf_troop1, lcr_troop1, mrk_troop1)

# inf_troop2 = Troop('Infantry', 'T11', 10, 100)
# lcr_troop2 = Troop('lanCer', 'T11', 10, 100)
# mrk_troop2 = Troop('Marksman', 'T11', 10, 100)
# troops_p2 = Formation(inf_troop2, lcr_troop2, mrk_troop2)

# player1 = Player(stats_p1, None, troops_p1)
# player2 = Player(stats_p2, None, troops_p2)

# battle = Battle(player1, None, player2, None, 'solo attack')
# battle.do_battle()

# test with heroes
stats_p1 = player_stats(1678.7, 1749.6, 979.6, 1173.9, 1080.6, 1137, 665.6, 635.1, 1942.9, 1982.7, 1293.7, 1224.8)
stats_p2 = player_stats(3250, 3250, 3250, 3250, 3250, 3250, 3250, 3250, 3250, 3250, 3250, 3250)

inf_troop1 = Troop('Infantry', 'T11', 10, 88260)
lcr_troop1 = Troop('lanCer', 'T10', 9, 0)
mrk_troop1 = Troop('Marksman', 'T11', 10, 88260)
troops_p1 = Formation(inf_troop1, lcr_troop1, mrk_troop1)

inf_troop2 = Troop('Infantry', 'T10', 0, 182000)
lcr_troop2 = Troop('lanCer', 'T10', 0, 182000)
mrk_troop2 = Troop('Marksman', 'T10', 0, 182000)
troops_p2 = Formation(inf_troop2, lcr_troop2, mrk_troop2)

mia_p1 = Hero( "Mia", 5, widget_level = 5)
gatot_p1 = Hero( "Gatot", 5, widget_level = 6)
blanchette_p1 = Hero( "Blanchette", 5, widget_level = 8)

joiners_p1 = Joiners([
    Hero("Patrick", 5),
    Hero("Mia", 5),
    Hero("Renee", 5),
    Hero("Hendrik", 5)
    ])

heroes_p1 = Heroes(mia_p1, gatot_p1, blanchette_p1)

fred_p2 = Hero( "Fred", 5, widget_level = 2)
gatot_p2 = Hero( "Gatot", 5, widget_level = 3)
Hendrik_p2 = Hero( "Hendrik", 5, widget_level = 2)

joiners_p2 = Joiners([
    Hero("Patrick", 5),
    Hero("Mia", 5),
    Hero("Renee", 5),
    Hero("Hendrik", 5)
    ])


heroes_p2 = Heroes(fred_p2, gatot_p2, Hendrik_p2)

player1 = Player(stats_p1, heroes_p1, troops_p1)
player2 = Player(stats_p2, None, troops_p2)

# player1 = Player(stats_p1, None, troops_p1)
# player2 = Player(stats_p2, None, troops_p2)

battle = Battle(player1, None, player2, None, 'solo attack')
# battle = Battle(player1, joiners_p1, player2, joiners_p2, 'rally')

battle.do_battle()
# sim(player1, joiners_p1, player2, joiners_p2, 1000)

# #test rallies
# stats_p1 = player_stats(1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000)
# stats_p2 = player_stats(1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000)

# inf_troop1 = Troop('Infantry', 'T11', 10, 3333)
# lcr_troop1 = Troop('lanCer', 'T12', 10, 3333)
# mrk_troop1 = Troop('Marksman', 'T11', 10, 3333)
# troops_p1 = Formation(inf_troop1, lcr_troop1, mrk_troop1)

# inf_troop2 = Troop('Infantry', 'T11', 10, 3333)
# lcr_troop2 = Troop('lanCer', 'T11', 10, 3333)
# mrk_troop2 = Troop('Marksman', 'T12', 10, 3333)
# troops_p2 = Formation(inf_troop2, lcr_troop2, mrk_troop2)

# player1 = Player(stats_p1, None, troops_p1)
# player2 = Player(stats_p2, None, troops_p2)
# print("player 1 has T12 lancer, player 2 has T12 marksman")
# # battle = Battle(player1, None, player2, None, 'solo attack')
# # battle.do_battle()

# sim(player1, player2, 1000)