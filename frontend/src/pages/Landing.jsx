import { Link } from "react-router-dom";
import {
  ArrowRight,
  ShieldCheck,
  Zap,
  Brain,
  FileCheck,
  CheckCircle2,
} from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#F7F9FC] text-[#111827]">
      {/* NAVBAR */}
      <header className="border-b border-[#E5E7EB] bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#2563EB] text-white">
              <ShieldCheck size={20} />
            </div>

            <div>
              <p className="text-lg font-bold tracking-tight">TRACE</p>
              <p className="text-[10px] font-medium uppercase tracking-wider text-[#667085]">
                Real-Time Fraud Intelligence
              </p>
            </div>
          </Link>

          <nav className="hidden items-center gap-8 text-sm text-[#667085] md:flex">
            <a href="#how-it-works" className="hover:text-[#111827]">
              How it works
            </a>
            <a href="#why-trace" className="hover:text-[#111827]">
              Why TRACE
            </a>
            <a href="#security" className="hover:text-[#111827]">
              Security
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              to="/sign-in"
              className="rounded-lg px-4 py-2 text-sm font-semibold text-[#344054] hover:bg-[#F2F4F7]"
            >
              Sign In
            </Link>

            <Link
              to="/sign-in"
              className="rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-semibold text-white hover:bg-[#1D4ED8]"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* HERO */}
      <main>
        <section className="mx-auto max-w-7xl px-6 pb-20 pt-20 lg:pt-28">
          <div className="grid items-center gap-14 lg:grid-cols-2">
            <div>
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-[#2563EB]">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2563EB]" />
                REAL-TIME FRAUD INTELLIGENCE
              </div>

              <h1 className="max-w-2xl text-4xl font-bold tracking-tight text-[#111827] sm:text-5xl lg:text-6xl">
                Stop fraud before it becomes a loss.
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-8 text-[#667085]">
                TRACE evaluates transaction risk using machine learning,
                behavioral signals, and entity intelligence to deliver fast,
                explainable decisions.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <Link
                  to="/sign-in"
                  className="inline-flex items-center gap-2 rounded-lg bg-[#2563EB] px-5 py-3 text-sm font-semibold text-white hover:bg-[#1D4ED8]"
                >
                  Start with TRACE
                  <ArrowRight size={16} />
                </Link>

                <a
                  href="#how-it-works"
                  className="inline-flex items-center gap-2 rounded-lg border border-[#D0D5DD] bg-white px-5 py-3 text-sm font-semibold text-[#344054] hover:bg-[#F9FAFB]"
                >
                  See how it works
                </a>
              </div>

              <div className="mt-8 grid gap-3 sm:grid-cols-3">
                <FeatureCheck text="Real-time risk scoring" />
                <FeatureCheck text="Explainable decisions" />
                <FeatureCheck text="Auditable decisions" />
              </div>
            </div>

            {/* PRODUCT PREVIEW */}
            <div className="rounded-2xl border border-[#DCE3EC] bg-white p-5 shadow-sm">
              <div className="rounded-xl border border-[#E5E7EB] bg-[#F9FAFB] p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-[#667085]">
                      TRACE Risk Assessment
                    </p>
                    <p className="mt-1 text-sm text-[#98A2B3]">
                      Transaction #TRX-8F42A1
                    </p>
                  </div>

                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                    ALLOW
                  </span>
                </div>

                <div className="mt-8 text-center">
                  <p className="text-xs font-medium uppercase tracking-wide text-[#667085]">
                    Risk Score
                  </p>

                  <p className="mt-2 text-6xl font-bold tracking-tight text-[#111827]">
                    16.8
                  </p>

                  <p className="mt-1 text-sm font-semibold text-emerald-600">
                    LOW RISK
                  </p>
                </div>

                <div className="mt-8 grid grid-cols-3 gap-3">
                  <MiniMetric label="Fraud" value="8.0%" />
                  <MiniMetric label="Anomaly" value="Low" />
                  <MiniMetric label="Entity" value="Low" />
                </div>

                <div className="mt-5 rounded-lg border border-[#E5E7EB] bg-white p-4">
                  <p className="text-sm font-semibold text-[#111827]">
                    Why was this allowed?
                  </p>

                  <div className="mt-3 space-y-2 text-sm text-[#667085]">
                    <Reason text="Transaction pattern looks normal" />
                    <Reason text="No major anomaly detected" />
                    <Reason text="Entity risk remains low" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section
          id="how-it-works"
          className="border-y border-[#E5E7EB] bg-white"
        >
          <div className="mx-auto max-w-7xl px-6 py-20">
            <SectionHeading
              eyebrow="HOW TRACE WORKS"
              title="Complex intelligence. Simple decisions."
              text="TRACE combines multiple signals behind the scenes and presents one clear operational decision."
            />

            <div className="mt-12 grid gap-5 md:grid-cols-4">
              <ProcessStep
                number="01"
                title="Transaction"
                text="Transaction data enters TRACE."
              />
              <ProcessStep
                number="02"
                title="Analyze"
                text="ML, anomaly and entity signals are evaluated."
              />
              <ProcessStep
                number="03"
                title="Decide"
                text="TRACE returns Allow, Review or Block."
              />
              <ProcessStep
                number="04"
                title="Explain"
                text="The decision is explained and recorded."
              />
            </div>
          </div>
        </section>

        {/* WHY TRACE */}
        <section id="why-trace" className="mx-auto max-w-7xl px-6 py-20">
          <SectionHeading
            eyebrow="WHY TRACE"
            title="Built for decisions, not dashboards."
            text="The goal is not to overwhelm analysts with model output. TRACE turns complex fraud signals into an actionable result."
          />

          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            <ValueCard
              icon={Zap}
              title="Real-Time"
              text="Evaluate transactions quickly as they arrive."
            />

            <ValueCard
              icon={Brain}
              title="Explainable"
              text="Understand why TRACE reached a decision."
            />

            <ValueCard
              icon={ShieldCheck}
              title="Multi-Signal"
              text="Combine fraud, anomaly and entity intelligence."
            />

            <ValueCard
              icon={FileCheck}
              title="Auditable"
              text="Keep a traceable record of every decision."
            />
          </div>
        </section>

        {/* IMPACT */}
        <section id="security" className="bg-[#111827]">
          <div className="mx-auto max-w-7xl px-6 py-20">
            <div className="max-w-3xl">
              <p className="text-sm font-semibold uppercase tracking-wider text-blue-300">
                THE TRACE APPROACH
              </p>

              <h2 className="mt-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Fraud teams do not need more alerts.
                <br />
                They need better decisions.
              </h2>

              <p className="mt-5 text-lg leading-8 text-slate-300">
                TRACE brings model intelligence, behavioral analysis and entity
                signals together so teams can act with confidence.
              </p>
            </div>

            <div className="mt-10 flex flex-wrap gap-3">
              <DecisionPill label="ALLOW" />
              <DecisionPill label="REVIEW" />
              <DecisionPill label="BLOCK" />
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-white">
          <div className="mx-auto max-w-4xl px-6 py-20 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-[#111827] sm:text-4xl">
              Ready to analyze your first transaction?
            </h2>

            <p className="mx-auto mt-4 max-w-xl text-[#667085]">
              Start with TRACE and turn complex fraud intelligence into a
              simple decision.
            </p>

            <Link
              to="/sign-in"
              className="mt-8 inline-flex items-center gap-2 rounded-lg bg-[#2563EB] px-5 py-3 text-sm font-semibold text-white hover:bg-[#1D4ED8]"
            >
              Get Started
              <ArrowRight size={16} />
            </Link>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="border-t border-[#E5E7EB] bg-[#F9FAFB]">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-8 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-bold text-[#111827]">TRACE</p>
            <p className="text-xs text-[#667085]">
              Real-Time Fraud Intelligence
            </p>
          </div>

          <p className="text-xs text-[#98A2B3]">
            © 2026 TRACE
          </p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCheck({ text }) {
  return (
    <div className="flex items-center gap-2 text-sm text-[#667085]">
      <CheckCircle2
        size={16}
        className="shrink-0 text-emerald-500"
      />
      {text}
    </div>
  );
}

function MiniMetric({ label, value }) {
  return (
    <div className="rounded-lg border border-[#E5E7EB] bg-white p-3">
      <p className="text-xs text-[#98A2B3]">{label}</p>
      <p className="mt-1 text-sm font-semibold text-[#111827]">
        {value}
      </p>
    </div>
  );
}

function Reason({ text }) {
  return (
    <div className="flex items-center gap-2">
      <CheckCircle2
        size={15}
        className="shrink-0 text-emerald-500"
      />
      {text}
    </div>
  );
}

function SectionHeading({ eyebrow, title, text }) {
  return (
    <div className="max-w-2xl">
      <p className="text-xs font-semibold uppercase tracking-wider text-[#2563EB]">
        {eyebrow}
      </p>
      <h2 className="mt-3 text-3xl font-bold tracking-tight text-[#111827]">
        {title}
      </h2>
      <p className="mt-4 text-base leading-7 text-[#667085]">
        {text}
      </p>
    </div>
  );
}

function ProcessStep({ number, title, text }) {
  return (
    <div className="rounded-xl border border-[#E5E7EB] bg-[#F9FAFB] p-5">
      <p className="text-xs font-bold text-[#2563EB]">{number}</p>
      <h3 className="mt-4 text-base font-semibold text-[#111827]">
        {title}
      </h3>
      <p className="mt-2 text-sm leading-6 text-[#667085]">
        {text}
      </p>
    </div>
  );
}

function ValueCard({ icon: Icon, title, text }) {
  return (
    <div className="rounded-xl border border-[#E5E7EB] bg-white p-5">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-[#2563EB]">
        <Icon size={20} />
      </div>

      <h3 className="mt-4 font-semibold text-[#111827]">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-[#667085]">
        {text}
      </p>
    </div>
  );
}

function DecisionPill({ label }) {
  const styles = {
    ALLOW: "bg-emerald-500 text-white",
    REVIEW: "bg-amber-400 text-[#111827]",
    BLOCK: "bg-red-500 text-white",
  };

  return (
    <span
      className={`rounded-lg px-5 py-2 text-sm font-bold ${styles[label]}`}
    >
      {label}
    </span>
  );
}