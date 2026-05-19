from backend.services.data_loader import *
from backend.models.hero import *
from backend.models.troop import *
from backend.models.player import *
from backend.models.battle_result import *

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
stats_p1 = player_stats(1915.3, 1897.3, 1198.2, 1349.1, 2027.6, 1959.8, 1311.8, 1085, 1755.7, 1676.8, 1372.2, 1166.4)
stats_p2 = player_stats(1289.2, 1263, 765.2, 768.2, 1307.7, 1280.3, 683.2, 677.3, 1133.1, 1096.7, 718, 720.8)

inf_troop1 = Troop('Infantry', 'T11', 10, 97383)
lcr_troop1 = Troop('lanCer', 'T10', 9, 38953)
mrk_troop1 = Troop('Marksman', 'T11', 9, 58430)
troops_p1 = Formation(inf_troop1, lcr_troop1, mrk_troop1)

inf_troop2 = Troop('Infantry', 'T10', 9, 138637)
lcr_troop2 = Troop('lanCer', 'T10', 9, 462239)
mrk_troop2 = Troop('Marksman', 'T10', 8, 66973)
troops_p2 = Formation(inf_troop2, lcr_troop2, mrk_troop2)

fred_p1 = Hero( "Fred", 5, widget_level = 5)
gatot_p1 = Hero( "Gatot", 5, widget_level = 6)
Bradley_p1 = Hero( "Bradley", 5, widget_level = 8)

heroes_p1 = Heroes(fred_p1, gatot_p1, Bradley_p1)

fred_p2 = Hero( "Fred", 5, widget_level = 2)
gatot_p2 = Hero( "Gatot", 5, widget_level = 3)
Hendrik_p2 = Hero( "Hendrik", 5, widget_level = 2)

heroes_p2 = Heroes(fred_p2, gatot_p2, Hendrik_p2)

player1 = Player(stats_p1, heroes_p1, troops_p1)
player2 = Player(stats_p2, heroes_p2, troops_p2)

# player1 = Player(stats_p1, None, troops_p1)
# player2 = Player(stats_p2, None, troops_p2)

battle = Battle(player1, None, player2, None, 'solo attack')
battle.do_battle()

#test rallies
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