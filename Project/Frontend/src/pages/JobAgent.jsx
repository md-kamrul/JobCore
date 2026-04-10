import React, { useState, useContext, useRef, useEffect } from "react";
import { getResumeCheckerRecommendation } from "../components/ResumeCheckerAgent";
import ProgressiveJobMessages from "../components/ProgressiveJobMessages";
import { AuthContext } from "../provider/AuthProvider";

// ─── CheckboxPrompt ──────────────────────────────────────────────────────────
// Renders an inline multi-select UI when the form question is a checkbox type.
const CheckboxPrompt = ({ question, onSubmit }) => {
  const [selected, setSelected] = useState([]);

  const toggle = (opt) => {
    setSelected((prev) =>
      prev.includes(opt) ? prev.filter((o) => o !== opt) : [...prev, opt]
    );
  };

  const handleConfirm = () => {
    if (selected.length === 0) return;
    onSubmit(selected);
  };

  return (
    <div className="mt-2 space-y-2">
      <p className="text-xs text-gray-400 mb-1">Select one or more options:</p>
      <div className="flex flex-wrap gap-2">
        {question.options.map((opt, i) => (
          <button
            key={i}
            type="button"
            onClick={() => toggle(opt)}
            className={`px-3 py-1.5 rounded-full text-sm border transition-all ${
              selected.includes(opt)
                ? "bg-blue-600 border-blue-500 text-white"
                : "bg-[#0d1117] border-gray-600 text-gray-300 hover:border-blue-400"
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
      {selected.length > 0 && (
        <button
          type="button"
          onClick={handleConfirm}
          className="mt-2 px-4 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-semibold transition"
        >
          ✅ Confirm ({selected.length} selected)
        </button>
      )}
    </div>
  );
};

const JobAgent = () => {
  const { user } = useContext(AuthContext);
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hi there! 👋 How can I help you find a job today?" },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [allJobMessages, setAllJobMessages] = useState([]);
  // pendingApplication: { applicationId, missing: [], awaitingCheckbox: bool }
  const [pendingApplication, setPendingApplication] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const describeQuestionType = (inputType) => {
    const t = (inputType || "").toLowerCase();
    switch (t) {
      case "text": return "Short answer";
      case "email": return "Email";
      case "textarea": return "Paragraph";
      case "radio": return "Multiple choice (radio)";
      case "checkbox": return "Checkboxes (multiple select)";
      case "dropdown": return "Dropdown";
      case "file": return "File upload";
      default: return t ? `Unknown (${t})` : "Unknown";
    }
  };

  const buildNeedsInfoPrompt = (missing) => {
    if (!Array.isArray(missing) || missing.length === 0) return "";
    const q = missing[0] || {};
    const label = (q.label || "").trim() || "(Untitled question)";
    const required = Boolean(q.required);
    const typeLine = `Type: ${describeQuestionType(q.input_type)}`;
    const options = Array.isArray(q.options)
      ? q.options.map((o) => String(o || "").trim()).filter(Boolean)
      : [];

    let msg = `${label}${required ? " (required)" : ""}\n${typeLine}`;
    if (options.length > 0) {
      msg += `\nOptions:\n${options.slice(0, 50).map((o, i) => `${i + 1}. ${o}`).join("\n")}`;
      if ((q.input_type || "").toLowerCase() === "checkbox") {
        msg += "\n\nThis is a multi-select question. You can select multiple options below.";
      } else {
        msg += "\n\nReply with the option number (e.g. 1) or the option text.";
      }
    }
    if ((q.input_type || "").toLowerCase() === "file") {
      msg += "\nPlease send a local file path to upload.";
    }
    return msg;
  };

  const normalizeOption = (value) => String(value || "").trim().toLowerCase();

  const resolveSingleOption = (options, rawInput) => {
    const input = String(rawInput || "").trim();
    if (!input) return null;

    const numMatch = input.match(/\b(\d{1,3})\b/);
    if (numMatch) {
      const idx = Number(numMatch[1]);
      if (Number.isInteger(idx) && idx >= 1 && idx <= options.length) {
        return options[idx - 1];
      }
    }

    const exact = options.find((o) => normalizeOption(o) === normalizeOption(input));
    if (exact) return exact;

    const inputNorm = normalizeOption(input);
    const containsMatches = options.filter((o) => {
      const optNorm = normalizeOption(o);
      return optNorm.includes(inputNorm) || inputNorm.includes(optNorm);
    });
    if (containsMatches.length === 1) return containsMatches[0];

    return null;
  };

  const resolveMultiOptions = (options, rawInput) => {
    const tokens = String(rawInput)
      .split(/[,;/\n]+/)
      .map((t) => t.trim())
      .filter(Boolean);

    const selected = [];
    const invalidTokens = [];

    for (const token of tokens) {
      const resolved = resolveSingleOption(options, token);
      if (!resolved) {
        invalidTokens.push(token);
        continue;
      }
      if (!selected.includes(resolved)) {
        selected.push(resolved);
      }
    }

    return { selected, invalidTokens };
  };

  const buildUserProfileForApply = () => {
    const stored = (() => {
      try { return JSON.parse(localStorage.getItem("jobcore_profile") || "null"); }
      catch { return null; }
    })();
    return {
      ...(stored || {}),
      email: stored?.email || user?.email || "",
      name: stored?.name || user?.displayName || "",
    };
  };

  // ── Shared helper: process a /api/apply/continue or /api/apply/start response ──
  const handleApplyResponse = (applyData) => {
    if (!applyData?.success) {
      setMessages((prev) => [...prev, { sender: "ai", text: `❌ ${applyData?.message || "Auto-apply failed."}` }]);
      setPendingApplication(null);
      return;
    }

    const missing = applyData?.missing || [];
    const firstQ = missing[0] || null;
    const isCheckbox = (firstQ?.input_type || "").toLowerCase() === "checkbox";

    if (applyData?.status === "needs_info") {
      const prompt = buildNeedsInfoPrompt(missing);
      setMessages((prev) => [...prev, {
        sender: "ai",
        text: prompt || applyData.message,
        // Attach checkbox metadata so the renderer can show a multi-select UI
        checkboxQuestion: isCheckbox ? firstQ : null,
        applicationId: applyData.applicationId,
      }]);
      setPendingApplication({
        applicationId: applyData.applicationId,
        missing,
        awaitingCheckbox: isCheckbox,
      });
    } else {
      setMessages((prev) => [...prev, { sender: "ai", text: applyData.message }]);
      setPendingApplication(null);
    }
  };

  // ── Called when user taps "Confirm" on a multi-select checkbox prompt ──
  const handleCheckboxConfirm = async (selectedOptions) => {
    if (!pendingApplication?.applicationId) return;

    // Show user's selection as a chat bubble
    const selectionText = selectedOptions.join(", ");
    setMessages((prev) => [...prev, { sender: "user", text: selectionText }]);
    setIsTyping(true);

    const currentQ = (pendingApplication.missing || [])[0];
    const label = currentQ?.label;
    // Send the array directly; api.py will join them into a comma-separated string
    const answers = label ? { [label]: selectedOptions } : { default: selectedOptions };

    try {
      const resp = await fetch("http://localhost:5001/api/apply/continue", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ applicationId: pendingApplication.applicationId, answers, headless: false }),
      });
      const data = await resp.json();
      handleApplyResponse(data);
    } catch {
      setMessages((prev) => [...prev, { sender: "ai", text: "❌ Unable to continue the auto-apply right now. Please try again." }]);
      setPendingApplication(null);
    } finally {
      setIsTyping(false);
    }
  };

  const handleApplyClick = async (job) => {
    const detailsUrl = job?.url;
    if (!detailsUrl) return;

    const placeholderId = `${Date.now()}-${Math.random()}`;
    setMessages((prev) => [...prev, { id: placeholderId, sender: "ai", text: "🔗 Finding the application link..." }]);

    try {
      const response = await fetch("http://localhost:5001/api/extract-apply-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ detailsUrl }),
      });
      const data = await response.json();
      const messageText = data && data.success
        ? data.message
        : `❌ Error: ${data?.message || "Could not extract the apply link."}`;

      setMessages((prev) => prev.map((m) => (m.id === placeholderId ? { ...m, text: messageText } : m)));

      if (data?.success && data?.applyUrl && data?.isGoogleForm) {
        setMessages((prev) => [...prev, { sender: "ai", text: "I am starting to apply the job. Please bear with me..." }]);
        const profile = buildUserProfileForApply();
        const applyResp = await fetch("http://localhost:5001/api/apply/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ applyUrl: data.applyUrl, profile, headless: false }),
        });
        const applyData = await applyResp.json();
        handleApplyResponse(applyData);
      }
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === placeholderId
            ? { ...m, text: "❌ Unable to extract the apply link right now. Please try again." }
            : m
        )
      );
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMessage = { sender: "user", text: input };
    const userQuery = input;
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    // Mid-application: treat text input as an answer to the pending question
    if (pendingApplication?.applicationId) {
      try {
        const missing = pendingApplication.missing || [];
        const first = missing[0];
        const label = first?.label;

        const inputType = (first?.input_type || "").toLowerCase();
        let answerValue = userQuery;
        const options = Array.isArray(first?.options) ? first.options : [];

        const sendInvalidPrompt = () => {
          const prompt = buildNeedsInfoPrompt(missing);
          const invalidText = `Invalid option!!!${prompt ? `\n${prompt}` : ""}`;
          setMessages((prev) => [...prev, { sender: "ai", text: invalidText }]);
          setIsTyping(false);
        };

        if (options.length > 0 && ["radio", "dropdown", "checkbox"].includes(inputType)) {
          if (inputType === "checkbox") {
            const { selected, invalidTokens } = resolveMultiOptions(options, userQuery);
            if (invalidTokens.length > 0 || selected.length === 0) {
              sendInvalidPrompt();
              return;
            }
            answerValue = selected;
          } else {
            const resolved = resolveSingleOption(options, userQuery);
            if (!resolved) {
              sendInvalidPrompt();
              return;
            }
            answerValue = resolved;
          }
        }

        // If it's a checkbox (multi-select), allow users to type: "1, 3" or "Option A; Option B".
        if (inputType === "checkbox") {
          // Backend will join arrays; keep as array to preserve multi-select intent.
          if (!Array.isArray(answerValue)) {
            const { selected } = resolveMultiOptions(options, userQuery);
            answerValue = selected.length > 0 ? selected : userQuery;
          }
        }

        const answers = label ? { [label]: answerValue } : { default: answerValue };

        const resp = await fetch("http://localhost:5001/api/apply/continue", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ applicationId: pendingApplication.applicationId, answers, headless: false }),
        });
        const data = await resp.json();
        handleApplyResponse(data);
      } catch {
        setMessages((prev) => [...prev, { sender: "ai", text: "❌ Unable to continue the auto-apply right now. Please try again." }]);
        setPendingApplication(null);
      } finally {
        setIsTyping(false);
      }
      return;
    }

    // Normal chat / job search flow
    setMessages((prev) => [...prev, { sender: "ai", text: "🤔 Understanding your query..." }]);

    try {
      const recommendation = getResumeCheckerRecommendation(userQuery);
      if (recommendation) {
        await new Promise((resolve) => setTimeout(resolve, 800));
        setMessages((prev) => { const n = prev.slice(0, -1); return [...n, { sender: "ai", text: recommendation }]; });
        setIsTyping(false);
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 800));
      setMessages((prev) => {
        const n = prev.slice(0, -1);
        return [...n, {
          sender: "ai",
          text: `🔍 Searching for "${userQuery}"...\n\nThis may take 30-60 seconds as I:\n1. Understand your requirements\n2. Generate search criteria\n3. Find relevant jobs\n4. Format results`,
        }];
      });

      const response = await fetch("http://localhost:5001/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userQuery }),
      });
      const data = await response.json();

      if (data.success) {
        if (Array.isArray(data.message)) {
          setMessages((prev) => {
            const n = prev.slice(0, -1);
            return [...n, { sender: "ai", text: `Job results for "${userQuery}":`, jobIndex: allJobMessages.length }];
          });
          setAllJobMessages((prev) => [...prev, data.message]);
        } else {
          setMessages((prev) => { const n = prev.slice(0, -1); return [...n, { sender: "ai", text: data.message }]; });
        }
      } else {
        setMessages((prev) => [...prev, { sender: "ai", text: `❌ Error: ${data.message || "Something went wrong. Please try again."}` }]);
      }
    } catch {
      setMessages((prev) => [...prev, { sender: "ai", text: "❌ Unable to connect to the job search service. Please make sure the backend server is running and try again." }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0d1117] text-white">
      <main className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => {
          if (msg.jobIndex !== undefined) {
            return (
              <div key={index}>
                <div className="flex justify-start">
                  <div className="max-w-[90%] break-normal whitespace-pre-line p-4 rounded-2xl bg-[#161b22] text-gray-200 rounded-bl-none">
                    {msg.text}
                  </div>
                </div>
                <ProgressiveJobMessages jobMessages={allJobMessages[msg.jobIndex]} onApply={handleApplyClick} />
              </div>
            );
          }

          return (
            <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[90%] break-normal whitespace-pre-line p-4 rounded-2xl ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-[#161b22] text-gray-200 rounded-bl-none"
                }`}
              >
                {msg.text}
                {/* Render multi-select checkbox UI if this message is a checkbox prompt */}
                {msg.checkboxQuestion &&
                  msg.checkboxQuestion.options?.length > 0 &&
                  // Only show the interactive UI for the latest pending checkbox question
                  pendingApplication?.awaitingCheckbox &&
                  pendingApplication?.applicationId === msg.applicationId && (
                    <CheckboxPrompt
                      question={msg.checkboxQuestion}
                      onSubmit={handleCheckboxConfirm}
                    />
                  )}
              </div>
            </div>
          );
        })}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-[#161b22] text-gray-400 px-4 py-2 rounded-2xl flex items-center gap-2 rounded-bl-none">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
              <span className="text-sm ml-2">JobCore AI is typing...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </main>

      <form
        onSubmit={handleSend}
        className="p-4 bg-[#161b22] flex items-center gap-2 border-t border-gray-700"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            pendingApplication?.awaitingCheckbox
              ? "Select options above, or type manually (e.g. 1, 3)..."
              : "Type your message..."
          }
          className="flex-1 px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default JobAgent;
