import { TROOP_TIERS, type TroopSlot } from "../data/dummyData";

interface TroopInputsProps {
  troops: {
    infantry: TroopSlot;
    lancer: TroopSlot;
    marksmen: TroopSlot;
  };

  maxExaltedLevel: number;

  onChange: (troops: TroopInputsProps["troops"]) => void;
}

function TroopRow({
  label,
  troop,
  maxExaltedLevel,
  onTroopChange,
}: {
  label: string;
  troop: TroopSlot;
  maxExaltedLevel: number;
  onTroopChange: (troop: TroopSlot) => void;
}) {
  return (
    <div className="grid gap-2 rounded-lg border border-slate-700/60 bg-slate-900/40 p-3 sm:grid-cols-5">
      <p className="self-center text-sm font-medium text-slate-300">
        {label}
      </p>

      <label className="flex flex-col gap-1 text-xs text-slate-400">
        Tier

        <select
          className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm"
          value={troop.level}
          onChange={(e) => {
            const level = e.target.value as TroopSlot["level"];

            onTroopChange({
              ...troop,
              level,

              // Current troops.json only defines T12 at FC10.
              fc: level === "T12" ? 10 : troop.fc,

              // Exalted is a T12-only value.
              exaltedLevel:
                level === "T12"
                  ? Math.min(troop.exaltedLevel, maxExaltedLevel)
                  : 0,
            });
          }}
        >
          {TROOP_TIERS.map((tier) => (
            <option key={tier} value={tier}>
              {tier}
            </option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1 text-xs text-slate-400">
        FC

        <input
          type="number"
          min={0}
          max={10}
          disabled={troop.level === "T12"}
          className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-60"
          value={troop.level === "T12" ? 10 : troop.fc}
          onChange={(e) =>
            onTroopChange({
              ...troop,
              fc: Number(e.target.value),
            })
          }
        />
      </label>

      <label className="flex flex-col gap-1 text-xs text-slate-400">
        Quantity

        <input
          type="number"
          min={0}
          className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm"
          value={troop.quantity}
          onChange={(e) =>
            onTroopChange({
              ...troop,
              quantity: Number(e.target.value),
            })
          }
        />
      </label>

      <label className="flex flex-col gap-1 text-xs text-slate-400">
        Exalted Lv

        <input
          type="number"
          min={0}
          max={maxExaltedLevel}
          disabled={troop.level !== "T12"}
          className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-40"
          value={
            troop.level === "T12"
              ? Math.min(troop.exaltedLevel, maxExaltedLevel)
              : 0
          }
          onChange={(e) =>
            onTroopChange({
              ...troop,
              exaltedLevel: Math.min(
                Math.max(Number(e.target.value), 0),
                maxExaltedLevel,
              ),
            })
          }
        />

        <span className="text-[10px] text-slate-500">
          {troop.level === "T12"
            ? `Max ${maxExaltedLevel}`
            : "T12 only"}
        </span>
      </label>
    </div>
  );
}

export default function TroopInputs({
  troops,
  maxExaltedLevel,
  onChange,
}: TroopInputsProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-200">Troops</h3>

      <TroopRow
        label="Infantry"
        troop={troops.infantry}
        maxExaltedLevel={maxExaltedLevel}
        onTroopChange={(infantry) =>
          onChange({
            ...troops,
            infantry,
          })
        }
      />

      <TroopRow
        label="Lancer"
        troop={troops.lancer}
        maxExaltedLevel={maxExaltedLevel}
        onTroopChange={(lancer) =>
          onChange({
            ...troops,
            lancer,
          })
        }
      />

      <TroopRow
        label="Marksmen"
        troop={troops.marksmen}
        maxExaltedLevel={maxExaltedLevel}
        onTroopChange={(marksmen) =>
          onChange({
            ...troops,
            marksmen,
          })
        }
      />
    </div>
  );
}
