import { Line } from "react-chartjs-2";
import { Chart as ChartJS, LineElement, LinearScale, CategoryScale, PointElement, Tooltip, Legend, Filler } from "chart.js";
import { getCategoryColor, getCategoryForAQI, getCategoryClass } from "../utils/aqi";

ChartJS.register(LineElement, LinearScale, CategoryScale, PointElement, Tooltip, Legend, Filler);

export default function MultiDayChart({ predictions = [] }) {
  if (!predictions.length) return null;

  const labels = predictions.map((_, i) => {
    const d = new Date(); d.setDate(d.getDate() + i + 1);
    return d.toLocaleDateString();
  });
  const values = predictions.map(p => p.predicted_aqi);

  const data = {
    labels,
    datasets: [{
      label: "Predicted AQI",
      data: values,
      borderColor: "#4F46E5",
      backgroundColor: "rgba(79,70,229,0.12)",
      pointBackgroundColor: values.map(v => getCategoryColor(getCategoryForAQI(v))),
      tension: 0.35,
      fill: true,
    }]
  };
  const options = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: "AQI" } },
      x: { title: { display: true, text: "Date" } }
    }
  };

  const avg = Math.round(values.reduce((a,b)=>a+b,0)/values.length);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const counts = predictions.reduce((acc,p)=>((acc[p.predicted_category]=(acc[p.predicted_category]||0)+1),acc),{});
  const common = Object.keys(counts).sort((a,b)=>counts[b]-counts[a])[0];

  return (
    <>
      <div className="h-[340px]">
        <Line data={data} options={options} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-5">
        <Summary label="Average AQI" value={avg} />
        <Summary label="Range" value={`${Math.round(min)} - ${Math.round(max)}`} />
        <Summary label="Most Common" value={<span className={`badge ${getCategoryClass(common)}`}>{common}</span>} />
      </div>
    </>
  );
}

function Summary({ label, value }) {
  return (
    <div className="flex items-center justify-between bg-white border border-slate-200 rounded-lg p-3">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="text-base font-semibold">{value}</div>
    </div>
  );
}
