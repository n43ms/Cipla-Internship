import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  ChevronRight,
  Loader2,
  MessageCircle,
  Send,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { queryAi } from "../../api/ai";
import type { AiQueryResponse } from "../../types/api";

type AiContext = {
  pageContext: string;
  filters: Record<string, unknown>;
};

const PROMPTS = [
  "Where is execution risk highest?",
  "Explain this doctor's sponsorship, FMV, and RCPA evidence.",
  "Which territory signals are underserved or overserved?",
  "Where do no-fee or paid engagements affect Doctor ROI?",
  "What data-quality limitations should I mention?",
];

export function AiAssistantPanel({ context }: { context: AiContext }) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AiQueryResponse | null>(null);
  const mutation = useMutation({
    mutationFn: queryAi,
    onSuccess: (data) => setAnswer(data),
  });

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
        {open ? <ChevronRight className="h-5 w-5" /> : <MessageCircle className="h-5 w-5" />}
        <span className="hidden sm:inline">ExecAI</span>
      </button>

      <div
        className={`ai-drawer-backdrop ${open ? "opacity-100" : "pointer-events-none opacity-0"}`}
        onClick={() => setOpen(false)}
        aria-hidden="true"
      />

      <aside
        id="exec-ai-drawer"
        className={`ai-drawer ${open ? "translate-x-0 opacity-100" : "pointer-events-none translate-x-[calc(100%+1.5rem)] opacity-0"}`}
        aria-hidden={!open}
      >
        <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-l-2xl border border-white/[0.1] bg-[#0b0e10]/95 shadow-[0_28px_90px_rgba(0,0,0,0.52)] backdrop-blur-2xl">
          <div className="border-b border-white/[0.08] bg-white/[0.035] p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 text-accent">
                  <Sparkles className="h-4 w-4" />
                  <p className="text-xs font-semibold uppercase tracking-[0.2em]">ExecAI</p>
                </div>
                <h2 className="mt-2 text-lg font-semibold text-zinc-100">Ask the dashboard</h2>
                <p className="mt-1 text-xs leading-5 text-zinc-500">
                  Structured RAG assistant: plans the question, retrieves FastAPI/PostgreSQL evidence, asks Gemini to synthesize it, then validates the answer against available data.
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-cyan-300/80" />
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
                  className="soft-button rounded-full px-3 py-1.5 text-xs"
                  onClick={() => submit(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-black/20 p-3">
              <label className="text-xs font-medium uppercase tracking-wide text-zinc-500" htmlFor="ai-question">
                Business question
              </label>
              <textarea
                id="ai-question"
                className="mt-2 min-h-28 w-full resize-y rounded-lg border border-[#303437] bg-[#0f1113] p-3 text-sm text-zinc-100 outline-none transition duration-300 placeholder:text-zinc-600 focus:border-accent/60 focus:ring-2 focus:ring-accent/10"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask about execution risk, workflow bottlenecks, budget gaps, doctor ROI, or data quality..."
              />
              <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-zinc-500">Context: {context.pageContext.replaceAll("_", " ")}</p>
                <button
                  type="button"
                  className="soft-button inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={mutation.isPending || question.trim().length < 3}
                  onClick={() => submit()}
                >
                  {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  Ask
                </button>
              </div>
            </div>

            {mutation.isPending ? (
              <div className="grid min-h-40 place-items-center rounded-xl border border-white/[0.08] bg-white/[0.025]">
                <Loader2 className="h-8 w-8 animate-spin text-accent" aria-label="Loading AI answer" />
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
    <div className="space-y-4 rounded-xl border border-white/[0.08] bg-[#101315] p-4">
      <div className="flex flex-wrap items-center gap-2">
        <StatusPill answer={answer} />
        <span className="rounded-full border border-white/[0.08] bg-white/[0.035] px-2.5 py-1 text-xs text-zinc-400">
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
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Evidence used</h3>
          <div className="mt-2 grid grid-cols-1 gap-2">
            {evidenceRefs.slice(0, 8).map((ref, index) => (
              <div key={`${ref.section}-${ref.label}-${index}`} className="rounded-lg border border-emerald-300/10 bg-emerald-300/[0.045] p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-emerald-300/15 bg-emerald-300/[0.07] px-2 py-0.5 text-[0.68rem] font-semibold uppercase tracking-wide text-emerald-200">
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
        </div>
      ) : null}
      {agentSteps.length ? (
        <div className="rounded-lg border border-cyan-300/15 bg-cyan-300/[0.055] p-3">
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
      {dashboardPointers.length ? (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Where to verify this</h3>
          <div className="mt-2 grid grid-cols-1 gap-2">
            {dashboardPointers.slice(0, 10).map((pointer) => (
              <div key={`${pointer.page}-${pointer.section}-${pointer.detail}`} className="rounded-lg border border-white/[0.08] bg-black/20 p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-accent/20 bg-accent/[0.08] px-2 py-0.5 text-[0.68rem] font-semibold uppercase tracking-wide text-accent">
                    {pointer.page}
                  </span>
                  <p className="text-xs font-semibold text-zinc-200">{pointer.section}</p>
                </div>
                <p className="mt-2 text-xs leading-5 text-zinc-400">{pointer.detail}</p>
                <p className="mt-2 text-[0.68rem] leading-5 text-zinc-600">{pointer.reason}</p>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {!dashboardPointers.length && hasUsableAnswer ? (
        <div className="rounded-lg border border-cyan-300/15 bg-cyan-300/[0.06] p-3 text-xs leading-5 text-cyan-100/80">
          Restart backend if dashboard pointers are missing repeatedly.
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
