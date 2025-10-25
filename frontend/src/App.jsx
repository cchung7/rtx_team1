import { useEffect, useMemo, useState } from "react";
import Select from "./components/Select";
import Spinner from "./components/Spinner";
import ErrorAlert from "./components/ErrorAlert";
import AqiLegend from "./components/AqiLegend";
import PredictionCard from "./components/PredictionCard";
import ProbabilitiesList from "./components/ProbabilitiesList";
import AqiChart from "./components/AqiChart";
import MultiDayChart from "./components/MultiDayChart";
import StatsStrip from "./components/StatsStrip";
import { getCounties, getHistorical, postPredict, getModelMetrics } from "./lib/api";
import clapLogo from "./assets/clap_logo.png";

export default function App() {
  const [counties, setCounties] = useState([]);
  const [selected, setSelected] = useState("");
  const [model, setModel] = useState("balanced");
  const [days, setDays] = useState(1);

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const [history, setHistory] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const countyOptions = useMemo(() => {
    return [{ label: "-- Select a County --", value: "" }].concat(
      counties.map(c => ({
        label: c.display_name || `${c.county} County, ${c.state}`,
        value: JSON.stringify({ county: c.county, state: c.state }),
      }))
    );
  }, [counties]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const cs = await getCounties();
        if (!mounted) return;
        setCounties(cs);
      } catch (e) {
        setErr(e.message);
      }
    })();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    (async () => {
      const m = await getModelMetrics(model);
      setMetrics(m);
    })();
  }, [model]);

  async function doLoad(val) {
    if (!val) return setErr("Please select a county first");
    try {
      setErr(""); setLoading(true);
      const { county, state } = JSON.parse(val);
      const hist = await getHistorical({ county, state, days: 30 });
      setHistory(hist);
      setPrediction(null);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function doRefresh(val = selected, forecastDays = days, modelKey = model) {
    if (!val) return setErr("Please select a county first");
    try {
      setErr(""); setLoading(true);
      const { county, state } = JSON.parse(val);
      const [hist, pred] = await Promise.all([
        getHistorical({ county, state, days: 30 }),
        postPredict({ county, state, model: modelKey, days: forecastDays }),
      ]);
      setHistory(hist);
      setPrediction(pred);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  const singlePrediction = useMemo(() => {
    if (!prediction) return null;
    if (days === 1) return prediction.prediction || prediction;
    return prediction.predictions?.[0];
  }, [prediction, days]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white py-10">
        <div className="container-xxl flex flex-col items-center text-center">
          <h1 className="text-3xl md:text-5xl font-extrabold flex items-center gap-3">
            <img
              src={clapLogo}
              alt="CLAP Logo"
              className="w-20 h-20 md:w-24 md:h-24 rounded-md shadow-md"
            />
            County Level Air Quality Prediction
          </h1>
          <p className="opacity-90 text-lg md:text-xl mt-2">Next-Day AQI Forecasting System</p>
        </div>
      </header>

      {/* Main */}
      <main className="container-xxl -mt-6 mb-16 space-y-6">
        {/* Select Location & Model */}
        <section className="card shadow-md hover:shadow-xl border border-slate-200 transition-shadow">
          <h2 className="section-title">Select Location & Model</h2>
          <div className="grid md:grid-cols-4 gap-4">
            <Select id="model" label="Model" value={model} onChange={v => { setModel(v); doRefresh(selected, days, v); }}>
              <option value="balanced">LightGBM</option>
            </Select>

            <Select id="county" label="County" value={selected} onChange={v => { setSelected(v); doRefresh(v, days, model); }}>
              {countyOptions.map(o => <option key={o.value || "blank"} value={o.value}>{o.label}</option>)}
            </Select>

            <Select id="days" label="Forecast Period" value={String(days)} onChange={v => { const d = Number(v); setDays(d); doRefresh(selected, d, model); }}>
              <option value="1">Next Day</option>
            </Select>

            <div className="flex items-end gap-3">
              {/* add 3D + gloss */}
              <button className="btn btn-3d btn-gloss btn-primary w-full btn-lg" onClick={() => doRefresh()}>
                🔮 Generate Forecast
              </button>
              <button className="btn btn-3d btn-gloss btn-secondary w-full btn-lg" onClick={() => doLoad(selected)}>
                📊 Load Data
              </button>
            </div>
          </div>
          <div className="mt-4">{loading ? <Spinner /> : <ErrorAlert message={err} />}</div>
        </section>

        {/* Prediction */}
        {prediction && (
          <section className="grid md:grid-cols-3 gap-6">
            <div className="card shadow-md hover:shadow-xl border border-slate-200 transition-shadow md:col-span-1">
              <h2 className="section-title">{days === 1 ? "Next-Day AQI Prediction" : `${days}-Day Forecast`}</h2>
              {days === 1 ? (
                <PredictionCard
                  aqi={Math.round(singlePrediction?.predicted_aqi ?? NaN)}
                  category={singlePrediction?.predicted_category}
                  date={singlePrediction?.forecast_date}
                />
              ) : (
                <div className="text-slate-600">See the chart & summary on the right →</div>
              )}
            </div>

            <div className="card shadow-md hover:shadow-xl border border-slate-200 transition-shadow md:col-span-2">
              <h2 className="section-title">{days === 1 ? "Category Probabilities" : `${days}-Day AQI Forecast`}</h2>
              {days === 1 ? (
                <ProbabilitiesList probabilities={singlePrediction?.probabilities} />
              ) : (
                <MultiDayChart predictions={prediction.predictions || []} />
              )}
            </div>
          </section>
        )}

        {/* Historical */}
        <section className="card shadow-md hover:shadow-xl border border-slate-200 transition-shadow">
          <h2 className="section-title">30-Day Historical AQI Trend</h2>
          <AqiChart history={history} overlayPrediction={singlePrediction} />
          <AqiLegend />
        </section>

        {/* Model Information */}
          <StatsStrip
            algorithm="LightGBM Regressor(Gradient Boosting Decision Tree)"
            mse={metrics?.mse}
            rmse={metrics?.rmse}
            r2={metrics?.r2}
          />
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-200 py-8 mt-auto">
      </footer>
    </div>
  );
}
