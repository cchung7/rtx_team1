import React, { useRef, useState, useLayoutEffect } from "react";

const TOOLTIP_TEXT = {
  Algorithm:
    "A Gradient Boosting Decision Tree ensemble that builds trees iteratively to reduce prediction error.",
  MSE: "Average squared prediction error (smaller value means lower error).",
  RMSE:
    "Average prediction error in AQI units (smaller value means higher accuracy).",
  "R2 Score":
    "Portion of variance explained by the model. Closer to 1.0 is better.",
};

function MetricBox({ label, value }) {
  const tooltipText = TOOLTIP_TEXT[label] ?? "";
  const wrapperRef = useRef(null);
  const tooltipRef = useRef(null);
  const [pos, setPos] = useState("right");
  const [visible, setVisible] = useState(false);

  useLayoutEffect(() => {
    if (!visible) return;
    const wrap = wrapperRef.current;
    const tip = tooltipRef.current;
    if (!wrap || !tip) return;

    const tipRect = tip.getBoundingClientRect();
    const wrapRect = wrap.getBoundingClientRect();
    const viewportWidth = window.innerWidth;

    const rightEdge = wrapRect.right + tipRect.width + 16;
    if (rightEdge <= viewportWidth) {
      setPos("right");
      return;
    }

    const leftEdge = wrapRect.left - tipRect.width - 16;
    if (leftEdge >= 0) {
      setPos("left");
      return;
    }

    setPos("top");
  }, [visible]);

  return (
    <div
      ref={wrapperRef}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      className="relative bg-white border border-slate-200 rounded-lg p-3 text-center shadow-sm"
    >
      <div className="text-xs uppercase tracking-wide text-slate-500 text-center">
        {label}
      </div>
      <div className="text-lg font-semibold text-slate-900 mt-1 text-center">
        {value ?? "--"}
      </div>

      {tooltipText && (
        <div
          ref={tooltipRef}
          className={[
            "pointer-events-none",
            "absolute",
            "z-50",
            "bg-slate-900/95",
            "text-white",
            "text-xs",
            "px-3",
            "py-2",
            "rounded-md",
            "shadow-lg",
            "w-64",
            "leading-snug",
            "transition-opacity",
            visible ? "opacity-100" : "opacity-0",
          ].join(" ")}
          style={
            pos === "right"
              ? {
                  top: "50%",
                  left: "108%",
                  transform: "translateY(-50%)",
                }
              : pos === "left"
              ? {
                  top: "50%",
                  right: "108%",
                  transform: "translateY(-50%)",
                }
              : {
                  bottom: "108%",
                  left: "50%",
                  transform: "translateX(-50%)",
                }
          }
        >
          {tooltipText}

          {pos === "right" && (
            <div className="absolute top-1/2 -translate-y-1/2 -left-1 w-2 h-2 bg-slate-900/95 rotate-45" />
          )}
          {pos === "left" && (
            <div className="absolute top-1/2 -translate-y-1/2 -right-1 w-2 h-2 bg-slate-900/95 rotate-45" />
          )}
          {pos === "top" && (
            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900/95 rotate-45" />
          )}
        </div>
      )}
    </div>
  );
}

export default function StatsStrip({ algorithm, mse, rmse, r2 }) {
  return (
    <div className="card shadow-md hover:shadow-xl border border-slate-200 transition-shadow mt-6">
      <h2 className="section-title">Model Information</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricBox label="Algorithm" value={algorithm} />
        <MetricBox
          label="MSE"
          value={typeof mse === "number" ? mse.toFixed(3) : "--"}
        />
        <MetricBox
          label="RMSE"
          value={typeof rmse === "number" ? rmse.toFixed(3) : "--"}
        />
        <MetricBox
          label="R2 Score"
          value={typeof r2 === "number" ? r2.toFixed(2) : "--"}
        />
      </div>
    </div>
  );
}
