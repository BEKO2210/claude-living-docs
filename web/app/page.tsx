import SmoothScroll from "@/components/SmoothScroll";
import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import Manifesto from "@/components/Manifesto";
import Pipeline from "@/components/Pipeline";
import Architecture from "@/components/Architecture";
import DriftCheck from "@/components/DriftCheck";
import Benchmarks from "@/components/Benchmarks";
import CTA from "@/components/CTA";

export default function Home() {
  return (
    <>
      <SmoothScroll />
      <Nav />
      <main className="relative">
        <Hero />
        <Manifesto />
        <Pipeline />
        <Architecture />
        <DriftCheck />
        <Benchmarks />
        <CTA />
      </main>
    </>
  );
}
