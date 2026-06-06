import type { SimulationResults } from "../data/dummyData";

interface ResultsPanelProps {
  results: SimulationResults | null;
  isRunning: boolean;
}

function WinBar({ label, rate, color }: { label: string; rate: number; color: string }) {
  const percent = (rate * 100).toFixed(1);
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="font-semibold text-white">{percent}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

export default function ResultsPanel({ results, isRunning }: ResultsPanelProps) {
  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900/70 p-5 shadow-lg">
      <h2 className="mb-4 text-lg font-bold text-white">Results</h2>

      {isRunning && (
        <p className="animate-pulse text-sm text-slate-400">
          Running simulations...
        </p>
      )}

      {!isRunning && !results && (
        <p className="text-sm text-slate-500">
          Configure both sides and click Simulate to see win rates.
        </p>
      )}

      {results && !isRunning && (
        <div className="space-y-5">
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Based on {results.numSims.toLocaleString()} simulations (dummy data)
          </p>

          <WinBar
            label="Attacker win rate"
            rate={results.attackerWinRate}
            color="bg-sky-500"
          />
          <WinBar
            label="Defender win rate"
            rate={results.defenderWinRate}
            color="bg-rose-500"
          />

          <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Average rounds
            </p>
            <p className="mt-1 text-3xl font-bold text-amber-300">
              {results.averageRounds}
            </p>
          </div>

          <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Average Attacker survivors
            </p>
            <p className="mt-1 text-3xl font-bold text-amber-300">
              {results.averageAttackerSurvivors.toFixed(0)}
            </p>
          </div>

          <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Average Defender survivors
            </p>
            <p className="mt-1 text-3xl font-bold text-amber-300">
              {results.averageDefenderSurvivors.toFixed(0)}
            </p>
          </div>

        </div>
      )}
    </section>
  );
}
