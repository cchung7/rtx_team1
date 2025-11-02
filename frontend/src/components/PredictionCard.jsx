import { getCategoryClass } from "../utils/aqi";

export default function PredictionCard({ aqi, category, date, county, state }) {
  const formattedDate = date
    ? new Date(date).toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "--";

  return (
    <div className="flex items-center justify-center h-full relative -translate-y-10">
      <div className="text-center p-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 text-white">
        {/* Title */}
        <div className="uppercase tracking-wider text-sm/5 opacity-90 font-bold">
          Predicted AQI
        </div>

        {/* Location */}
        {county && state && (
          <div className="text-xs opacity-80 font-semibold mt-1 mb-2">
            {county}, {state}
          </div>
        )}

        {/* AQI Value */}
        <div className="text-6xl font-extrabold my-2">{aqi ?? "--"}</div>

        <div
          className={`badge ${getCategoryClass(
            category
          )} !text-black font-extrabold`}
        >
          {category ?? "--"}
        </div>

        {/* Forecast Date */}
        <div className="text-xs opacity-90 mt-2 font-extrabold leading-tight">
          Forecast for:
          <br />
          {formattedDate}
        </div>
      </div>
    </div>
  );
}
