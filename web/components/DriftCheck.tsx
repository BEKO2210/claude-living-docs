"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

export default function DriftCheck() {
  const root = useRef<HTMLDivElement>(null);
  const stage = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      gsap.registerPlugin(ScrollTrigger);

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: root.current,
          start: "top top",
          end: "+=260%",
          scrub: 0.7,
          pin: stage.current,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });

      tl.from(".dc-prompt", { opacity: 0, x: -10, duration: 0.2 });
      tl.fromTo(".dc-red", { opacity: 0, y: 8 }, { opacity: 1, y: 0, stagger: 0.12, duration: 0.15 }, ">");
      tl.to(".dc-glow-red", { opacity: 1, duration: 0.2 }, "<");
      tl.to(".dc-verdict-red", { opacity: 1, scale: 1, duration: 0.2 }, ">");

      // hold, then resolve
      tl.to({}, { duration: 0.4 });
      tl.to(".dc-screen-red", { opacity: 0, y: -24, duration: 0.25 });
      tl.to(".dc-glow-red", { opacity: 0, duration: 0.25 }, "<");
      tl.fromTo(".dc-green", { opacity: 0, y: 12 }, { opacity: 1, y: 0, stagger: 0.12, duration: 0.18 }, ">");
      tl.to(".dc-glow-green", { opacity: 1, duration: 0.25 }, "<");
      tl.to(".dc-verdict-green", { opacity: 1, scale: 1, duration: 0.25 }, ">");
    },
    { scope: root },
  );

  return (
    <section ref={root} className="relative h-[360vh]">
      <div ref={stage} className="flex h-[100svh] flex-col items-center justify-center overflow-hidden px-6">
        <p className="mb-3 font-mono text-xs uppercase tracking-[0.4em] text-[var(--color-cyan)]/80">
          the killer feature
        </p>
        <h2 className="mb-12 max-w-2xl text-center text-3xl font-medium tracking-tight md:text-5xl">
          A drift check turns <span className="text-[var(--color-violet)]">“probably stale”</span> into{" "}
          <span className="text-gradient">a failing build</span>.
        </h2>

        <div className="relative w-full max-w-2xl">
          <div className="dc-glow-red pointer-events-none absolute -inset-6 rounded-3xl opacity-0 blur-2xl"
            style={{ background: "radial-gradient(circle, rgba(255,70,90,0.5), transparent 70%)" }}
          />
          <div className="dc-glow-green pointer-events-none absolute -inset-6 rounded-3xl opacity-0 blur-2xl"
            style={{ background: "radial-gradient(circle, rgba(56,240,150,0.5), transparent 70%)" }}
          />

          <div className="glass relative overflow-hidden rounded-2xl">
            <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3">
              <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
              <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
              <span className="h-3 w-3 rounded-full bg-[#28c840]" />
              <span className="ml-3 font-mono text-xs text-white/40">ci · drift check</span>
            </div>

            <div className="relative h-72 p-5 font-mono text-[13px] leading-relaxed md:text-sm">
              {/* RED screen */}
              <div className="dc-screen-red absolute inset-0 p-5">
                <p className="dc-prompt text-white/80">
                  <span className="text-[var(--color-cyan)]">$</span> living-docs check
                </p>
                <p className="dc-red mt-2 text-white/40">comparing docs/ against sources…</p>
                <p className="dc-red mt-2 text-white/50">--- API.md (on disk)</p>
                <p className="dc-red text-white/50">+++ API.md (generated)</p>
                <p className="dc-red text-[#ff8a98]">- Callables: 24</p>
                <p className="dc-red text-[#7dffc4]">+ Callables: 25</p>
                <p className="dc-verdict-red mt-3 inline-block scale-95 rounded-md bg-[#ff465a]/15 px-2 py-1 text-[#ff8a98] opacity-0">
                  DRIFT: 1 document out of date · exit 1
                </p>
              </div>

              {/* GREEN screen */}
              <div className="absolute inset-0 p-5">
                <p className="dc-green text-white/80 opacity-0">
                  <span className="text-[var(--color-cyan)]">$</span> living-docs update
                </p>
                <p className="dc-green text-white/40 opacity-0">wrote docs/API.md</p>
                <p className="dc-green text-white/80 opacity-0">
                  <span className="text-[var(--color-cyan)]">$</span> living-docs check
                </p>
                <p className="dc-green text-white/40 opacity-0">OK: 4 documents up to date.</p>
                <p className="dc-verdict-green mt-3 inline-block scale-95 rounded-md bg-[#28c840]/15 px-2 py-1 text-[#7dffc4] opacity-0">
                  ✓ in sync · exit 0
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
