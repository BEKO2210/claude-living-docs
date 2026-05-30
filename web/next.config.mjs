/** @type {import('next').NextConfig} */
const nextConfig = {
  // Emit a fully static HTML site into `out/` — deployable on any static host.
  output: "export",
  images: { unoptimized: true },
  // Set NEXT_PUBLIC_BASE_PATH=/repo-name when hosting under a sub-path
  // (e.g. GitHub Pages). Left empty for root-level hosting / local preview.
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || "",
  trailingSlash: true,
};

export default nextConfig;
