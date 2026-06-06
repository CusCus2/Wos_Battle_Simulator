from backend.models.hero import Hero, Heroes, Joiners
from backend.models.player import Player, player_stats
from backend.models.troop import Formation, Troop
from backend.schemas.battle import HeroSchema, PlayerSchema


def _build_hero(hero: HeroSchema) -> Hero:
    return Hero(hero.name, hero.stars, widget_level=hero.widget_level)


def build_player(payload: PlayerSchema) -> Player:
    stats = payload.stats
    player_stat_block = player_stats(
        stats.inf_attack,
        stats.inf_defense,
        stats.inf_health,
        stats.inf_lethality,
        stats.lancer_attack,
        stats.lancer_defense,
        stats.lancer_health,
        stats.lancer_lethality,
        stats.marks_attack,
        stats.marks_defense,
        stats.marks_health,
        stats.marks_lethality,
    )

    heroes = None
    if payload.heroes:
        hero_objects = [_build_hero(hero) for hero in payload.heroes]
        heroes = Heroes(hero_objects[0], hero_objects[1], hero_objects[2])

    troops = payload.troops
    formation = Formation(
        Troop("infantry", troops.infantry.level, troops.infantry.fc, troops.infantry.quantity),
        Troop("lancer", troops.lancer.level, troops.lancer.fc, troops.lancer.quantity),
        Troop("marksman", troops.marksmen.level, troops.marksmen.fc, troops.marksmen.quantity),
    )

    return Player(player_stat_block, heroes, formation)


def build_joiners(joiners: list[HeroSchema]) -> Joiners | None:
    if not joiners:
        return None
    return Joiners([_build_hero(hero) for hero in joiners])
