import { getCategoryClass } from "../utils/aqi";

export default function ProbabilitiesList({ probabilities }) {
  if (!probabilities) return null;
  const entries = Object.entries(probabilities).sort((a,b) => b[1]-a[1]);
  return (
    <div className="p-6 rounded-xl bg-slate-50">
      <h3 className="text-lg font-semibold text-slate-700 mb-4">Category Probabilities</h3>
      <div className="space-y-3">
        {entries.map(([cat, p]) => {
          const pct = (p * 100).toFixed(1);
          return (
            <div key={cat} className="flex items-center gap-3">
              <div className="w-48 text-sm font-semibold text-slate-800">{cat}</div>
              <div className="flex-1 h-8 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getCategoryClass(cat)} flex items-center justify-end pr-2 text-xs font-bold`}
                  style={{ width: `${pct}%` }}
                  aria-valuenow={pct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  {pct}%
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
