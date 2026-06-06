export const INFANTRY_HERO_NAMES = [
  "Smith",
  "Sergey",
  "Eugene",
  "Edith",
  "Gatot",
  "Magnus",
  "Gregory",
  "Eleonora",
  "Hervor",
  "Gisela",
  "Elif",
  "Hank",
  "Flint",
  "Logan",
  "Hector",
  "Wu Ming",
  "Jeronimo",
  "Natalia",
] as const;

export const LANCER_HERO_NAMES = [
  "Patrick",
  "Jessie",
  "Charlie",
  "Lumak Bokan",
  "Norah",
  "Gordon",
  "Sonya",
  "Fred",
  "Freya",
  "Lloyd",
  "Karol",
  "Flora",
  "Dominic",
  "Estrella",
  "Philly",
  "Mia",
  "Reina",
  "Gwen",
  "Renee",
  "Molly",
] as const;

export const MARKSMAN_HERO_NAMES = [
  "Bahiti",
  "Cloris",
  "Jasser",
  "Seo-yoon",
  "Bradley",
  "Hendrik",
  "Xura",
  "Blanchette",
  "Rufus",
  "Ligeia",
  "Vulcanus",
  "Cara",
  "Viveca",
  "Alonso",
  "Greg",
  "Lynn",
  "Wayne",
  "Zinman",
] as const;

export const HOST_HERO_NAMES = [
  INFANTRY_HERO_NAMES,
  LANCER_HERO_NAMES,
  MARKSMAN_HERO_NAMES,
] as const;

export const ALL_HERO_NAMES = [
  ...INFANTRY_HERO_NAMES,
  ...LANCER_HERO_NAMES,
  ...MARKSMAN_HERO_NAMES,
] as const;

export const TROOP_TIERS = ["T6", "T10", "T11", "T12"] as const;

export type TroopTier = (typeof TROOP_TIERS)[number];

export interface HeroSelection {
  name: string;
  stars: number;
  widgetLevel: number;
}

export interface TroopSlot {
  level: TroopTier;
  fc: number;
  quantity: number;
}

export interface PlayerStats {
  inf_attack: number;
  inf_defense: number;
  inf_health: number;
  inf_lethality: number;
  lancer_attack: number;
  lancer_defense: number;
  lancer_health: number;
  lancer_lethality: number;
  marks_attack: number;
  marks_defense: number;
  marks_health: number;
  marks_lethality: number;
}

export type BattleType = "rally" | "solo attack";

export interface SideConfig {
  stats: PlayerStats;
  joinersEnabled: boolean;
  heroes: [HeroSelection, HeroSelection, HeroSelection];
  joiners: HeroSelection[];
  troops: {
    infantry: TroopSlot;
    lancer: TroopSlot;
    marksmen: TroopSlot;
  };
}

export interface SimulateResponse {
  num_sims: number;
  attacker_wins: number;
  defender_wins: number;
  attacker_win_rate: number;
  defender_win_rate: number;
  average_rounds: number;
  average_attacker_survivors: number;
  average_defender_survivors: number;
}

export interface SimulationResults {
  numSims: number;
  attacker_wins : number;
  defender_wins : number;
  attackerWinRate: number;
  defenderWinRate: number;
  averageRounds: number;
  averageAttackerSurvivors: number;
  averageDefenderSurvivors: number;
}

const defaultHero = (name: string): HeroSelection => ({
  name,
  stars: 5,
  widgetLevel: 0,
});

export function deriveBattleType(
  attackerJoinersEnabled: boolean,
  defenderJoinersEnabled: boolean,
): BattleType {
  return attackerJoinersEnabled || defenderJoinersEnabled ? "rally" : "solo attack";
}

export const defaultAttacker: SideConfig = {
  joinersEnabled: true,
  stats: {
    inf_attack: 1915.3,
    inf_defense: 1897.3,
    inf_health: 1198.2,
    inf_lethality: 1349.1,
    lancer_attack: 2027.6,
    lancer_defense: 1959.8,
    lancer_health: 1311.8,
    lancer_lethality: 1085,
    marks_attack: 1755.7,
    marks_defense: 1676.8,
    marks_health: 1372.2,
    marks_lethality: 1166.4,
  },
  heroes: [
    defaultHero("Gatot"),
    defaultHero("Fred"),
    defaultHero("Bradley"),
  ],
  joiners: [
    defaultHero("Patrick"),
    defaultHero("Mia"),
    defaultHero("Renee"),
    defaultHero("Hendrik"),
  ],
  troops: {
    infantry: { level: "T11", fc: 10, quantity: 97383 },
    lancer: { level: "T10", fc: 9, quantity: 38953 },
    marksmen: { level: "T11", fc: 9, quantity: 58430 },
  },
};

export const defaultDefender: SideConfig = {
  joinersEnabled: true,
  stats: {
    inf_attack: 1289.2,
    inf_defense: 1263,
    inf_health: 765.2,
    inf_lethality: 768.2,
    lancer_attack: 1307.7,
    lancer_defense: 1280.3,
    lancer_health: 683.2,
    lancer_lethality: 677.3,
    marks_attack: 1133.1,
    marks_defense: 1096.7,
    marks_health: 718,
    marks_lethality: 720.8,
  },
  heroes: [
    defaultHero("Gatot"),
    defaultHero("Fred"),
    defaultHero("Hendrik"),
  ],
  joiners: [
    defaultHero("Patrick"),
    defaultHero("Mia"),
    defaultHero("Renee"),
    defaultHero("Hendrik"),
  ],
  troops: {
    infantry: { level: "T10", fc: 9, quantity: 138637 },
    lancer: { level: "T10", fc: 9, quantity: 462239 },
    marksmen: { level: "T10", fc: 8, quantity: 66973 },
  },
};

// export function runDummySimulation(numSims: number): SimulationResults {
//   const attackerStrength =
//     defaultAttacker.troops.infantry.quantity +
//     defaultAttacker.troops.lancer.quantity +
//     defaultAttacker.troops.marksmen.quantity;
//   const defenderStrength =
//     defaultDefender.troops.infantry.quantity +
//     defaultDefender.troops.lancer.quantity +
//     defaultDefender.troops.marksmen.quantity;

//   const ratio = attackerStrength / (attackerStrength + defenderStrength);
//   const attackerWinRate = Math.min(0.95, Math.max(0.05, ratio * 0.85 + 0.1));
//   const defenderWinRate = 1 - attackerWinRate;

//   return {
//     numSims,
//     attacker_wins,
//     defender_wins,
//     attackerWinRate,
//     defenderWinRate,
//     averageRounds: 42 + Math.round(ratio * 18),
//     averageAttackerSurvivors: 0,
//     averageDefenderSurvivors: 0,
//   };
// }
