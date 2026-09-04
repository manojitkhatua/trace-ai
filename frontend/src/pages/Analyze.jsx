import { useState } from "react";
import {
  ChevronDown,
  PlayCircle,
  RotateCcw,
  Sparkles,
  ShieldAlert,
  Info,
} from "lucide-react";

import { Link } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";

import {
  Card,
  CardHeader,
} from "../components/ui/Card";

import {
  FormField,
  TextInput,
  SelectInput,
} from "../components/ui/FormField";

import { InfoTooltip } from "../components/ui/InfoTooltip";

import {
  LoadingState,
  NoResultState,
  ErrorState,
} from "../components/ui/States";

import { DecisionHeader } from "../components/trace/DecisionHeader";

import { predictTransaction } from "../services/api";

import { useTrace } from "../context/TraceContext";

import {
  PRODUCT_CATEGORIES,
  CARD_NETWORKS,
  CARD_TYPES,
  DEVICE_TYPES,
} from "../utils/options";

import {
  DEMO_INPUT,
  VERIFIED_BLOCK_INPUT,
} from "../utils/demoData";


// ============================================================
// CURRENT LOCAL TIME FOR FORM
// ============================================================

function nowForInput() {
  const d = new Date();

  d.setSeconds(0, 0);

  d.setMinutes(
    d.getMinutes() -
      d.getTimezoneOffset()
  );

  return d.toISOString().slice(0, 16);
}


// ============================================================
// EMPTY FORM
// ============================================================

const EMPTY_FORM = {
  amount: "",

  timestamp: nowForInput(),

  cardId: "",

  productCategory:
    PRODUCT_CATEGORIES[0]?.value || "",

  cardNetwork:
    CARD_NETWORKS[0]?.value || "",

  cardType:
    CARD_TYPES[0]?.value || "",

  deviceType: "",

  deviceInfo: "",

  billingAddress: {
    line1: "",
    city: "",
    state: "",
    zip: "",
    country: null,
  },

  advanced: {
    card2: "",
    addr2: "",
    d7: "",
    d12: "",
    d13: "",
    d14: "",
  },
};


// ============================================================
// COMPONENT
// ============================================================

export default function Analyze() {
  const {
    addRecord,
    setApiStatus,
  } = useTrace();

  const [form, setForm] =
    useState(EMPTY_FORM);

  const [advancedOpen, setAdvancedOpen] =
    useState(false);

  const [status, setStatus] =
    useState("idle");

  const [analysis, setAnalysis] =
    useState(null);


  // ==========================================================
  // GENERIC FIELD UPDATE
  // ==========================================================

  function update(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }


  // ==========================================================
  // BILLING REGION
  // ==========================================================

  function updateBillingRegion(value) {
    setForm((current) => ({
      ...current,

      billingAddress: {
        ...current.billingAddress,
        state: value,
      },
    }));
  }


  // ==========================================================
  // ADVANCED FIELDS
  // ==========================================================

  function updateAdvanced(
    field,
    value
  ) {
    setForm((current) => ({
      ...current,

      advanced: {
        ...current.advanced,
        [field]: value,
      },
    }));
  }


  // ==========================================================
  // RUN ANALYSIS
  // ==========================================================

  async function runAnalysis(
    targetForm
  ) {
    setStatus("loading");

    setAnalysis(null);

    try {
      const outcome =
        await predictTransaction(
          targetForm
        );

      addRecord(
        outcome.result
      );

      setApiStatus({
        mode: outcome.mode,
        checkedAt: Date.now(),
        error: outcome.error,
      });

      setAnalysis(outcome);

      setStatus("done");
    } catch (error) {
      console.error(
        "TRACE analysis failed:",
        error
      );

      setStatus("error");

      setAnalysis(null);
    }
  }


  // ==========================================================
  // NORMAL FORM SUBMIT
  // ==========================================================

  function handleSubmit(event) {
    event.preventDefault();

    if (
      !form.amount ||
      !form.cardId
    ) {
      setStatus("error");
      return;
    }

    runAnalysis(form);
  }


  // ==========================================================
  // LOAD ALLOW DEMO
  // ==========================================================

  function loadDemo() {
    const demoForm = {
      ...EMPTY_FORM,

      ...DEMO_INPUT,

      // Normal demo can use current display time.
      timestamp:
        nowForInput(),

      billingAddress: {
        ...EMPTY_FORM.billingAddress,

        ...(
          DEMO_INPUT.billingAddress ||
          {}
        ),
      },

      advanced: {
        ...EMPTY_FORM.advanced,

        ...(
          DEMO_INPUT.advanced ||
          {}
        ),
      },
    };

    setForm(demoForm);

    runAnalysis(demoForm);
  }


  // ==========================================================
  // LOAD REAL VERIFIED BLOCK CASE
  // ==========================================================

  function loadVerifiedBlockDemo() {
    const blockForm = {
      ...EMPTY_FORM,

      ...VERIFIED_BLOCK_INPUT,

      // IMPORTANT:
      // Do NOT overwrite transactionDT.
      // The exact validation TransactionDT is required.

      timestamp:
        nowForInput(),

      billingAddress: {
        ...EMPTY_FORM.billingAddress,

        ...(
          VERIFIED_BLOCK_INPUT.billingAddress ||
          {}
        ),
      },

      advanced: {
        ...EMPTY_FORM.advanced,

        ...(
          VERIFIED_BLOCK_INPUT.advanced ||
          {}
        ),
      },
    };

    setForm(blockForm);

    runAnalysis(blockForm);
  }


  // ==========================================================
  // RESET
  // ==========================================================

  function reset() {
    setForm({
      ...EMPTY_FORM,
      timestamp: nowForInput(),
    });

    setAnalysis(null);

    setStatus("idle");
  }


  // ==========================================================
  // RESULT
  // ==========================================================

  const result =
    analysis?.result;


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <AppLayout
      title="Analyze Transaction"
      subtitle="Submit a transaction to run the TRACE decision pipeline"
    >

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">

        {/* ================================================= */}
        {/* LEFT PANEL */}
        {/* ================================================= */}

        <Card>

          <CardHeader
            title="Transaction Details"
            subtitle="Enter the basic information TRACE needs"
          />

          <form
            onSubmit={handleSubmit}
            className="space-y-6"
          >

            {/* ============================================= */}
            {/* TRANSACTION */}
            {/* ============================================= */}

            <div>

              <p className="mb-3 text-sm font-semibold text-[#111827]">
                Transaction
              </p>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

                <FormField
                  label="Amount (USD)"
                >
                  <TextInput
                    type="number"
                    min="0"
                    step="0.001"
                    required
                    placeholder="e.g. 84.500"
                    value={form.amount}
                    onChange={(e) =>
                      update(
                        "amount",
                        e.target.value
                      )
                    }
                  />
                </FormField>


                <FormField
                  label="Transaction Time"
                >
                  <TextInput
                    type="datetime-local"
                    required
                    value={form.timestamp}
                    onChange={(e) =>
                      update(
                        "timestamp",
                        e.target.value
                      )
                    }
                  />
                </FormField>

              </div>

            </div>


            {/* ============================================= */}
            {/* PAYMENT */}
            {/* ============================================= */}

            <div className="border-t border-[#EAECF0] pt-5">

              <p className="mb-3 text-sm font-semibold text-[#111827]">
                Payment
              </p>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

                <FormField
                  label="Payment / Card ID"
                  hint="Use the internal numeric card identifier"
                >
                  <TextInput
                    type="number"
                    min="0"
                    required
                    placeholder="e.g. 9300"
                    value={form.cardId}
                    onChange={(e) =>
                      update(
                        "cardId",
                        e.target.value
                      )
                    }
                  />
                </FormField>


                <FormField
                  label="Product Category"
                >
                  <SelectInput
                    options={
                      PRODUCT_CATEGORIES
                    }
                    value={
                      form.productCategory
                    }
                    onChange={(e) =>
                      update(
                        "productCategory",
                        e.target.value
                      )
                    }
                  />
                </FormField>


                <FormField
                  label="Card Network"
                >
                  <SelectInput
                    options={
                      CARD_NETWORKS
                    }
                    value={
                      form.cardNetwork
                    }
                    onChange={(e) =>
                      update(
                        "cardNetwork",
                        e.target.value
                      )
                    }
                  />
                </FormField>


                <FormField
                  label="Card Type"
                >
                  <SelectInput
                    options={
                      CARD_TYPES
                    }
                    value={
                      form.cardType
                    }
                    onChange={(e) =>
                      update(
                        "cardType",
                        e.target.value
                      )
                    }
                  />
                </FormField>

              </div>

            </div>


            {/* ============================================= */}
            {/* DEVICE */}
            {/* ============================================= */}

            <div className="border-t border-[#EAECF0] pt-5">

              <p className="mb-3 text-sm font-semibold text-[#111827]">

                Device{" "}

                <span className="font-normal text-[#98A2B3]">
                  (optional)
                </span>

              </p>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

                <FormField
                  label="Device Type"
                >
                  <SelectInput
                    options={[
                      {
                        label: "Not provided",
                        value: "",
                      },

                      ...DEVICE_TYPES,
                    ]}
                    value={
                      form.deviceType
                    }
                    onChange={(e) =>
                      update(
                        "deviceType",
                        e.target.value
                      )
                    }
                  />
                </FormField>


                <FormField
                  label="Device Information"
                  hint="OS / browser / device"
                >
                  <TextInput
                    placeholder="e.g. Android Device"
                    value={
                      form.deviceInfo
                    }
                    onChange={(e) =>
                      update(
                        "deviceInfo",
                        e.target.value
                      )
                    }
                  />
                </FormField>

              </div>

            </div>


            {/* ============================================= */}
            {/* BILLING REGION */}
            {/* ============================================= */}

            <div className="border-t border-[#EAECF0] pt-5">

              <div className="mb-3 flex items-center gap-1.5">

                <p className="text-sm font-semibold text-[#111827]">
                  Billing Region
                </p>

                <InfoTooltip
                  text="Optional region code used by the existing TRACE model."
                />

              </div>


              <FormField
                label="Region Code"
              >
                <TextInput
                  type="number"
                  min="0"
                  placeholder="e.g. 315"
                  value={
                    form.billingAddress.state
                  }
                  onChange={(e) =>
                    updateBillingRegion(
                      e.target.value
                    )
                  }
                />
              </FormField>

            </div>


            {/* ============================================= */}
            {/* ADVANCED */}
            {/* ============================================= */}

            <div className="border-t border-[#EAECF0] pt-5">

              <button
                type="button"
                onClick={() =>
                  setAdvancedOpen(
                    (open) => !open
                  )
                }
                className="flex w-full items-center justify-between text-left"
              >

                <span className="flex items-center gap-1.5 text-sm font-semibold text-[#344054]">

                  Advanced / Model Signals

                  <Info
                    size={14}
                    className="text-[#98A2B3]"
                  />

                </span>


                <ChevronDown
                  size={17}
                  className={`text-[#667085] transition-transform ${
                    advancedOpen
                      ? "rotate-180"
                      : ""
                  }`}
                />

              </button>


              {advancedOpen && (
                <div className="mt-4 grid grid-cols-2 gap-4">

                  <FormField
                    label="Card Attribute"
                  >
                    <TextInput
                      type="number"
                      placeholder="Optional"
                      value={
                        form.advanced.card2
                      }
                      onChange={(e) =>
                        updateAdvanced(
                          "card2",
                          e.target.value
                        )
                      }
                    />
                  </FormField>


                  <FormField
                    label="Secondary Region"
                  >
                    <TextInput
                      type="number"
                      placeholder="Optional"
                      value={
                        form.advanced.addr2
                      }
                      onChange={(e) =>
                        updateAdvanced(
                          "addr2",
                          e.target.value
                        )
                      }
                    />
                  </FormField>


                  {[
                    "d7",
                    "d12",
                    "d13",
                    "d14",
                  ].map((key) => (
                    <FormField
                      key={key}
                      label={key.toUpperCase()}
                    >
                      <TextInput
                        type="number"
                        step="0.1"
                        placeholder="Optional"
                        value={
                          form.advanced[key]
                        }
                        onChange={(e) =>
                          updateAdvanced(
                            key,
                            e.target.value
                          )
                        }
                      />
                    </FormField>
                  ))}

                </div>
              )}

            </div>


            {/* ============================================= */}
            {/* ACTIONS */}
            {/* ============================================= */}

            <div className="flex flex-wrap items-center gap-3 pt-1">

              <button
                type="submit"
                disabled={
                  status === "loading"
                }
                className="inline-flex items-center gap-2 rounded-lg bg-[#2563EB] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#1D4ED8] disabled:cursor-not-allowed disabled:opacity-60"
              >

                <PlayCircle size={17} />

                {status === "loading"
                  ? "Analyzing..."
                  : "Run TRACE Analysis"}

              </button>


              {/* ALLOW */}

              <button
                type="button"
                onClick={loadDemo}
                disabled={
                  status === "loading"
                }
                className="inline-flex items-center gap-2 rounded-lg border border-[#D0D5DD] bg-white px-4 py-2.5 text-sm font-semibold text-[#344054] transition hover:bg-[#F9FAFB] disabled:opacity-60"
              >

                <Sparkles size={16} />

                Load ALLOW Demo

              </button>


              {/* REAL BLOCK */}

              <button
                type="button"
                onClick={
                  loadVerifiedBlockDemo
                }
                disabled={
                  status === "loading"
                }
                className="inline-flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2.5 text-sm font-semibold text-red-700 transition hover:bg-red-100 disabled:opacity-60"
              >

                <ShieldAlert
                  size={16}
                />

                Load Verified BLOCK

              </button>


              {/* RESET */}

              <button
                type="button"
                onClick={reset}
                className="inline-flex items-center gap-2 px-2 py-2.5 text-sm font-medium text-[#667085] hover:text-[#111827]"
              >

                <RotateCcw size={15} />

                Reset

              </button>

            </div>

          </form>

        </Card>


        {/* ================================================= */}
        {/* RIGHT PANEL */}
        {/* ================================================= */}

        <Card>

          <CardHeader
            title="TRACE Risk Assessment"
            subtitle="Decision → Risk Score → Why?"
          />


          {/* =============================================== */}
          {/* IDLE */}
          {/* =============================================== */}

          {status === "idle" && (
            <NoResultState />
          )}


          {/* =============================================== */}
          {/* LOADING */}
          {/* =============================================== */}

          {status === "loading" && (
            <LoadingState />
          )}


          {/* =============================================== */}
          {/* ERROR */}
          {/* =============================================== */}

          {status === "error" && (
            <ErrorState
              description="TRACE could not complete this analysis. Check the transaction values and try again."
            />
          )}


          {/* =============================================== */}
          {/* RESULT */}
          {/* =============================================== */}

          {status === "done" &&
            result && (

            <div className="space-y-5">

              {/* ------------------------------------------- */}
              {/* FALLBACK DEMO NOTICE */}
              {/* ------------------------------------------- */}

              {analysis.mode === "demo" && (
                <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">

                  <strong>
                    Demo Mode:
                  </strong>{" "}

                  {analysis.error ||
                    "Showing representative demo data."}

                </div>
              )}


              {/* ------------------------------------------- */}
              {/* VALIDATION CASE NOTICE */}
              {/* ------------------------------------------- */}

              {result.source ===
                "validation" && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">

                  <strong>
                    Verified Validation Case
                  </strong>

                  <span className="ml-1">
                    Real fraud transaction
                    from the validation set.
                  </span>

                </div>
              )}


              {/* ------------------------------------------- */}
              {/* DECISION HEADER */}
              {/* ------------------------------------------- */}

              <DecisionHeader
                result={result}
              />


              {/* ------------------------------------------- */}
              {/* WHY */}
              {/* ------------------------------------------- */}

              <div>

                <h3 className="mb-3 text-sm font-semibold text-[#111827]">
                  Why did TRACE decide?
                </h3>


                <div className="space-y-2">

                  {/* Fraud */}

                  <div className="rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] px-4 py-3">

                    <p className="text-sm font-medium text-[#111827]">
                      Fraud Model
                    </p>

                    <p className="mt-1 text-sm text-[#667085]">

                      Fraud probability:{" "}

                      {(
                        result
                          .scores
                          .fraudProbability *
                        100
                      ).toFixed(1)}
                      %

                    </p>

                  </div>


                  {/* Anomaly */}

                  <div className="rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] px-4 py-3">

                    <p className="text-sm font-medium text-[#111827]">
                      Anomaly Check
                    </p>

                    <p className="mt-1 text-sm text-[#667085]">

                      Anomaly score:{" "}

                      {(
                        result
                          .scores
                          .anomalyScore *
                        100
                      ).toFixed(1)}
                      %

                    </p>

                  </div>


                  {/* Entity */}

                  <div className="rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] px-4 py-3">

                    <p className="text-sm font-medium text-[#111827]">
                      Entity Check
                    </p>

                    <p className="mt-1 text-sm text-[#667085]">

                      Entity risk:{" "}

                      {(
                        result
                          .scores
                          .entityRisk *
                        100
                      ).toFixed(1)}
                      %

                    </p>

                  </div>

                </div>

              </div>


              {/* ------------------------------------------- */}
              {/* ACTION LINKS */}
              {/* ------------------------------------------- */}

              <div className="flex flex-wrap gap-3 border-t border-[#EAECF0] pt-4">

                <Link
                  to="/app/investigation"
                  className="inline-flex items-center rounded-lg bg-[#111827] px-4 py-2 text-sm font-semibold text-white hover:bg-[#1F2937]"
                >
                  View Investigation
                </Link>


                <Link
                  to="/app/audit-trail"
                  className="inline-flex items-center rounded-lg border border-[#D0D5DD] bg-white px-4 py-2 text-sm font-semibold text-[#344054] hover:bg-[#F9FAFB]"
                >
                  View Audit
                </Link>

              </div>

            </div>
          )}

        </Card>

      </div>

    </AppLayout>
  );
}