import { useEffect, useRef, useState } from "react";
import Vapi from "@vapi-ai/web";
import { FaMicrophone, FaPhoneSlash, FaSpinner } from "react-icons/fa";

/**
 * VapiButton
 *
 * Props
 * ─────
 * onCallStart()                          – fired when the call goes live
 * onCallEnd()                            – fired when the call ends
 * onTranscript(role, text, isFinal)      – fired on every transcript event
 *   role    : "user" | "assistant"
 *   text    : string
 *   isFinal : boolean
 */
export default function VapiButton({ onCallStart, onCallEnd, onTranscript }) {
  const vapiRef   = useRef(null);
  const [connected,  setConnected]  = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [isReady,    setIsReady]    = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const publicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY;

    if (!publicKey) {
      setErrorMessage("Add VITE_VAPI_PUBLIC_KEY to enable voice calls.");
      setIsReady(false);
      return undefined;
    }

    const vapi = new Vapi(publicKey);
    vapiRef.current = vapi;
    setIsReady(true);
    setErrorMessage("");

    vapi.on("call-start", () => {
      setConnecting(false);
      setConnected(true);
      onCallStart?.();
    });

    vapi.on("call-end", () => {
      setConnecting(false);
      setConnected(false);
      onCallEnd?.();
    });

    vapi.on("error", (event) => {
      console.error("Vapi error:", event);
      setErrorMessage("The voice agent could not start. Check your Vapi credentials.");
      setConnecting(false);
      setConnected(false);
    });

    // Real-time transcript events
    vapi.on("message", (msg) => {
      if (msg?.type !== "transcript") return;
      const role    = msg.role;          // "user" | "assistant"
      const text    = msg.transcript;
      const isFinal = msg.transcriptType === "final";
      onTranscript?.(role, text, isFinal);
    });

    return () => {
      vapi.stop();
      vapiRef.current = null;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const start = () => {
    const assistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID;
    if (!assistantId) {
      setErrorMessage("Add VITE_VAPI_ASSISTANT_ID to start the assistant.");
      return;
    }
    setErrorMessage("");
    setConnecting(true);
    vapiRef.current?.start(assistantId);
  };

  const stop = () => {
    vapiRef.current?.stop();
    setConnecting(false);
  };

  return (
    <div className="flex w-full flex-col items-center gap-3">
      <button
        type="button"
        onClick={connected ? stop : start}
        disabled={(!isReady && !connected) || connecting}
        className="inline-flex min-w-[220px] items-center justify-center gap-2 rounded-full px-6 py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60"
        style={{
          backgroundColor: connected
            ? "rgba(239, 68, 68, 0.18)"
            : connecting
            ? "rgba(234, 179, 8, 0.18)"
            : "var(--color-accent)",
          color: "#fff",
          boxShadow: connected
            ? "inset 0 0 0 1px rgba(248, 113, 113, 0.35)"
            : connecting
            ? "inset 0 0 0 1px rgba(234, 179, 8, 0.35)"
            : "none",
        }}
      >
        {connecting ? (
          <FaSpinner className="h-4 w-4 animate-spin" />
        ) : connected ? (
          <FaPhoneSlash className="h-4 w-4" />
        ) : (
          <FaMicrophone className="h-4 w-4" />
        )}
        {connecting ? "Connecting…" : connected ? "End call" : "Talk to assistant"}
      </button>

      <p className="flex items-center gap-2 text-sm" style={{ color: "var(--color-subtext)" }}>
        {!isReady && !connecting ? <FaSpinner className="h-3.5 w-3.5 animate-spin" /> : null}
        <span>
          {connected
            ? "🟢 Voice assistant is live."
            : connecting
            ? "Connecting to voice assistant…"
            : errorMessage || "Press the button above to start the voice interview."}
        </span>
      </p>
    </div>
  );
}
