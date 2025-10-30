import React, { useRef, useState, useLayoutEffect } from "react";
import { AQI_CATEGORIES } from "../utils/aqi";

const TOOLTIP_TEXT = {
  Good: "Air quality is satisfactory, and air pollution poses little or no risk.",
  Moderate:
    "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
  "Unhealthy for Sensitive Groups":
    "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
  Unhealthy:
    "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
  "Very Unhealthy":
    "Health alert: The risk of health effects is increased for everyone.",
  Hazardous:
    "Health warning of emergency conditions: everyone is more likely to be affected.",
};

function LegendItem({ name, cfg }) {
  const tooltipText = TOOLTIP_TEXT[name] ?? name;
  const wrapperRef = useRef(null);
  const tooltipRef = useRef(null);
  const [pos, setPos] = useState("right"); // ✅ removed TypeScript type annotation
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
      className="relative flex flex-col items-center text-center p-2 rounded-lg hover:bg-slate-50 transition w-40"
    >
      {/* color box */}
      <span
        className="w-6 h-6 rounded-md border mb-1 shadow-sm"
        style={{
          borderColor: "black",
          backgroundColor: cfg.color,
          boxShadow: `0 0 6px ${cfg.color}66`,
        }}
      />

      {/* label */}
      <span className="text-sm font-medium text-slate-800 leading-tight">
        {name}
      </span>
      <span className="text-xs text-slate-600 leading-tight">
        ({cfg.range[0]}–{cfg.range[1]})
      </span>

      {/* tooltip */}
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
          "w-60",
          "leading-snug",
          "transition-opacity",
          visible ? "opacity-100" : "opacity-0",
        ].join(" ")}
        style={
          pos === "right"
            ? {
                top: "50%",
                left: "110%",
                transform: "translateY(-50%)",
              }
            : pos === "left"
            ? {
                top: "50%",
                right: "110%",
                transform: "translateY(-50%)",
              }
            : {
                bottom: "110%",
                left: "50%",
                transform: "translateX(-50%)",
              }
        }
      >
        {tooltipText}

        {/* arrow indicators */}
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
    </div>
  );
}

export default function AqiLegend() {
  return (
    <div className="mt-6 border-t border-slate-200 pt-6">
      <h3 className="text-lg font-semibold text-slate-700 mb-3 text-center">
        EPA AQI Categories
      </h3>

      <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4 justify-items-center">
        {Object.entries(AQI_CATEGORIES).map(([name, cfg]) => (
          <LegendItem key={name} name={name} cfg={cfg} />
        ))}
      </div>
    </div>
  );
}
