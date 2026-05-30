"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

const LINE_ONE = "Documentation rots.";
const LINE_TWO = "Here, stale docs are a build failure — not a silent lie.";

export default function Manifesto() {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      gsap.registerPlugin(ScrollTrigger);

      gsap.fromTo(
        ".man-word",
        { opacity: 0.08, filter: "blur(6px)" },
        {
          opacity: 1,
          filter: "blur(0px)",
          stagger: 0.4,
          ease: "none",
          scrollTrigger: {
            trigger: root.current,
            start: "top 70%",
            end: "bottom 60%",
            scrub: true,
          },
        },
      );
    },
    { scope: root },
  );

  return (
    <section ref={root} className="relative mx-auto max-w-5xl px-6 py-[22vh]">
      <h2 className="text-3xl font-medium leading-[1.25] tracking-tight md:text-5xl md:leading-[1.2]">
        <span className="mb-6 block font-mono text-xs uppercase tracking-[0.4em] text-[var(--color-violet)]">
          the problem
        </span>
        {LINE_ONE.split(" ").map((w, i) => (
          <span key={`a${i}`} className="man-word text-gradient">
            {w}{" "}
          </span>
        ))}
        <br />
        {LINE_TWO.split(" ").map((w, i) => (
          <span key={`b${i}`} className="man-word text-white">
            {w}{" "}
          </span>
        ))}
      </h2>
    </section>
  );
}
