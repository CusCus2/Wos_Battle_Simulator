import { HOST_HERO_NAMES, type SideConfig } from "../data/dummyData";
import HeroSelect from "./HeroSelect";
import PlayerStatsInputs from "./PlayerStatsInputs";
import TroopInputs from "./TroopInputs";

interface PlayerSectionProps {
  title: string;
  accent: "sky" | "rose";
  joinersToggleLabel: "Rally" | "Garrison";
  config: SideConfig;
  onChange: (config: SideConfig) => void;
}

const HOST_HERO_LABELS = ["Hero 1 (Infantry)", "Hero 2 (Lancer)", "Hero 3 (Marksmen)"] as const;

const accentClasses = {
  sky: "border-sky-500/40 from-sky-950/40",
  rose: "border-rose-500/40 from-rose-950/40",
};

export default function PlayerSection({
  title,
  accent,
  joinersToggleLabel,
  config,
  onChange,
}: PlayerSectionProps) {
  const updateHero = (index: number, hero: SideConfig["heroes"][number]) => {
    const heroes = [...config.heroes] as SideConfig["heroes"];
    heroes[index] = hero;
    onChange({ ...config, heroes });
  };

  const updateJoiner = (index: number, hero: SideConfig["heroes"][number]) => {
    const joiners = [...config.joiners];
    joiners[index] = hero;
    onChange({ ...config, joiners });
  };

  return (
    <section
      className={`rounded-xl border bg-gradient-to-br to-slate-900/60 p-5 shadow-lg ${accentClasses[accent]}`}
    >
      <h2 className="mb-4 text-lg font-bold text-white">{title}</h2>

      <div className="mb-5">
        <PlayerStatsInputs
          stats={config.stats}
          onChange={(stats) => onChange({ ...config, stats })}
        />
      </div>

      <div className="mb-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-200">Main Heroes</h3>
        {config.heroes.map((hero, index) => (
          <HeroSelect
            key={`hero-${index}`}
            label={HOST_HERO_LABELS[index]}
            heroNames={HOST_HERO_NAMES[index]}
            value={hero}
            onChange={(updated) => updateHero(index, updated)}
          />
        ))}
      </div>

      <label className="mb-5 flex cursor-pointer items-center gap-2">
        <input
          type="checkbox"
          checked={config.joinersEnabled}
          onChange={(e) =>
            onChange({ ...config, joinersEnabled: e.target.checked })
          }
          className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-sky-500 focus:ring-sky-500"
        />
        <span className="text-sm font-medium text-slate-200">
          {joinersToggleLabel}
        </span>
      </label>

      {config.joinersEnabled && (
        <div className="mb-5 space-y-3">
          <h3 className="text-sm font-semibold text-slate-200">
            Joiners (up to 4)
          </h3>
          {config.joiners.map((joiner, index) => (
            <HeroSelect
              key={`joiner-${index}`}
              label={`Joiner ${index + 1}`}
              value={joiner}
              showWidget={false}
              onChange={(updated) => updateJoiner(index, updated)}
            />
          ))}
        </div>
      )}

      <TroopInputs
        troops={config.troops}
        onChange={(troops) => onChange({ ...config, troops })}
      />
    </section>
  );
}
