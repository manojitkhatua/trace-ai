import { ReactNode } from "react";
import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import { TraceProvider } from "./context/TraceContext";

import Landing from "./pages/Landing";
import SignIn from "./pages/SignIn";
import Overview from "./pages/Overview";
import Analyze from "./pages/Analyze";
import Investigation from "./pages/Investigation";
import RiskIntelligence from "./pages/RiskIntelligence";
import AuditTrail from "./pages/AuditTrail";

function RequireAuth({ children }: { children: ReactNode }) {
  const authenticated =
    localStorage.getItem("trace_authenticated") === "true";

  if (!authenticated) {
    return <Navigate to="/sign-in" replace />;
  }

  return children;
}

export default function App() {
  return (
    <HashRouter>
      <TraceProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/sign-in" element={<SignIn />} />

          {/* Protected application routes */}
          <Route
            path="/app"
            element={
              <RequireAuth>
                <Overview />
              </RequireAuth>
            }
          />

          <Route
            path="/app/analyze"
            element={
              <RequireAuth>
                <Analyze />
              </RequireAuth>
            }
          />

          <Route
            path="/app/investigation"
            element={
              <RequireAuth>
                <Investigation />
              </RequireAuth>
            }
          />

          <Route
            path="/app/risk-intelligence"
            element={
              <RequireAuth>
                <RiskIntelligence />
              </RequireAuth>
            }
          />

          <Route
            path="/app/audit-trail"
            element={
              <RequireAuth>
                <AuditTrail />
              </RequireAuth>
            }
          />

          {/* Backward-compatible routes */}
          <Route
            path="/analyze"
            element={<Navigate to="/app/analyze" replace />}
          />

          <Route
            path="/investigation"
            element={<Navigate to="/app/investigation" replace />}
          />

          <Route
            path="/risk-intelligence"
            element={<Navigate to="/app/risk-intelligence" replace />}
          />

          <Route
            path="/audit-trail"
            element={<Navigate to="/app/audit-trail" replace />}
          />

          {/* Unknown route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </TraceProvider>
    </HashRouter>
  );
}