import { ALL_HERO_NAMES, type HeroSelection } from "../data/dummyData";

interface HeroSelectProps {
  label: string;
  value: HeroSelection;
  onChange: (hero: HeroSelection) => void;
  showWidget?: boolean;
  heroNames?: readonly string[];
}

export default function HeroSelect({
  label,
  value,
  onChange,
  showWidget = true,
  heroNames = ALL_HERO_NAMES,
}: HeroSelectProps) {  return (
    <div className="space-y-2 rounded-lg border border-slate-700/80 bg-slate-900/50 p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>
      <div className="grid gap-2 sm:grid-cols-3">
        <label className="flex flex-col gap-1 text-xs text-slate-400">
          Hero
          <select
            className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm text-slate-100"
            value={value.name}
            onChange={(e) => onChange({ ...value, name: e.target.value })}
          >
            {heroNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-slate-400">
          Stars
          <select
            className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm text-slate-100"
            value={value.stars}
            onChange={(e) =>
              onChange({ ...value, stars: Number(e.target.value) })
            }
          >
            {[1, 2, 3, 4, 5].map((stars) => (
              <option key={stars} value={stars}>
                {stars}
              </option>
            ))}
          </select>
        </label>
        {showWidget && (
          <label className="flex flex-col gap-1 text-xs text-slate-400">
            Widget
            <select
              className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm text-slate-100"
              value={value.widgetLevel}
              onChange={(e) =>
                onChange({ ...value, widgetLevel: Number(e.target.value) })
              }
            >
              {Array.from({ length: 11 }, (_, i) => (
                <option key={i} value={i}>
                  {i}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
    </div>
  );
}
