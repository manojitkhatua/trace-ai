import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Activity,
} from "lucide-react";

import { AppLayout } from "../components/layout/AppLayout";
import { StatCard } from "../components/ui/StatCard";
import { Card, CardHeader } from "../components/ui/Card";
import { DecisionBadge } from "../components/ui/Badge";
import { useTrace } from "../context/TraceContext";
import {
  formatCurrency,
  formatRelativeTime,
  truncateMiddle,
} from "../utils/format";

export default function Overview() {
  const { history, isDemoOnly } = useTrace();

  const stats = useMemo(() => {
    const total = history.length;
    const allowed = history.filter(
      (r) => r.decision === "ALLOW"
    ).length;
    const review = history.filter(
      (r) => r.decision === "REVIEW"
    ).length;
    const blocked = history.filter(
      (r) => r.decision === "BLOCK"
    ).length;

    return {
      total,
      allowed,
      review,
      blocked,
    };
  }, [history]);

  const recent = useMemo(
    () => history.slice(0, 6),
    [history]
  );

  return (
    <AppLayout
      title="Overview"
      subtitle="A simple view of TRACE fraud decisions"
    >
      {/* Demo notice */}
      {isDemoOnly && (
        <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <strong>Demo Mode:</strong>{" "}
          Showing sample transactions. Run a transaction from{" "}
          <Link
            to="/analyze"
            className="font-semibold underline"
          >
            Analyze
          </Link>{" "}
          to connect TRACE to the live API.
        </div>
      )}

      {/* Summary */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="Transactions"
          value={stats.total}
          icon={Activity}
          tone="default"
          hint="Analyzed"
        />

        <StatCard
          label="Allowed"
          value={stats.allowed}
          icon={ShieldCheck}
          tone="green"
          hint={`${percent(stats.allowed, stats.total)} of total`}
        />

        <StatCard
          label="Needs Review"
          value={stats.review}
          icon={ShieldAlert}
          tone="amber"
          hint={`${percent(stats.review, stats.total)} of total`}
        />

        <StatCard
          label="Blocked"
          value={stats.blocked}
          icon={ShieldX}
          tone="red"
          hint={`${percent(stats.blocked, stats.total)} of total`}
        />
      </div>

      {/* Main action */}
      <Card className="mt-6">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-[#111827]">
              Analyze a transaction
            </p>

            <p className="mt-1 max-w-xl text-sm text-[#667085]">
              Enter a few transaction details and let TRACE
              evaluate the risk and recommend an action.
            </p>
          </div>

          <Link
            to="/analyze"
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-[#2563EB] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#1D4ED8]"
          >
            Analyze Transaction
            <ArrowRight size={16} />
          </Link>
        </div>
      </Card>

      {/* Recent activity */}
      <Card className="mt-6" padded={false}>
        <div className="flex items-center justify-between px-5 pt-5">
          <CardHeader
            title="Recent Decisions"
            subtitle="Latest transactions analyzed by TRACE"
          />

          <Link
            to="/audit-trail"
            className="mb-4 inline-flex items-center gap-1 text-xs font-semibold text-[#2563EB] hover:underline"
          >
            View all
            <ArrowRight size={13} />
          </Link>
        </div>

        {recent.length === 0 ? (
          <div className="px-5 py-10 text-center">
            <p className="text-sm font-medium text-[#344054]">
              No transactions yet
            </p>

            <p className="mt-1 text-sm text-[#98A2B3]">
              Analyze your first transaction to see it here.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-y border-[#E5E7EB] text-xs uppercase tracking-wide text-[#98A2B3]">
                  <th className="px-5 py-3 font-medium">
                    Transaction
                  </th>

                  <th className="px-5 py-3 font-medium">
                    Amount
                  </th>

                  <th className="px-5 py-3 font-medium">
                    Risk
                  </th>

                  <th className="px-5 py-3 font-medium">
                    Decision
                  </th>

                  <th className="px-5 py-3 font-medium">
                    Time
                  </th>
                </tr>
              </thead>

              <tbody>
                {recent.map((record) => (
                  <tr
                    key={record.id}
                    className="border-b border-[#F2F4F7] last:border-0"
                  >
                    <td className="px-5 py-3 font-mono text-xs text-[#344054]">
                      {truncateMiddle(record.id, 16)}
                    </td>

                    <td className="px-5 py-3 text-[#344054]">
                      {formatCurrency(
                        record.input?.amount
                      )}
                    </td>

                    <td className="px-5 py-3 font-semibold text-[#111827]">
                      {Number(
                        record.scores?.riskScore || 0
                      ).toFixed(1)}
                    </td>

                    <td className="px-5 py-3">
                      <DecisionBadge
                        decision={record.decision}
                      />
                    </td>

                    <td className="px-5 py-3 text-xs text-[#667085]">
                      {formatRelativeTime(
                        record.timestamp
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Simple explanation */}
      <Card className="mt-6">
        <CardHeader
          title="How TRACE works"
          subtitle="Complex intelligence, simple decision"
        />

        <div className="grid gap-3 sm:grid-cols-4">
          <Step
            number="1"
            title="Analyze"
            text="Transaction data enters TRACE."
          />

          <Step
            number="2"
            title="Evaluate"
            text="ML, anomaly and entity signals are checked."
          />

          <Step
            number="3"
            title="Decide"
            text="TRACE returns Allow, Review or Block."
          />

          <Step
            number="4"
            title="Explain"
            text="The decision is explained and recorded."
          />
        </div>
      </Card>
    </AppLayout>
  );
}

function Step({ number, title, text }) {
  return (
    <div className="rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] p-4">
      <div className="mb-3 flex h-7 w-7 items-center justify-center rounded-full bg-[#EFF6FF] text-xs font-bold text-[#2563EB]">
        {number}
      </div>

      <p className="text-sm font-semibold text-[#111827]">
        {title}
      </p>

      <p className="mt-1 text-xs leading-5 text-[#667085]">
        {text}
      </p>
    </div>
  );
}

function percent(value, total) {
  if (!total) return "0%";
  return `${Math.round((value / total) * 100)}%`;
}