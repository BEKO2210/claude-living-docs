"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { useRef } from "react";
import { repoUrl } from "@/lib/data";

export default function Nav() {
  const ref = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      gsap.from(ref.current, {
        y: -60,
        opacity: 0,
        duration: 1,
        delay: 1.6,
        ease: "power3.out",
      });
    },
    { scope: ref },
  );

  return (
    <nav
      ref={ref}
      className="fixed inset-x-0 top-0 z-50 flex items-center justify-between px-6 py-5 md:px-10"
    >
      <a href="#top" className="flex items-center gap-2.5 font-mono text-sm tracking-wide">
        <span className="relative grid h-7 w-7 place-items-center rounded-md ring-glow">
          <span className="absolute inset-0 rounded-md bg-gradient-to-br from-[var(--color-violet)]/30 to-[var(--color-cyan)]/30" />
          <span className="relative h-1.5 w-1.5 rounded-full bg-[var(--color-cyan)] shadow-[0_0_12px_var(--color-cyan)]" />
        </span>
        <span className="text-white/90">living-docs</span>
      </a>
      <a
        href={repoUrl}
        target="_blank"
        rel="noreferrer"
        className="font-mono text-xs text-white/60 transition hover:text-white"
      >
        GitHub ↗
      </a>
    </nav>
  );
}
