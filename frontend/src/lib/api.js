const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function getCounties() {
  const r = await fetch(`${API_BASE}/counties`);
  const j = await r.json();
  if (!j.success) throw new Error(j.error || "Failed to load counties");
  return j.counties; // [{county,state,display_name?}, ...]
}

export async function getHistorical({ county, state, days = 30 }) {
  const r = await fetch(`${API_BASE}/aqi/historical?county=${encodeURIComponent(county)}&state=${encodeURIComponent(state)}&days=${days}`);
  const j = await r.json();
  if (!j.success) throw new Error(j.error || "Failed to load historical data");
  return j.data; // [{date, aqi}, ...] assuming your backend returns this shape
}

export async function postPredict({ county, state, model = "balanced", days = 1 }) {
  const r = await fetch(`${API_BASE}/aqi/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ county, state, model, days }),
  });
  const j = await r.json();
  if (!j.success) throw new Error(j.error || "Failed to generate prediction");
  return j;
}

export async function getModelMetrics(model = "balanced") {
  const r = await fetch(`${API_BASE}/model/metrics?model=${model}`);
  const j = await r.json();
  if (!j.success) return null;
  return j.metrics; // {mse, rmse, r2, ...}
}
