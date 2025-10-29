import { AQI_CATEGORIES } from "../utils/aqi";

export default function AqiLegend() {
  return (
    <div className="mt-6 border-t border-slate-200 pt-6">
      <h3 className="text-lg font-semibold text-slate-700 mb-3">EPA AQI Categories</h3>
      <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-3">
        {Object.entries(AQI_CATEGORIES).map(([name, cfg]) => (
          <div key={name} className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50">
            <span className="w-6 h-6 rounded border" style={{ backgroundColor: cfg.color }} />
            <span className="text-sm font-medium text-slate-800">
              {name} ({cfg.range[0]}–{cfg.range[1]})
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
