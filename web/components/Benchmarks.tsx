"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";
import { benchmarks } from "@/lib/data";

export default function Benchmarks() {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      gsap.registerPlugin(ScrollTrigger);

      gsap.from(".bm-card", {
        y: 60,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        stagger: 0.15,
        scrollTrigger: { trigger: root.current, start: "top 70%" },
      });

      // count every number up from 0
      gsap.utils.toArray<HTMLElement>(".bm-num").forEach((el) => {
        const target = Number(el.dataset.value);
        const obj = { v: 0 };
        gsap.to(obj, {
          v: target,
          duration: 1.6,
          ease: "power2.out",
          scrollTrigger: { trigger: el, start: "top 85%" },
          onUpdate: () => {
            el.textContent = obj.v.toFixed(2);
          },
        });
      });
    },
    { scope: root },
  );

  const slowest = Math.max(...benchmarks.map((b) => b.ms));
  const fastest = Math.min(...benchmarks.map((b) => b.ms));
  const factor = Math.round(slowest / fastest);

  return (
    <section ref={root} className="relative mx-auto max-w-6xl px-6 py-[16vh]">
      <div className="mb-14 text-center">
        <p className="mb-3 font-mono text-xs uppercase tracking-[0.4em] text-[var(--color-cyan)]/80">
          benchmarks · measured, not estimated
        </p>
        <h2 className="mx-auto max-w-2xl text-3xl font-medium tracking-tight md:text-5xl">
          <span className="text-gradient">{factor}× faster</span> than the alternatives.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-sm text-white/45">
          timeit · 10 runs · median, generating the API docs for <span className="font-mono">src/</span>.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        {benchmarks.map((b) => (
          <div
            key={b.tool}
            className={`bm-card relative overflow-hidden rounded-2xl p-7 ${
              b.hero ? "glass ring-glow" : "border border-white/10 bg-white/[0.02]"
            }`}
          >
            {b.hero && (
              <span className="absolute right-4 top-4 rounded-full bg-[var(--color-cyan)]/15 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-[var(--color-cyan)]">
                this
              </span>
            )}
            <p className="font-mono text-sm text-white/70">{b.tool}</p>
            <div className="mt-6 flex items-baseline gap-1.5">
              <span
                className={`bm-num text-6xl font-bold tabular-nums tracking-tight md:text-7xl ${
                  b.hero ? "text-gradient text-glow" : "text-white/85"
                }`}
                data-value={b.ms}
              >
                0.00
              </span>
              <span className="font-mono text-sm text-white/40">ms</span>
            </div>
            <div className="mt-6 flex items-center justify-between border-t border-white/10 pt-4 font-mono text-[11px] text-white/40">
              <span>{b.lines} lines</span>
              <span>{b.output}</span>
            </div>
          </div>
        ))}
      </div>

      <p className="mx-auto mt-10 max-w-2xl text-center text-xs leading-relaxed text-white/35">
        Read honestly: it&apos;s apples-to-oranges. pdoc and Sphinx build a whole HTML site with
        search and cross-links; living-docs builds a single Markdown file. Faster is true — but pick
        the tool that matches the output you actually want.
      </p>
    </section>
  );
}
