// Real data pulled from the living-docs project itself — not invented.

export const stats = {
  coverage: 97,
  callables: 25,
  docstringCoverage: 100,
  generatedDocs: 4,
  modules: 9,
  generatorLines: 1180,
};

export type PipelineStep = {
  id: string;
  label: string;
  sub: string;
  detail: string;
};

export const pipeline: PipelineStep[] = [
  {
    id: "code",
    label: "Code",
    sub: "src/ · Python",
    detail: "Your source is the single source of truth. Nothing is written by hand.",
  },
  {
    id: "ast",
    label: "AST",
    sub: "extractors.py",
    detail: "Parsed with the stdlib ast module — signatures, type hints, decorators. The code is never imported.",
  },
  {
    id: "markdown",
    label: "Markdown",
    sub: "generators.py",
    detail: "Pure, deterministic renderers. Same input → byte-identical output, every run.",
  },
  {
    id: "docs",
    label: "docs/",
    sub: "drift-checked",
    detail: "Committed artifacts. If they ever drift from the code, CI turns red.",
  },
];

export type ModuleNode = {
  name: string;
  role: string;
  // normalized 0..1 position for the constellation layout
  x: number;
  y: number;
};

export const modules: ModuleNode[] = [
  { name: "cli", role: "the living-docs command", x: 0.5, y: 0.12 },
  { name: "engine", role: "orchestrates every document", x: 0.5, y: 0.42 },
  { name: "config", role: "[tool.living_docs] · zero-config", x: 0.2, y: 0.3 },
  { name: "extractors", role: "AST → typed data", x: 0.16, y: 0.66 },
  { name: "generators", role: "data → Markdown", x: 0.84, y: 0.66 },
  { name: "sources", role: "JSON + git history", x: 0.8, y: 0.3 },
  { name: "build", role: "deterministic timestamps", x: 0.34, y: 0.86 },
  { name: "benchmark", role: "vs pdoc & sphinx", x: 0.66, y: 0.86 },
];

// Edges describing how modules depend on each other (for the constellation).
export const moduleEdges: [string, string][] = [
  ["cli", "engine"],
  ["cli", "config"],
  ["engine", "extractors"],
  ["engine", "generators"],
  ["engine", "sources"],
  ["engine", "config"],
  ["extractors", "build"],
  ["generators", "build"],
  ["sources", "build"],
  ["benchmark", "generators"],
  ["benchmark", "extractors"],
];

export type Benchmark = {
  tool: string;
  ms: number;
  lines: number;
  output: string;
  hero?: boolean;
};

// Measured: timeit, 10 runs, median — from benchmarks/results.json.
export const benchmarks: Benchmark[] = [
  { tool: "living-docs", ms: 9.12, lines: 292, output: "single Markdown file", hero: true },
  { tool: "pdoc", ms: 402.78, lines: 531, output: "HTML site" },
  { tool: "sphinx-apidoc", ms: 238.78, lines: 84, output: "reST stub files" },
];

export const repoUrl = "https://github.com/beko2210/claude-living-docs";
