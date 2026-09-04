import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export default function SignIn() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    if (!email || !password) {
      return;
    }

    localStorage.setItem(
      "trace_authenticated",
      "true"
    );

    localStorage.setItem(
      "trace_user",
      email
    );

    navigate("/app");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F7F9FC] px-6 py-10">
      <div className="w-full max-w-md">
        <Link
          to="/"
          className="mb-8 inline-flex items-center gap-2 text-sm text-[#667085] hover:text-[#111827]"
        >
          <ArrowLeft size={16} />
          Back to TRACE
        </Link>

        <div className="rounded-2xl border border-[#E5E7EB] bg-white p-8 shadow-sm">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-[#2563EB] text-white">
            <ShieldCheck size={22} />
          </div>

          <h1 className="mt-6 text-2xl font-bold text-[#111827]">
            Welcome to TRACE
          </h1>

          <p className="mt-2 text-sm text-[#667085]">
            Sign in to access the fraud intelligence platform.
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-5"
          >
            <div>
              <label className="mb-2 block text-sm font-medium text-[#344054]">
                Email
              </label>

              <input
                type="email"
                required
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                placeholder="you@company.com"
                className="w-full rounded-lg border border-[#D0D5DD] bg-white px-3.5 py-2.5 text-sm outline-none transition focus:border-[#2563EB] focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-[#344054]">
                Password
              </label>

              <input
                type="password"
                required
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                placeholder="••••••••"
                className="w-full rounded-lg border border-[#D0D5DD] bg-white px-3.5 py-2.5 text-sm outline-none transition focus:border-[#2563EB] focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-lg bg-[#2563EB] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#1D4ED8]"
            >
              Sign In
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-[#98A2B3]">
            Demo authentication for the TRACE prototype.
          </p>
        </div>
      </div>
    </div>
  );
}