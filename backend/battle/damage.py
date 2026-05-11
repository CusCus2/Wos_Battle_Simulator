
#damage formulae
def damage(atk, atk_sts, lth, lth_sts, mods):
    return ( (  ((atk *(1+ atk_sts)) * (1 + mods['attack'])) * ((lth *(1 + lth_sts)) * (1 + mods['lethality']))  ) / 100) * (1 + mods['damage_dealt'])

# defense formulae
def defense(dfn, dfn_sts, hlth, hlth_sts, mods):
    return ( (  ((dfn *(1+ dfn_sts)) * (1 + mods['defense'])) * ((hlth *(1 + hlth_sts)) * (1 + mods['health']))  ) / 100) / (1 - mods['damage_taken'])