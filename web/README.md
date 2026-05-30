# living-docs · cinematic site

A scroll-driven, futuristic visualization of the living-docs engine, built with
**Next.js (App Router) · Tailwind CSS v4 · GSAP + ScrollTrigger · Lenis**.

It tells the project's story in seven scroll acts: hero → the problem → the
`code → AST → Markdown → docs` pipeline (scroll-scrubbed) → the module
constellation → the drift-check terminal (red → green) → measured benchmarks →
call to action. All numbers are pulled from the real project
(`lib/data.ts`), not invented.

## Develop

```bash
cd web
npm install
npm run dev        # http://localhost:3000
```

## Build a static site

```bash
npm run build      # emits a fully static site into web/out/
```

`next.config.mjs` uses `output: "export"`, so `out/` is plain HTML/CSS/JS that
deploys to any static host (GitHub Pages, Netlify, Vercel, S3, …).

When hosting under a sub-path (e.g. GitHub Pages at `/claude-living-docs`):

```bash
NEXT_PUBLIC_BASE_PATH=/claude-living-docs npm run build
```

## Structure

```
app/         layout.tsx · page.tsx · globals.css (Tailwind v4 + theme tokens)
components/   Hero · Manifesto · Pipeline · Architecture · DriftCheck
              Benchmarks · CTA · Nav · SmoothScroll (Lenis ↔ ScrollTrigger)
lib/data.ts   real project data: pipeline, modules, benchmark numbers, stats
```

Animations honour `prefers-reduced-motion` (Lenis momentum scrolling is
disabled when the user opts out).
