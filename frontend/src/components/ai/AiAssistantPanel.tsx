import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Loader2,
  Send,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { queryAi } from "../../api/ai";
import type { AiQueryResponse } from "../../types/api";
import { formatTitleText } from "../../utils/textFormat";

type AiContext = {
  pageContext: string;
  filters: Record<string, unknown>;
};

const PROMPTS = [
  "Identify the main execution bottlenecks and where to review them.",
  "Which doctors show the strongest ROI signal, and how should I drill into the interpretation?",
  "Which territories are overserved or underserved, and where can I verify the signals?",
  "Explain the current spend split and where to investigate the drivers.",
  "What are the current data quality limitations?",
];

const LOADING_ACTIONS = [
  "planning the evidence path",
  "retrieving dashboard context",
  "checking source-backed signals",
  "validating query scope",
  "assembling the interpretation",
  "mapping results to dashboard sections",
  "grounding the answer",
];

export function AiAssistantPanel({ compactHeader = false, context, openSignal = 0 }: { compactHeader?: boolean; context: AiContext; openSignal?: number }) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AiQueryResponse | null>(null);
  const [loadingAction, setLoadingAction] = useState(LOADING_ACTIONS[0]);
  const mutation = useMutation({
    mutationFn: queryAi,
    onSuccess: (data) => setAnswer(data),
  });

  useEffect(() => {
    if (openSignal > 0) setOpen(true);
  }, [openSignal]);

  useEffect(() => {
    if (!mutation.isPending) {
      setLoadingAction(LOADING_ACTIONS[0]);
      return undefined;
    }
    const interval = window.setInterval(() => {
      setLoadingAction((current) => {
        const nextOptions = LOADING_ACTIONS.filter((action) => action !== current);
        return nextOptions[Math.floor(Math.random() * nextOptions.length)] ?? LOADING_ACTIONS[0];
      });
    }, 950);
    return () => window.clearInterval(interval);
  }, [mutation.isPending]);

  function submit(nextQuestion = question) {
    const trimmed = nextQuestion.trim();
    if (!trimmed || mutation.isPending) return;
    setQuestion(trimmed);
    setOpen(true);
    mutation.mutate({
      question: trimmed,
      pageContext: context.pageContext,
      filters: context.filters,
    });
  }

  return (
    <>
      <button
        type="button"
        className={`ai-drawer-toggle ${open ? "ai-drawer-toggle-open" : ""}`}
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        aria-controls="exec-ai-drawer"
        aria-label={open ? "Close ExecAI" : "Open ExecAI"}
      >
        {open ? <ChevronRight className="h-[1.35rem] w-[1.35rem]" /> : <BrainCircuit className="h-[1.35rem] w-[1.35rem]" />}
        <span className="hidden sm:inline">ExecAI</span>
      </button>

      <div
        className={`ai-drawer-backdrop ${compactHeader ? "ai-drawer-backdrop-compact-header" : ""} ${open ? "opacity-100" : "pointer-events-none opacity-0"}`}
        onClick={() => setOpen(false)}
        aria-hidden="true"
      />

      <aside
        id="exec-ai-drawer"
        className={`ai-drawer ${compactHeader ? "ai-drawer-compact-header" : ""} ${open ? "translate-x-0 opacity-100" : "pointer-events-none translate-x-[calc(100%+1.5rem)] opacity-0"}`}
        aria-hidden={!open}
      >
        <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-l-2xl border border-cyan-200/[0.075] bg-[linear-gradient(145deg,rgba(8,13,18,0.97),rgba(13,22,31,0.97)_48%,rgba(10,24,29,0.97))] shadow-[0_28px_90px_rgba(0,0,0,0.52),0_0_24px_rgba(103,232,249,0.045)] backdrop-blur-2xl">
          <div className="border-b border-cyan-200/[0.055] bg-[linear-gradient(135deg,rgba(14,165,233,0.075),rgba(99,102,241,0.045),rgba(45,212,191,0.055))] p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 text-cyan-200">
                  <Sparkles className="h-4 w-4" />
                  <p className="text-xs font-semibold uppercase tracking-[0.2em]">ExecAI</p>
                </div>
                <h2 className="mt-2 text-lg font-semibold text-cyan-50">Decision Intelligence Copilot</h2>
                <p className="mt-1 text-xs leading-5 text-cyan-300/80">
                  Plans queries, grounds answers in dashboard evidence, and points to verification paths.
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-cyan-200/90" />
                <button
                  type="button"
                  className="soft-button rounded-md p-2"
                  onClick={() => setOpen(false)}
                  aria-label="Close ExecAI"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
            <div className="flex flex-wrap gap-2">
              {PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  className="rounded-full border border-cyan-200/[0.065] bg-cyan-300/[0.038] px-3 py-1.5 text-left text-xs font-medium text-cyan-100/86 shadow-[0_0_0_1px_rgba(255,255,255,0.012)_inset] transition duration-200 hover:border-cyan-200/[0.13] hover:bg-cyan-300/[0.065] hover:text-cyan-50"
                  onClick={() => submit(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>

            <div className="rounded-xl border border-cyan-200/[0.065] bg-[linear-gradient(135deg,rgba(14,165,233,0.038),rgba(255,255,255,0.012))] p-3 shadow-[0_0_0_1px_rgba(255,255,255,0.01)_inset]">
              <label className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200/75" htmlFor="ai-question">
                Ask anything
              </label>
              <textarea
                id="ai-question"
                className="mt-2 min-h-28 w-full resize-y rounded-lg border border-cyan-200/[0.075] bg-[linear-gradient(135deg,rgba(14,165,233,0.06),rgba(99,102,241,0.035),rgba(45,212,191,0.04))] p-3 text-sm text-cyan-50 outline-none transition duration-300 placeholder:text-cyan-100/32 focus:border-cyan-200/30 focus:ring-2 focus:ring-cyan-300/[0.075]"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask about execution risk, workflow bottlenecks, budget gaps, doctor ROI, or data quality..."
              />
              <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-cyan-100/45">Context: {formatTitleText(context.pageContext)}</p>
                <button
                  type="button"
                  className="inline-flex items-center gap-2 rounded-md border border-cyan-200/[0.085] bg-cyan-300/[0.058] px-4 py-2 text-sm font-semibold text-cyan-50 transition duration-200 hover:border-cyan-200/18 hover:bg-cyan-300/[0.09] disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={mutation.isPending || question.trim().length < 3}
                  onClick={() => submit()}
                >
                  {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  Ask
                </button>
              </div>
            </div>

            {mutation.isPending ? (
              <div className="grid min-h-40 place-items-center rounded-xl border border-cyan-200/[0.065] bg-[linear-gradient(135deg,rgba(14,165,233,0.045),rgba(99,102,241,0.028),rgba(45,212,191,0.035))]">
                <div className="flex flex-col items-center gap-3 text-center">
                  <Loader2 className="h-8 w-8 animate-spin text-cyan-200" aria-label="Loading AI answer" />
                  <p className="text-sm font-semibold text-cyan-50">
                    ExecAI is{" "}
                    <span key={loadingAction} className="execai-thinking-action text-cyan-200">
                      {loadingAction}
                    </span>
                  </p>
                </div>
              </div>
            ) : null}

            {mutation.isError ? (
              <div className="rounded-xl border border-red-400/20 bg-red-400/[0.08] p-4 text-sm text-red-100">
                The AI endpoint could not return an answer. Check that the backend is running.
              </div>
            ) : null}

            {answer ? <AiAnswerCard answer={answer} /> : null}
          </div>
        </div>
      </aside>
    </>
  );
}

function AiAnswerCard({ answer }: { answer: AiQueryResponse }) {
  const dashboardPointers = answer.dashboardPointers ?? [];
  const limitations = answer.limitations ?? [];
  const evidenceRefs = answer.evidenceRefs ?? [];
  const agentSteps = answer.agentSteps ?? [];
  const answerMarkdown = answer.answerMarkdown ?? answer.answer;
  const hasUsableAnswer = typeof answerMarkdown === "string" && answerMarkdown.trim().length > 0;
  return (
    <div className="space-y-4 rounded-xl border border-cyan-200/[0.065] bg-[linear-gradient(145deg,rgba(8,15,20,0.92),rgba(12,22,30,0.92))] p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.01)_inset]">
      <div className="flex flex-wrap items-center gap-2">
        <StatusPill answer={answer} />
        <span className="rounded-full border border-cyan-200/[0.06] bg-cyan-300/[0.035] px-2.5 py-1 text-xs text-cyan-100/70">
          Confidence: {answer.confidence}
        </span>
        {answer.redactionApplied ? (
          <span className="rounded-full border border-cyan-300/15 bg-cyan-300/[0.07] px-2.5 py-1 text-xs text-cyan-200">
            Redacted
          </span>
        ) : null}
      </div>
      {hasUsableAnswer ? (
        <div className="ai-markdown text-sm leading-6 text-zinc-200">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{answerMarkdown}</ReactMarkdown>
        </div>
      ) : (
        <div className="rounded-lg border border-red-400/20 bg-red-400/[0.08] p-3 text-sm text-red-100">
          AI response was incomplete. Restart the backend if dashboard pointers are missing repeatedly.
        </div>
      )}
      {evidenceRefs.length ? (
        <InsightDropdown title="Evidence used" count={evidenceRefs.length}>
          <div className="grid grid-cols-1 gap-2">
            {evidenceRefs.slice(0, 8).map((ref, index) => (
              <div key={`${ref.section}-${ref.label}-${index}`} className="rounded-lg border border-cyan-300/[0.06] bg-cyan-300/[0.03] p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-cyan-300/[0.08] bg-cyan-300/[0.045] px-2 py-0.5 text-[0.68rem] font-semibold uppercase tracking-wide text-cyan-200">
                    {ref.section}
                  </span>
                  <p className="text-xs font-semibold text-zinc-100">{ref.label}</p>
                </div>
                {ref.value !== null && ref.value !== undefined ? (
                  <p className="mt-2 text-xs text-zinc-300">Value: {String(ref.value)}</p>
                ) : null}
              </div>
            ))}
          </div>
        </InsightDropdown>
      ) : null}
      {dashboardPointers.length ? (
        <InsightDropdown title="Where to verify this" count={dashboardPointers.length}>
          <div className="grid grid-cols-1 gap-2">
            {dashboardPointers.slice(0, 10).map((pointer) => (
              <div key={`${pointer.page}-${pointer.section}-${pointer.detail}`} className="rounded-lg border border-cyan-200/[0.055] bg-black/20 p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-cyan-300/[0.08] bg-cyan-300/[0.045] px-2 py-0.5 text-[0.68rem] font-semibold uppercase tracking-wide text-cyan-200">
                    {pointer.page}
                  </span>
                  <p className="text-xs font-semibold text-zinc-200">{pointer.section}</p>
                </div>
                <p className="mt-2 text-xs leading-5 text-zinc-400">{pointer.detail}</p>
                <p className="mt-2 text-[0.68rem] leading-5 text-zinc-600">{pointer.reason}</p>
              </div>
            ))}
          </div>
        </InsightDropdown>
      ) : null}
      {!dashboardPointers.length && hasUsableAnswer ? (
        <div className="rounded-lg border border-cyan-300/15 bg-cyan-300/[0.06] p-3 text-xs leading-5 text-cyan-100/80">
          Restart backend if dashboard pointers are missing repeatedly.
        </div>
      ) : null}
      {agentSteps.length ? (
        <div className="rounded-lg border border-cyan-300/[0.08] bg-cyan-300/[0.04] p-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-cyan-100">
            <ShieldCheck className="h-4 w-4" />
            ExecAI evidence workflow
          </div>
          <ol className="mt-2 space-y-1 text-xs leading-5 text-cyan-100/75">
            {agentSteps.map((step) => (
              <li key={step.step} className="flex gap-2">
                <span className={step.status === "fallback" ? "text-amber-200" : "text-emerald-200"}>
                  {step.status === "fallback" ? "Fallback" : "Done"}
                </span>
                <span>{step.step}</span>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
      {limitations.length ? (
        <div className="rounded-lg border border-amber-300/20 bg-amber-300/[0.07] p-3 text-xs text-amber-100/80">
          <div className="flex items-center gap-2 font-semibold">
            <AlertTriangle className="h-4 w-4" />
            Limitations
          </div>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {limitations.slice(0, 5).map((limitation) => (
              <li key={limitation}>{limitation}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

function InsightDropdown({ children, count, title }: { children: ReactNode; count: number; title: string }) {
  return (
    <details className="group rounded-lg border border-cyan-200/[0.105] bg-[linear-gradient(135deg,rgba(14,165,233,0.07),rgba(99,102,241,0.038),rgba(45,212,191,0.048))] shadow-[0_0_18px_rgba(103,232,249,0.04)]">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 p-3 marker:hidden">
        <div className="flex min-w-0 items-center gap-2">
          <Sparkles className="h-4 w-4 shrink-0 text-cyan-200" />
          <span className="truncate text-xs font-semibold uppercase tracking-wide text-cyan-50">{title}</span>
          <span className="rounded-full border border-cyan-200/12 bg-cyan-300/[0.07] px-2 py-0.5 text-[0.65rem] text-cyan-100/80">{count}</span>
        </div>
        <ChevronRight className="execai-dropdown-icon h-4 w-4 shrink-0 text-cyan-200/85 transition-transform duration-200" />
      </summary>
      <div className="border-t border-cyan-200/[0.06] px-3 pb-3 pt-2">
        {children}
      </div>
    </details>
  );
}

function StatusPill({ answer }: { answer: AiQueryResponse }) {
  if (answer.fallbackUsed) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full border border-amber-300/20 bg-amber-300/[0.07] px-2.5 py-1 text-xs text-amber-100">
        <Bot className="h-3.5 w-3.5" />
        Safe fallback
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-emerald-300/20 bg-emerald-300/[0.07] px-2.5 py-1 text-xs text-emerald-100">
      <CheckCircle2 className="h-3.5 w-3.5" />
      {answer.providerUsed} {answer.modelUsed ? `/${answer.modelUsed}` : ""}
    </span>
  );
}
