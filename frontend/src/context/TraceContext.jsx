import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { ALL_DEMO_RECORDS } from "../utils/demoData";
import { API_BASE_URL } from "../services/api";

const STORAGE_KEY = "trace_history_v1";

const TraceContext = createContext(null);

function loadStoredHistory() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);

    if (!raw) return null;

    const parsed = JSON.parse(raw);

    return Array.isArray(parsed) && parsed.length
      ? parsed
      : null;
  } catch {
    return null;
  }
}

export function TraceProvider({ children }) {
  const initialHistory = loadStoredHistory() || ALL_DEMO_RECORDS;

  const [history, setHistory] = useState(initialHistory);

  const [currentId, setCurrentId] = useState(
    initialHistory[0]?.id || null
  );

  const [apiStatus, setApiStatus] = useState({
    mode: "unknown",
    checkedAt: null,
    error: null,
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(history.slice(0, 200))
      );
    } catch {
      // Ignore localStorage errors.
    }
  }, [history]);

  // Check the live Render backend.
  useEffect(() => {
    let cancelled = false;

    async function checkApi() {
      try {
        const controller = new AbortController();

        const timer = setTimeout(() => {
          controller.abort();
        }, 10000);

        const response = await fetch(
          API_BASE_URL.replace(/\/$/, ""),
          {
            method: "GET",
            signal: controller.signal,
          }
        );

        clearTimeout(timer);

        if (!response.ok) {
          throw new Error(
            `TRACE API health check failed: ${response.status}`
          );
        }

        const data = await response.json();

        if (!cancelled) {
          setApiStatus({
            mode: data?.status === "ok" ? "live" : "unknown",
            checkedAt: new Date().toISOString(),
            error: null,
          });
        }
      } catch (error) {
        if (!cancelled) {
          setApiStatus({
            mode: "offline",
            checkedAt: new Date().toISOString(),
            error:
              error?.message ||
              "TRACE API is unreachable.",
          });
        }
      }
    }

    checkApi();

    return () => {
      cancelled = true;
    };
  }, []);

  const addRecord = useCallback((record) => {
    setHistory((previous) => [record, ...previous]);
    setCurrentId(record.id);
  }, []);

  const current = useMemo(
    () =>
      history.find((record) => record.id === currentId) ||
      history[0] ||
      null,
    [history, currentId]
  );

  const isDemoOnly = useMemo(
    () => history.every((record) => record.source === "demo"),
    [history]
  );

  const resetHistory = useCallback(() => {
    setHistory(ALL_DEMO_RECORDS);
    setCurrentId(ALL_DEMO_RECORDS[0]?.id || null);

    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore localStorage errors.
    }
  }, []);

  const value = useMemo(
    () => ({
      history,
      current,
      currentId,
      addRecord,
      setCurrentId,
      isDemoOnly,
      apiStatus,
      setApiStatus,
      resetHistory,
    }),
    [
      history,
      current,
      currentId,
      addRecord,
      isDemoOnly,
      apiStatus,
      resetHistory,
    ]
  );

  return (
    <TraceContext.Provider value={value}>
      {children}
    </TraceContext.Provider>
  );
}

export function useTrace() {
  const context = useContext(TraceContext);

  if (!context) {
    throw new Error(
      "useTrace must be used inside a TraceProvider"
    );
  }

  return context;
}