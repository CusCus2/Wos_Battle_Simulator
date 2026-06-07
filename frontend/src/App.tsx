import { useState } from "react";
import PlayerSection from "./components/PlayerSection";
import ResultsPanel from "./components/ResultsPanel";
import {
  defaultAttacker,
  defaultDefender,
  type SideConfig,
  type SimulationResults,
} from "./data/dummyData";

export default function App() {
  const [attacker, setAttacker] = useState<SideConfig>(defaultAttacker);
  const [defender, setDefender] = useState<SideConfig>(defaultDefender);
  const [numSims, setNumSims] = useState(1000);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const handleSimulate = async () => {
    setIsRunning(true);
    setResults(null);

    const payload = {
      num_sims : numSims,
      attacker: {
        stats: attacker.stats,
        heroes: attacker.heroes,
        troops: attacker.troops,
      },
      defender: {
        stats: defender.stats,
        heroes: defender.heroes,
        troops: defender.troops,
      },

      attacker_joiners: attacker.joiners,
      defender_joiners: defender.joiners,
    };

    console.log("Payload being sent:", payload);

    try{
      const API_URL = import.meta.env.VITE_API_URL;
      const response = await fetch(`${API_URL}/simulate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
          body: JSON.stringify(payload),
        });

      const apiData = await response.json();
      if (!response.ok) {
        console.error("API validation error:", apiData);
        throw new Error(`API error: ${response.status}`);
      }
      

      const formattedResults: SimulationResults = {
        numSims: apiData.num_sims,
        attacker_wins: apiData.attacker_wins,
        defender_wins: apiData.defender_wins,
        attackerWinRate: apiData.attacker_win_rate,
        defenderWinRate: apiData.defender_win_rate,
        averageRounds: apiData.average_rounds,
        averageAttackerSurvivors: apiData.average_attacker_survivors,
        averageDefenderSurvivors: apiData.average_defender_survivors,
      };
      setResults(formattedResults);
    } catch (error) {
      console.error("Simulation failed:", error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="mx-auto min-h-screen max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Whiteout Survival Battle Simulator
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Configure armies, run Monte Carlo simulations, and compare outcomes.
        </p>
      </header>

      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        <PlayerSection
          title="Attacker"
          accent="sky"
          joinersToggleLabel="Rally"
          config={attacker}
          onChange={setAttacker}
        />
        <PlayerSection
          title="Defender"
          accent="rose"
          joinersToggleLabel="Garrison"
          config={defender}
          onChange={setDefender}
        />
      </div>

      <div className="mb-6 flex flex-col items-center gap-4 rounded-xl border border-slate-700 bg-slate-900/50 p-5 sm:flex-row sm:justify-center">
        <label className="flex items-center gap-2 text-sm text-slate-300">
          Simulations
          <input
            type="number"
            min={1}
            max={100000}
            value={numSims}
            onChange={(e) => setNumSims(Number(e.target.value))}
            className="w-28 rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-center text-white"
          />
        </label>
        <button
          type="button"
          onClick={handleSimulate}
          disabled={isRunning}
          className="rounded-lg bg-gradient-to-r from-sky-600 to-cyan-500 px-8 py-2.5 font-semibold text-white shadow-lg transition hover:from-sky-500 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isRunning ? "Simulating..." : "Simulate"}
        </button>
      </div>

      <ResultsPanel results={results} isRunning={isRunning} />
    </div>
  );
}
