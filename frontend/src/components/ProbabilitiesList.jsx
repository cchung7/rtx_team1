import { getCategoryClass, AQI_CATEGORIES } from "../utils/aqi";

const ORDER = [
  "Good",
  "Moderate",
  "Unhealthy for Sensitive Groups",
  "Unhealthy",
  "Hazardous",
  "Very Unhealthy",
];

export default function ProbabilitiesList({ probabilities }) {
  if (!probabilities) return null;

  const entries = ORDER.map(cat => [cat, probabilities?.[cat] ?? 0]);

  return (
    <div className="p-6 rounded-xl bg-slate-50">
      <h3 className="text-lg font-semibold text-slate-700 mb-4">Category Probabilities</h3>
      <div className="space-y-3">
        {entries.map(([cat, p]) => {
          const pctNum = Math.max(0, Math.min(100, (p * 100)));
          const pct = pctNum.toFixed(1);
          return (
            <div key={cat} className="flex items-center gap-3">
              <div className="w-48 text-sm font-semibold text-slate-800">{cat}</div>

              {/* Bar container */}
              <div className="relative flex-1 h-8 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getCategoryClass(cat)} transition-[width] duration-300 ease-out`}
                  style={{ width: `${pctNum}%` }}
                  role="progressbar"
                  aria-valuenow={pct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
                <div className="absolute inset-0 grid place-items-center text-sm font-semibold text-slate-800">
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
