"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";
import { pipeline } from "@/lib/data";

export default function Pipeline() {
  const root = useRef<HTMLDivElement>(null);
  const stage = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      gsap.registerPlugin(ScrollTrigger);
      const steps = pipeline.length;

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: root.current,
          start: "top top",
          end: "+=320%",
          scrub: 0.6,
          pin: stage.current,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });

      // the energy travels along the connector
      tl.fromTo(".pipe-progress", { scaleX: 0 }, { scaleX: 1, ease: "none" }, 0);
      tl.fromTo(".pipe-pulse", { left: "0%" }, { left: "100%", ease: "none" }, 0);

      pipeline.forEach((_, i) => {
        const at = (i + 0.15) / steps;
        tl.to(`.node-${i}`, { "--on": 1, scale: 1.08, duration: 0.001 }, at);
        tl.fromTo(
          `.detail-${i}`,
          { opacity: 0, y: 26, filter: "blur(8px)" },
          { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.15 },
          at,
        );
        if (i > 0) tl.to(`.detail-${i - 1}`, { opacity: 0, y: -26, duration: 0.12 }, at);
      });
    },
    { scope: root },
  );

  return (
    <section ref={root} className="relative h-[420vh]">
      <div ref={stage} className="flex h-[100svh] flex-col items-center justify-center overflow-hidden px-6">
        <p className="mb-3 font-mono text-xs uppercase tracking-[0.4em] text-[var(--color-cyan)]/80">
          the pipeline
        </p>
        <h2 className="mb-16 max-w-2xl text-center text-3xl font-medium tracking-tight md:text-5xl">
          One source of truth, <span className="text-gradient">four pure stages</span>.
        </h2>

        {/* node rail */}
        <div className="relative mb-14 w-full max-w-4xl">
          <div className="absolute left-0 right-0 top-1/2 h-px -translate-y-1/2 bg-white/10" />
          <div className="pipe-progress absolute left-0 right-0 top-1/2 h-px origin-left -translate-y-1/2 bg-gradient-to-r from-[var(--color-violet)] to-[var(--color-cyan)] shadow-[0_0_18px_var(--color-cyan)]" />
          <div className="pipe-pulse absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white shadow-[0_0_22px_8px_rgba(56,240,216,0.7)]" />

          <div className="relative flex items-center justify-between">
            {pipeline.map((step, i) => (
              <div
                key={step.id}
                className={`node-${i} group flex flex-col items-center`}
                style={{ ["--on" as string]: 0 }}
              >
                <div
                  className="relative grid h-16 w-16 place-items-center rounded-2xl border border-white/10 bg-[var(--color-ink)] font-mono text-sm"
                  style={{
                    boxShadow: "0 0 calc(var(--on) * 38px) rgba(56,240,216,calc(var(--on) * 0.6))",
                    borderColor: "rgba(160,107,255,calc(0.1 + var(--on) * 0.7))",
                  }}
                >
                  <span
                    className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[var(--color-violet)]/40 to-[var(--color-cyan)]/30"
                    style={{ opacity: "var(--on)" }}
                  />
                  <span className="relative text-white/80">{String(i + 1).padStart(2, "0")}</span>
                </div>
                <span className="mt-4 text-sm font-medium text-white/90">{step.label}</span>
                <span className="mt-1 font-mono text-[10px] text-white/40">{step.sub}</span>
              </div>
            ))}
          </div>
        </div>

        {/* detail panel (stacked, crossfaded by scroll) */}
        <div className="relative h-24 w-full max-w-xl">
          {pipeline.map((step, i) => (
            <p
              key={step.id}
              className={`detail-${i} absolute inset-0 text-center text-base text-white/70 md:text-lg`}
              style={{ opacity: i === 0 ? 1 : 0 }}
            >
              {step.detail}
            </p>
          ))}
        </div>
      </div>
    </section>
  );
}
