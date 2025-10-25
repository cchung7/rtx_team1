export default function StatsStrip({ algorithm="LightGBM Regressor (Gradient Boosting Decision Tree)", mse, rmse, r2 }) {
  return (
    <div className="card shadow-md hover:shadow-xl border border-slate-200 transition-shadow">
      <h2 className="section-title">Model Information</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Info label="Algorithm" value={algorithm} />
        <Info label="MSE" value={mse != null ? mse.toFixed(2) : "--"} />
        <Info label="RMSE" value={rmse != null ? `~${Math.round(rmse)} AQI units` : "--"} />
        <Info label="R² Score" value={r2 != null ? r2.toFixed(2) : "--"} />
      </div>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="flex flex-col">
      <span className="text-xs text-slate-500 font-semibold">{label}</span>
      <span className="text-lg font-bold text-slate-800">{value}</span>
    </div>
  );
}
