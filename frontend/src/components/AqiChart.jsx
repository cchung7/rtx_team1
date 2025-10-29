import { Line } from "react-chartjs-2";
import { Chart as ChartJS, LineElement, LinearScale, CategoryScale, PointElement, Tooltip, Legend, Filler } from "chart.js";
import { getCategoryForAQI, getCategoryColor } from "../utils/aqi";

ChartJS.register(LineElement, LinearScale, CategoryScale, PointElement, Tooltip, Legend, Filler);

export default function AqiChart({ history = [], overlayPrediction }) {
  const labels = history.map(d => d.date);
  const values = history.map(d => d.aqi);

  if (overlayPrediction?.predicted_aqi) {
    const nextDate = new Date();
    nextDate.setDate(nextDate.getDate() + 1);
    labels.push(nextDate.toISOString().split("T")[0]);
    values.push(Math.round(overlayPrediction.predicted_aqi));
  }

  const pointColors = values.map(v => getCategoryColor(getCategoryForAQI(v)));

  const data = {
    labels,
    datasets: [{
      label: "AQI",
      data: values,
      borderColor: "#2563eb",
      backgroundColor: "rgba(37, 99, 235, 0.1)",
      pointBackgroundColor: pointColors,
      pointBorderColor: "#fff",
      pointBorderWidth: 2,
      pointRadius: 5,
      tension: 0.35,
      fill: true,
    }]
  };

  const maxY = Math.max(200, Math.max(...values) * 1.2);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: true } },
    scales: {
      y: { beginAtZero: true, max: maxY, ticks: { stepSize: 50 }, title: { display: true, text: "AQI" } },
      x: { title: { display: true, text: "Date" } }
    }
  };

  // stats
  const histOnly = overlayPrediction ? values.slice(0, -1) : values;
  const avg = Math.round(histOnly.reduce((a,b)=>a+b,0)/Math.max(1, histOnly.length));
  const min = Math.min(...histOnly);
  const max = Math.max(...histOnly);
  const latest = histOnly[histOnly.length-1];

  return (
    <>
      <div className="h-[380px]">
        <Line data={data} options={options} />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5">
        <Stat label="Average AQI" value={isFinite(avg) ? avg : "--"} />
        <Stat label="Minimum AQI" value={isFinite(min) ? min : "--"} />
        <Stat label="Maximum AQI" value={isFinite(max) ? max : "--"} />
        <Stat label="Latest AQI" value={isFinite(latest) ? latest : "--"} />
      </div>
    </>
  );
}

function Stat({ label, value }) {
  return (
    <div className="text-center bg-slate-50 border border-slate-200 rounded-lg p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-xl font-semibold">{value}</div>
    </div>
  );
}
