from backend.services.data_loader import *
from backend.models.hero import *
from backend.models.troop import *
from backend.models.player import *
from backend.models.battle_result import *


stats_p1 = player_stats(22.9, 22.9, 11.5, 11.5, 22.9, 22.9, 11.5, 11.5, 22.9, 22.9, 11.5, 11.5)
stats_p2 = player_stats(14.8, 13.3, 5.5, 5.5, 13.1, 13.3, 5.5, 5.5, 13.1, 13.3, 5.5, 5.5)

inf_troop1 = Troop('Infantry', 'T6', 0, 100)
lcr_troop1 = Troop('lanCer', 'T6', 0, 100)
mrk_troop1 = Troop('Marksman', 'T6', 0, 100)
troops_p1 = Formation(inf_troop1, lcr_troop1, mrk_troop1)

inf_troop2 = Troop('Infantry', 'T6', 0, 100)
lcr_troop2 = Troop('lanCer', 'T6', 0, 100)
mrk_troop2 = Troop('Marksman', 'T6', 0, 100)
troops_p2 = Formation(inf_troop2, lcr_troop2, mrk_troop2)

player2 = Player(stats_p1, None, troops_p1)
player1 = Player(stats_p2, None, troops_p2)

battle = Battle(player1, None, player2, None, 'solo attack')
battle.do_battle()