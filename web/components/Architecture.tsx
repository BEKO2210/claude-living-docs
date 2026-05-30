"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";
import { moduleEdges, modules } from "@/lib/data";

const pos = Object.fromEntries(modules.map((m) => [m.name, m]));

export default function Architecture() {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      gsap.registerPlugin(ScrollTrigger);

      gsap.from(".arch-heading", {
        y: 40,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        scrollTrigger: { trigger: root.current, start: "top 75%" },
      });

      // edges draw themselves
      gsap.fromTo(
        ".edge",
        { strokeDashoffset: 1, opacity: 0 },
        {
          strokeDashoffset: 0,
          opacity: 1,
          duration: 1.4,
          ease: "power2.inOut",
          stagger: 0.06,
          scrollTrigger: { trigger: root.current, start: "top 55%" },
        },
      );

      // nodes bloom in
      gsap.from(".arch-node", {
        scale: 0.4,
        opacity: 0,
        duration: 0.9,
        ease: "back.out(2)",
        stagger: 0.08,
        scrollTrigger: { trigger: root.current, start: "top 55%" },
      });

      // gentle perpetual float
      gsap.to(".arch-node", {
        y: "+=8",
        duration: 3,
        ease: "sine.inOut",
        repeat: -1,
        yoyo: true,
        stagger: { each: 0.3, from: "random" },
      });

      // parallax on the whole field
      gsap.to(".arch-field", {
        yPercent: -8,
        scrollTrigger: { trigger: root.current, start: "top bottom", end: "bottom top", scrub: true },
      });
    },
    { scope: root },
  );

  return (
    <section ref={root} className="relative mx-auto max-w-6xl px-6 py-[16vh]">
      <div className="arch-heading mb-4 text-center">
        <p className="mb-3 font-mono text-xs uppercase tracking-[0.4em] text-[var(--color-violet)]">
          the architecture
        </p>
        <h2 className="mx-auto max-w-2xl text-3xl font-medium tracking-tight md:text-5xl">
          One engine. <span className="text-gradient">Extraction never touches rendering.</span>
        </h2>
      </div>

      <div className="arch-field relative mx-auto mt-10 aspect-[4/3] w-full max-w-4xl md:aspect-[16/9]">
        <svg
          className="absolute inset-0 h-full w-full"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >
          {moduleEdges.map(([a, b], i) => (
            <line
              key={i}
              className="edge"
              x1={pos[a].x * 100}
              y1={pos[a].y * 100}
              x2={pos[b].x * 100}
              y2={pos[b].y * 100}
              stroke="url(#edgeGrad)"
              strokeWidth={1}
              vectorEffect="non-scaling-stroke"
              pathLength={1}
              strokeDasharray={1}
            />
          ))}
          <defs>
            <linearGradient id="edgeGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#a06bff" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#38f0d8" stopOpacity="0.7" />
            </linearGradient>
          </defs>
        </svg>

        {modules.map((m) => (
          <div
            key={m.name}
            className="arch-node group absolute -translate-x-1/2 -translate-y-1/2"
            style={{ left: `${m.x * 100}%`, top: `${m.y * 100}%` }}
          >
            <div className="glass ring-glow flex items-center gap-2 rounded-full px-3.5 py-2 transition-transform duration-300 group-hover:scale-110">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-cyan)] shadow-[0_0_10px_var(--color-cyan)]" />
              <span className="font-mono text-xs text-white/90">{m.name}</span>
            </div>
            <span className="pointer-events-none absolute left-1/2 top-full mt-1.5 w-40 -translate-x-1/2 text-center text-[10px] leading-tight text-white/35 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
              {m.role}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
