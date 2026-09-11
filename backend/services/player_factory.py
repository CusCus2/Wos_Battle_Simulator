from backend.models.hero import Hero, Heroes, Joiners
from backend.models.player import Player, PlayerStats, TroopStats
from backend.models.troop import Formation, Troop
from backend.schemas.battle import HeroSchema, PlayerSchema


def _build_hero(hero: HeroSchema) -> Hero:
    return Hero(
        hero.name,
        hero.stars,
        widget_level=hero.widget_level,
    )


def build_player(payload: PlayerSchema) -> Player:
    stats = payload.stats

    # The API stays flat for now, while the internal battle model becomes:
    # player.stats.infantry.attack
    # player.stats.lancer.defense
    # etc.
    player_stat_block = PlayerStats(
        infantry=TroopStats(
            attack=stats.inf_attack / 100,
            defense=stats.inf_defense / 100,
            health=stats.inf_health / 100,
            lethality=stats.inf_lethality / 100,
        ),
        lancer=TroopStats(
            attack=stats.lancer_attack / 100,
            defense=stats.lancer_defense / 100,
            health=stats.lancer_health / 100,
            lethality=stats.lancer_lethality / 100,
        ),
        marksman=TroopStats(
            attack=stats.marks_attack / 100,
            defense=stats.marks_defense / 100,
            health=stats.marks_health / 100,
            lethality=stats.marks_lethality / 100,
        ),
    )

    heroes = None

    if payload.heroes:
        hero_objects = [
            _build_hero(hero)
            for hero in payload.heroes
        ]

        heroes = Heroes(
            hero_objects[0],
            hero_objects[1],
            hero_objects[2],
        )

    troops = payload.troops

    formation = Formation(
        Troop(
            "infantry",
            troops.infantry.level,
            troops.infantry.fc,
            troops.infantry.quantity,
            troops.infantry.exalted_level,
        ),
        Troop(
            "lancer",
            troops.lancer.level,
            troops.lancer.fc,
            troops.lancer.quantity,
            troops.lancer.exalted_level,
        ),
        Troop(
            "marksman",
            troops.marksmen.level,
            troops.marksmen.fc,
            troops.marksmen.quantity,
            troops.marksmen.exalted_level,
        ),
    )

    return Player(
        player_stat_block,
        heroes,
        formation,
    )


def build_joiners(
    joiners: list[HeroSchema],
) -> Joiners | None:
    if not joiners:
        return None

    return Joiners(
        [_build_hero(hero) for hero in joiners]
    )
