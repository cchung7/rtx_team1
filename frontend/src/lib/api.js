const API_BASE = "/api";
const join = (b, p) => `${b.replace(/\/+$/,'')}/${String(p).replace(/^\/+/, '')}`;

export async function getCounties() {
  const r = await fetch(join(API_BASE, "counties"));
  const j = await r.json();
  if (!r.ok || !j.success) throw new Error(j.error || "Failed to load counties");
  return j.counties;
}

export async function getModelMetrics(model = "balanced") {
  const r = await fetch(join(API_BASE, `model/metrics?model=${encodeURIComponent(model)}`));
  const j = await r.json();
  if (!r.ok || !j.success) return null;
  return j.metrics;
}

export async function getHistorical({ county, state, days = 30 }) {
  const r = await fetch(
    join(API_BASE, `aqi/historical?county=${encodeURIComponent(county)}&state=${encodeURIComponent(state)}&days=${days}`)
  );
  const j = await r.json();
  if (!r.ok || !j.success) throw new Error(j.error || "Failed to load historical data");
  return j.data;
}

export async function postPredict({ county, state, model = "balanced", days = 1 }) {
  const r = await fetch(join(API_BASE, "aqi/predict"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ county, state, model, days }),
  });
  const j = await r.json();
  if (!r.ok || !j.success) throw new Error(j.error || "Failed to generate prediction");
  return j;
}
