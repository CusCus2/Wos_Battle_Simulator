
#damage formulae
def damage(atk, atk_sts, lth, lth_sts):
    return (atk *(1+ atk_sts) * lth *(1 + lth_sts)) / 100

# defense formulae
def defense(dfn, dfn_sts, hlth, hlth_sts):
    return (dfn *(1+ dfn_sts) * hlth *(1 + hlth_sts)) / 100