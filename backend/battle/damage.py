def combine_modifiers(attacker_mods,defender_mods, attacker_troop_type):
    final = {}
    keys = [
        "attack",
        "lethality",
        "defense",
        "health",
        "damage_dealt",
        "damage_taken",
        "normal_attack_damage",
        "skill_damage"
    ]

    for key in keys:
        host_value = (attacker_mods["host"][attacker_troop_type][key] + attacker_mods["host"]["all"][key])
        enemy_value = (defender_mods["enemy"][attacker_troop_type][key] + defender_mods["enemy"]["all"][key])
        final[key] = host_value + enemy_value

    return final

#damage formulae
def damage(atk, atk_sts, lth, lth_sts, attacker_mods, defender_mods):
    effective_attack = (atk* (1 + atk_sts)* (1 + attacker_mods["attack"]))
    effective_lethality = (lth* (1 + lth_sts)* (1 + attacker_mods["lethality"]))

    raw_damage = (effective_attack* effective_lethality) / 100

    normal_damage = raw_damage * (attacker_mods["normal_attack_damage"])
    skill_damage = raw_damage * (attacker_mods["skill_damage"])
    damage = raw_damage + normal_damage + skill_damage

    total_damage = damage * (1 + attacker_mods["damage_dealt"])
    return total_damage

# defense formulae
def defense(dfn, dfn_sts, hlth, hlth_sts, defender_mods, attacker_mods):
    effective_defense = (dfn * (1 + dfn_sts) * (1 + defender_mods["defense"]))
    effective_health = (hlth * (1 + hlth_sts) * (1 + defender_mods["health"]))

    total_defense = (effective_defense * effective_health) / 100
    total_defense /= (1 - defender_mods["damage_taken"])
    return total_defense