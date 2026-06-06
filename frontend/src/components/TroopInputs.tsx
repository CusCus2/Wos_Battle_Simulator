import { TROOP_TIERS, type TroopSlot } from "../data/dummyData";

interface TroopInputsProps {
  troops: {
    infantry: TroopSlot;
    lancer: TroopSlot;
    marksmen: TroopSlot;
  };
  onChange: (troops: TroopInputsProps["troops"]) => void;
}

function TroopRow({
  label,
  troop,
  onTroopChange,
}: {
  label: string;
  troop: TroopSlot;
  onTroopChange: (troop: TroopSlot) => void;
}) {
  return (
    <div className="grid gap-2 rounded-lg border border-slate-700/60 bg-slate-900/40 p-3 sm:grid-cols-4">
      <p className="self-center text-sm font-medium text-slate-300">{label}</p>
      <label className="flex flex-col gap-1 text-xs text-slate-400">
        Tier
        <select
          className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm"
          value={troop.level}
          onChange={(e) =>
            onTroopChange({
              ...troop,
              level: e.target.value as TroopSlot["level"],
            })
          }
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
          className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1.5 text-sm"
          value={troop.fc}
          onChange={(e) =>
            onTroopChange({ ...troop, fc: Number(e.target.value) })
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
            onTroopChange({ ...troop, quantity: Number(e.target.value) })
          }
        />
      </label>
    </div>
  );
}

export default function TroopInputs({ troops, onChange }: TroopInputsProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-200">Troops</h3>
      <TroopRow
        label="Infantry"
        troop={troops.infantry}
        onTroopChange={(infantry) => onChange({ ...troops, infantry })}
      />
      <TroopRow
        label="Lancer"
        troop={troops.lancer}
        onTroopChange={(lancer) => onChange({ ...troops, lancer })}
      />
      <TroopRow
        label="Marksmen"
        troop={troops.marksmen}
        onTroopChange={(marksmen) => onChange({ ...troops, marksmen })}
      />
    </div>
  );
}
