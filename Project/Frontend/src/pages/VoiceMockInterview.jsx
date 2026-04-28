import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { FaChevronLeft, FaMicrophone, FaRobot, FaShieldAlt, FaUser } from "react-icons/fa";
import VapiButton from "../components/VapiButton";

// ─── helpers ────────────────────────────────────────────────────────────────

/** Generate a stable key for list rendering */
let _keySeq = 0;
const nextKey = () => `t-${++_keySeq}`;

// ─── TranscriptPanel ─────────────────────────────────────────────────────────

function TranscriptPanel({ messages, liveMessage }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, liveMessage]);

  const hasContent = messages.length > 0 || liveMessage;

  return (
    <div
      className="flex flex-col rounded-2xl border overflow-hidden"
      style={{ borderColor: "var(--color-border)", backgroundColor: "rgba(255,255,255,0.02)" }}
    >
      {/* header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b text-xs font-semibold uppercase tracking-widest"
        style={{ borderColor: "var(--color-border)", color: "var(--color-subtext)" }}
      >
        <span>Live Transcript</span>
        {hasContent && (
          <span
            className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px]"
            style={{ backgroundColor: "rgba(59,130,246,0.15)", color: "#93c5fd" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" />
            live
          </span>
        )}
      </div>

      {/* body */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 max-h-80 min-h-[120px]">
        {!hasContent ? (
          <p className="text-sm text-center py-6" style={{ color: "var(--color-subtext)" }}>
            Transcript will appear here once the call starts.
          </p>
        ) : (
          <>
            {messages.map((m) => (
              <Bubble key={m.id} role={m.role} text={m.text} partial={false} />
            ))}
            {liveMessage && (
              <Bubble role={liveMessage.role} text={liveMessage.text} partial />
            )}
          </>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

function Bubble({ role, text, partial }) {
  const isUser = role === "user";
  return (
    <div className={`flex items-start gap-2 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* avatar */}
      <div
        className="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[11px]"
        style={{
          backgroundColor: isUser ? "rgba(59,130,246,0.2)" : "rgba(139,92,246,0.2)",
          color: isUser ? "#93c5fd" : "#c4b5fd",
        }}
      >
        {isUser ? <FaUser className="w-3 h-3" /> : <FaRobot className="w-3 h-3" />}
      </div>

      {/* bubble */}
      <div
        className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed ${
          isUser ? "rounded-tr-sm" : "rounded-tl-sm"
        }`}
        style={{
          backgroundColor: isUser ? "rgba(59,130,246,0.12)" : "rgba(139,92,246,0.10)",
          color: "#e2e8f0",
          border: "1px solid",
          borderColor: isUser ? "rgba(59,130,246,0.25)" : "rgba(139,92,246,0.20)",
          opacity: partial ? 0.7 : 1,
          fontStyle: partial ? "italic" : "normal",
        }}
      >
        {text}
        {partial && (
          <span className="inline-flex gap-0.5 ml-1.5 align-middle">
            <span className="w-1 h-1 rounded-full bg-current animate-bounce [animation-delay:-0.3s]" />
            <span className="w-1 h-1 rounded-full bg-current animate-bounce [animation-delay:-0.15s]" />
            <span className="w-1 h-1 rounded-full bg-current animate-bounce" />
          </span>
        )}
      </div>
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function VoiceMockInterview() {
  const [messages,    setMessages]    = useState([]);   // finalized turns
  const [liveMessage, setLiveMessage] = useState(null); // current partial

  // Called by VapiButton on every transcript event
  const handleTranscript = useCallback((role, text, isFinal) => {
    if (isFinal) {
      // Commit the final text as a new message bubble
      setMessages((prev) => [...prev, { id: nextKey(), role, text }]);
      // Clear live bubble only if it belongs to this role
      setLiveMessage((prev) => (prev?.role === role ? null : prev));
    } else {
      // Update live bubble for this role
      setLiveMessage({ role, text });
    }
  }, []);

  const handleCallEnd = useCallback(() => {
    // Small delay so the last final transcript has time to arrive
    setTimeout(() => {
      setMessages([]);
      setLiveMessage(null);
    }, 300);
  }, []);

  return (
    <div
      className="min-h-screen pb-8"
      style={{
        background: "radial-gradient(circle at top, rgba(59, 130, 246, 0.22), transparent 38%), var(--color-bg)",
        color: "var(--color-text)",
      }}
    >
      {/* ── top bar ── */}
      <div
        className="mb-6 flex items-center justify-between gap-4 rounded-3xl border px-5 py-4 md:px-6"
        style={{ borderColor: "var(--color-border)", backgroundColor: "rgba(26, 29, 35, 0.86)" }}
      >
        <div>
          <p className="text-xs uppercase tracking-[0.24em]" style={{ color: "var(--color-subtext)" }}>
            Mock Interview
          </p>
          <h1 className="mt-1 text-2xl font-semibold">Voice Interview Room</h1>
          <p className="mt-1 text-sm" style={{ color: "var(--color-subtext)" }}>
            Real-time transcript appears below as you speak.
          </p>
        </div>

        <Link
          to="/mock-interview"
          className="inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition"
          style={{ borderColor: "var(--color-border)", color: "var(--color-text)", backgroundColor: "rgba(255,255,255,0.03)" }}
        >
          <FaChevronLeft className="h-3.5 w-3.5" />
          Back
        </Link>
      </div>

      {/* ── main card ── */}
      <div
        className="rounded-3xl border p-4 md:p-6"
        style={{ borderColor: "var(--color-border)", backgroundColor: "rgba(15, 17, 21, 0.88)" }}
      >
        {/* badges */}
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <div
            className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium"
            style={{ backgroundColor: "rgba(59,130,246,0.14)", color: "#bfdbfe" }}
          >
            <FaMicrophone className="h-3.5 w-3.5" />
            Embedded voice mode
          </div>
          <div
            className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium"
            style={{ backgroundColor: "rgba(16,185,129,0.12)", color: "#a7f3d0" }}
          >
            <FaShieldAlt className="h-3.5 w-3.5" />
            Microphone access required
          </div>
        </div>

        <div
          className="overflow-hidden rounded-2xl border"
          style={{ borderColor: "var(--color-border)", backgroundColor: "#05070c" }}
        >
          <div className="flex flex-col gap-6 px-5 py-8 md:px-8 md:py-10">

            {/* ── call controls row ── */}
            <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr] lg:items-start">
              <div className="space-y-3">
                <p className="text-sm uppercase tracking-[0.22em]" style={{ color: "var(--color-subtext)" }}>
                  Voice mode
                </p>
                <h2 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
                  Speak naturally with the interview assistant.
                </h2>
                <p className="text-sm leading-6" style={{ color: "var(--color-subtext)" }}>
                  Start the call below. Both your words and the assistant's replies will appear in real time beneath the controls.
                </p>
              </div>

              <div
                className="rounded-3xl border p-5"
                style={{ borderColor: "var(--color-border)", backgroundColor: "rgba(255,255,255,0.02)" }}
              >
                <div className="mb-4 flex items-center gap-2 text-sm font-medium text-white">
                  <FaMicrophone className="h-4 w-4 text-sky-300" />
                  Voice call controls
                </div>
                <VapiButton
                  onTranscript={handleTranscript}
                  onCallEnd={handleCallEnd}
                />
              </div>
            </div>

            {/* ── live transcript panel ── */}
            <TranscriptPanel messages={messages} liveMessage={liveMessage} />

            {/* ── back link ── */}
            <div className="flex justify-start">
              <Link
                to="/mock-interview"
                className="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-medium"
                style={{ borderColor: "var(--color-border)", color: "var(--color-text)" }}
              >
                Back
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
