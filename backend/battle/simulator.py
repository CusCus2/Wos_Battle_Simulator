from backend.models.battle_result import *

def sim(attacker, attacker_joiners, defender, defender_joiners, num_sims):
    results = {
        'attacker_wins': 0,
        'defender_wins': 0,
    }
    for _ in range(num_sims):
        battle = Battle(attacker, attacker_joiners, defender, defender_joiners, 'rally')
        res = battle.do_battle()
        if res == 1:
            results['attacker_wins'] += 1
        else:
            results['defender_wins'] += 1
        
    
    print(f"After {num_sims} simulations:")
    print(f"Attacker wins: {results['attacker_wins']} ({results['attacker_wins']/num_sims*100:.2f}%)")
    print(f"Defender wins: {results['defender_wins']} ({results['defender_wins']/num_sims*100:.2f}%)")
    return results
