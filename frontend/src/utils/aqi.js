export const AQI_CATEGORIES = {
  Good: { range: [0, 50], color: "#00E400", textColor: "#000000", cls: "bg-aqi-good text-black" },
  Moderate: { range: [51, 100], color: "#FFFF00", textColor: "#000000", cls: "bg-aqi-moderate text-black" },
  "Unhealthy for Sensitive Groups": { range: [101, 150], color: "#FF7E00", textColor: "#000000", cls: "bg-aqi-ufs text-black" },
  Unhealthy: { range: [151, 200], color: "#FF0000", textColor: "#ffffff", cls: "bg-aqi-unhealthy text-white" },
  "Very Unhealthy": { range: [201, 300], color: "#8F3F97", textColor: "#ffffff", cls: "bg-aqi-veryunhealthy text-white" },
  Hazardous: { range: [301, 500], color: "#7E0023", textColor: "#ffffff", cls: "bg-aqi-hazardous text-white" },
};

export function getCategoryForAQI(aqi) {
  for (const [name, cfg] of Object.entries(AQI_CATEGORIES)) {
    const [lo, hi] = cfg.range;
    if (aqi >= lo && aqi <= hi) return name;
  }
  return aqi > 500 ? "Hazardous" : "Unknown";
}

export function getCategoryColor(category) {
  return AQI_CATEGORIES[category]?.color ?? "#6B7280";
}

export function getCategoryClass(category) {
  return AQI_CATEGORIES[category]?.cls ?? "bg-slate-400 text-white";
}
