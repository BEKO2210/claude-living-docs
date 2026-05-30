"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

const TITLE = "LIVING DOCS";

export default function Hero() {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      gsap.registerPlugin(ScrollTrigger);

      const tl = gsap.timeline({ defaults: { ease: "power4.out" } });
      tl.from(".hero-char", {
        yPercent: 120,
        opacity: 0,
        rotateX: -80,
        stagger: 0.045,
        duration: 1.1,
        delay: 0.2,
      })
        .from(".hero-line", { scaleX: 0, duration: 1.2, ease: "power3.inOut" }, "-=0.6")
        .from(".hero-sub", { y: 24, opacity: 0, duration: 0.9 }, "-=0.7")
        .from(".hero-meta", { y: 18, opacity: 0, stagger: 0.12, duration: 0.7 }, "-=0.5")
        .from(".hero-cue", { opacity: 0, duration: 0.8 }, "-=0.3");

      // parallax drift of the aura layers as you scroll out of the hero
      gsap.to(".aura-a", {
        yPercent: 30,
        scrollTrigger: { trigger: root.current, start: "top top", end: "bottom top", scrub: true },
      });
      gsap.to(".aura-b", {
        yPercent: -20,
        scrollTrigger: { trigger: root.current, start: "top top", end: "bottom top", scrub: true },
      });
      gsap.to(".hero-content", {
        yPercent: -12,
        opacity: 0.15,
        scrollTrigger: { trigger: root.current, start: "top top", end: "bottom top", scrub: true },
      });
    },
    { scope: root },
  );

  return (
    <section
      id="top"
      ref={root}
      className="relative flex h-[100svh] items-center justify-center overflow-hidden bg-grid"
    >
      {/* aura / nebula layers */}
      <div className="aura-a pointer-events-none absolute -top-1/4 left-1/2 h-[80vmax] w-[80vmax] -translate-x-1/2 rounded-full opacity-60 blur-[120px]"
        style={{ background: "radial-gradient(circle, rgba(160,107,255,0.45), transparent 60%)" }}
      />
      <div className="aura-b pointer-events-none absolute bottom-[-30%] left-[20%] h-[60vmax] w-[60vmax] rounded-full opacity-50 blur-[120px]"
        style={{ background: "radial-gradient(circle, rgba(56,240,216,0.35), transparent 60%)" }}
      />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_30%,rgba(4,5,10,0.9)_80%)]" />

      <div className="hero-content relative z-10 px-6 text-center">
        <p className="hero-meta mb-7 font-mono text-[11px] uppercase tracking-[0.5em] text-[var(--color-cyan)]/80">
          self-updating documentation
        </p>

        <h1 className="select-none text-[15vw] font-bold leading-[0.85] tracking-tight md:text-[12vw] lg:text-[10rem]">
          <span className="sr-only">{TITLE}</span>
          <span aria-hidden className="block [perspective:600px]">
            {TITLE.split("").map((c, i) => (
              <span key={i} className="hero-char inline-block text-gradient text-glow">
                {c === " " ? " " : c}
              </span>
            ))}
          </span>
        </h1>

        <div className="hero-line mx-auto my-8 h-px w-[min(420px,70vw)] origin-center bg-gradient-to-r from-transparent via-white/60 to-transparent" />

        <p className="hero-sub mx-auto max-w-xl text-balance text-base text-white/70 md:text-lg">
          Reference docs generated from your code, config and git history — and a
          drift check that makes <span className="text-white">stale docs fail CI</span>.
        </p>
      </div>

      <div className="hero-cue absolute bottom-8 left-1/2 z-10 flex -translate-x-1/2 flex-col items-center gap-2 text-white/40">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em]">scroll</span>
        <span className="h-10 w-px animate-pulse bg-gradient-to-b from-white/60 to-transparent" />
      </div>
    </section>
  );
}
