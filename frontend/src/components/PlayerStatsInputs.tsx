import type { PlayerStats } from "../data/dummyData";

interface PlayerStatsInputsProps {
  stats: PlayerStats;
  onChange: (stats: PlayerStats) => void;
}

const STAT_GROUPS = [
  {
    label: "Infantry",
    fields: [
      { key: "Attack", stat: "inf_attack" },
      { key: "Defense", stat: "inf_defense" },
      { key: "Health", stat: "inf_health" },
      { key: "Lethality", stat: "inf_lethality" },
    ],
  },
  {
    label: "Lancer",
    fields: [
      { key: "Attack", stat: "lancer_attack" },
      { key: "Defense", stat: "lancer_defense" },
      { key: "Health", stat: "lancer_health" },
      { key: "Lethality", stat: "lancer_lethality" },
    ],
  },
  {
    label: "Marksmen",
    fields: [
      { key: "Attack", stat: "marks_attack" },
      { key: "Defense", stat: "marks_defense" },
      { key: "Health", stat: "marks_health" },
      { key: "Lethality", stat: "marks_lethality" },
    ],
  },
] as const;

export default function PlayerStatsInputs({
  stats,
  onChange,
}: PlayerStatsInputsProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-200">Player Stats (%)</h3>
      {STAT_GROUPS.map((group) => (
        <div
          key={group.label}
          className="grid gap-2 rounded-lg border border-slate-700/60 bg-slate-900/40 p-3 sm:grid-cols-5"
        >
          <p className="self-center text-sm font-medium text-slate-300">
            {group.label}
          </p>
          {group.fields.map(({ key, stat }) => (
            <label
              key={stat}
              className="flex flex-col gap-1 text-xs text-slate-400"
            >
              {key}
              <input
                type="number"
                step="0.1"
                className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm"
                value={stats[stat]}
                onChange={(e) =>
                  onChange({ ...stats, [stat]: Number(e.target.value) })
                }
              />
            </label>
          ))}
        </div>
      ))}
    </div>
  );
}
