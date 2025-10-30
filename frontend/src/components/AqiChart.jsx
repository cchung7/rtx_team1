import { Line } from "react-chartjs-2";
import { Chart as ChartJS, LineElement, LinearScale, CategoryScale, PointElement, Tooltip, Legend, Filler } from "chart.js";
import { getCategoryForAQI, getCategoryColor } from "../utils/aqi";

ChartJS.register(LineElement, LinearScale, CategoryScale, PointElement, Tooltip, Legend, Filler);

const dangerLinePlugin = {
  id: "dangerLine",
  beforeDatasetsDraw: (chart) => {
    const data = chart.data.datasets[0]?.data;
    if (!data || data.length < 2) return;

    const { ctx, chartArea, scales } = chart;
    if (!chartArea || !scales?.y) return;

    const { left, right, top, bottom } = chartArea;
    const yScale = scales.y;

    const thresholds = [
      { value: 0, color: "#22c55e" },   // Green - Good
      { value: 50, color: "#eab308" },  // Yellow - Moderate
      { value: 100, color: "#f97316" }, // Orange - Unhealthy (Sensitive)
      { value: 150, color: "#ef4444" }, // Red - Unhealthy
      { value: 200, color: "#9333ea" }, // Purple - Very Unhealthy
      { value: 300, color: "#7f1d1d" }, // Maroon - Hazardous
    ];

    ctx.save();

    for (let i = 0; i < thresholds.length - 1; i++) {
      const current = thresholds[i];
      const next = thresholds[i + 1];
      const yTop = yScale.getPixelForValue(next.value);
      const yBottom = yScale.getPixelForValue(current.value);

      if (yTop < top || yBottom > bottom) continue;

      ctx.fillStyle = current.color + "15";
      ctx.fillRect(left, yTop, right - left, yBottom - yTop);
    }

    thresholds.slice(1).forEach((th) => {
      const y = yScale.getPixelForValue(th.value);
      if (y < top || y > bottom) return;

      ctx.strokeStyle = th.color + "66";
      ctx.lineWidth = 1.3;
      ctx.setLineDash([6, 4]);
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(right, y);
      ctx.stroke();
    });

    ctx.restore();
  },
};

const lineShadowPlugin = {
  id: "lineShadow",
  beforeDatasetsDraw: (chart, args, opts) => {
    const { ctx } = chart;
    ctx.save();
    ctx.shadowColor = "rgba(37, 99, 235, 0.35)";
    ctx.shadowBlur = 12;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 6;
  },
  afterDatasetsDraw: (chart) => {
    chart.ctx.restore();
  },
};

const gradientFillPlugin = {
  id: "gradientFill",
  beforeDatasetsDraw(chart) {
    const { ctx, chartArea } = chart;
    if (!chartArea) return;
    const { top, bottom } = chartArea;

    const dataset = chart.data.datasets[0];
    if (!dataset) return;

    const gradient = ctx.createLinearGradient(0, top, 0, bottom);
    gradient.addColorStop(0, "rgba(37, 99, 235, 0.35)");
    gradient.addColorStop(1, "rgba(37, 99, 235, 0)");
    dataset.backgroundColor = gradient;
  },
};

export default function AqiChart({ history = [], overlayPrediction }) {
  const labels = history.map((d) => d.date);
  const values = history.map((d) => d.aqi);

  if (overlayPrediction?.predicted_aqi) {
    const nextDate = new Date();
    nextDate.setDate(nextDate.getDate() + 1);
    labels.push(nextDate.toISOString().split("T")[0]);
    values.push(Math.round(overlayPrediction.predicted_aqi));
  }

  const pointColors = values.map((v) =>
    getCategoryColor(getCategoryForAQI(v))
  );

  const data = {
    labels,
    datasets: [
      {
        label: "AQI (Higher AQI Means Worse Air Quality)",
        data: values,
        borderColor: "#2563eb",
        borderWidth: 3,
        backgroundColor: "rgba(37, 99, 235, 0.15)", // gradientFillPlugin overrides this
        pointBackgroundColor: pointColors,
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        pointRadius: 5,
        tension: 0.35,
        fill: true,
      },
    ],
  };

  const maxVal = values.length ? Math.max(...values) : 0;
  const maxY = maxVal > 200 ? Math.max(300, maxVal * 1.2) : 200;

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: maxY,
        ticks: { stepSize: 50 },
        title: { display: true, text: "AQI Values" },
      },
      x: { title: { display: true, text: "Date Recorded" } },
    },
  };

  // Stats
  const histOnly = overlayPrediction ? values.slice(0, -1) : values;
  const avg =
    histOnly.length > 0
      ? Math.round(histOnly.reduce((a, b) => a + b, 0) / histOnly.length)
      : NaN;
  const min = histOnly.length ? Math.min(...histOnly) : NaN;
  const max = histOnly.length ? Math.max(...histOnly) : NaN;
  const latest = histOnly.length ? histOnly[histOnly.length - 1] : NaN;

  return (
    <>
      <div className="h-[380px]">
        <Line
          data={data}
          options={options}
          plugins={[dangerLinePlugin, lineShadowPlugin, gradientFillPlugin]}
        />
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
