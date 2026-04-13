import React, { useState, useContext, useRef, useEffect } from "react";
import { getResumeCheckerRecommendation } from "../components/ResumeCheckerAgent";
import ProgressiveJobMessages from "../components/ProgressiveJobMessages";
import { AuthContext } from "../provider/AuthProvider";
import { getProfile, getWorkExperience, getEducation } from "../lib/profileService";

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

// ─── ConfirmPrompt ─────────────────────────────────────────────────────────
// Confirms a suggested answer from the user profile before auto-filling.
const ConfirmPrompt = ({ suggestedAnswer, onConfirm, onEdit }) => (
  <div className="mt-3 space-y-2">
    {suggestedAnswer && (
      <div className="text-xs text-gray-300 bg-[#0d1117] border border-gray-700 rounded-lg px-3 py-2">
        Suggested: <span className="text-gray-100">{String(suggestedAnswer)}</span>
      </div>
    )}
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={onConfirm}
        className="px-4 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-semibold transition"
      >
        Confirm
      </button>
      <button
        type="button"
        onClick={onEdit}
        className="px-4 py-1.5 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-semibold transition"
      >
        Edit
      </button>
    </div>
  </div>
);

const JobAgent = () => {
  const { user } = useContext(AuthContext);
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hi there! 👋 How can I help you find a job today?" },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [allJobMessages, setAllJobMessages] = useState([]);
  // pendingApplication: { applicationId, missing: [], awaitingCheckbox: bool, awaitingConfirm: bool, suggestedAnswer: any }
  const [pendingApplication, setPendingApplication] = useState(null);
  // Gmail login modal state
  const [gmailModal, setGmailModal] = useState({ show: false, applicationId: null, polling: false });
  const gmailPollRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // ── Stop Gmail login polling ──
  const stopGmailPoll = () => {
    if (gmailPollRef.current) {
      clearInterval(gmailPollRef.current);
      gmailPollRef.current = null;
    }
  };

  // ── Cancel Gmail login modal ──
  const handleGmailLoginCancel = () => {
    stopGmailPoll();
    setGmailModal({ show: false, applicationId: null, polling: false });
    setIsTyping(false);
    setMessages((prev) => [
      ...prev,
      { sender: "ai", text: "Gmail login cancelled. You can try applying again when ready." },
    ]);
  };

  // ── Poll backend until user completes Gmail login ──
  const startGmailLoginPolling = (applicationId) => {
    setGmailModal({ show: true, applicationId, polling: true });
    stopGmailPoll();
    gmailPollRef.current = setInterval(async () => {
      try {
        const resp = await fetch(
          `http://localhost:5001/api/apply/gmail-login/status?applicationId=${applicationId}`
        );
        const data = await resp.json();

        if (!data.success) {
          stopGmailPoll();
          setGmailModal({ show: false, applicationId: null, polling: false });
          setIsTyping(false);
          setMessages((prev) => [
            ...prev,
            { sender: "ai", text: `❌ ${data.message || "Gmail login session lost."}` },
          ]);
          return;
        }

        if (data.status === "awaiting_login") return; // still waiting

        // Login done & form loaded – close modal and drive the form
        stopGmailPoll();
        setGmailModal({ show: false, applicationId: null, polling: false });
        setMessages((prev) => [
          ...prev,
          { sender: "ai", text: "✅ Gmail login successful! Starting form automation..." },
        ]);
        handleApplyResponse(data);
        setIsTyping(false);
      } catch {
        // Network hiccup — keep polling
      }
    }, 2000);
  };

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
        msg ;
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

  const buildUserProfileForApply = async () => {
    const stored = (() => {
      try { return JSON.parse(localStorage.getItem("jobcore_profile") || "null"); }
      catch { return null; }
    })();

    let dbProfile = null;
    let workExperience = null;
    let education = null;

    if (user?.id) {
      try {
        const { data } = await getProfile(user.id);
        dbProfile = data || null;
      } catch {
        dbProfile = null;
      }
      try {
        const { data } = await getWorkExperience(user.id);
        workExperience = data || null;
      } catch {
        workExperience = null;
      }
      try {
        const { data } = await getEducation(user.id);
        education = data || null;
      } catch {
        education = null;
      }
    }

    const combined = { ...(dbProfile || {}), ...(stored || {}) };

    return {
      ...combined,
      full_name: combined.full_name || combined.name || user?.displayName || "",
      name: combined.name || combined.full_name || user?.displayName || "",
      email: combined.email || stored?.email || user?.email || "",
      work_experience: workExperience || combined.work_experience || combined.experience || [],
      education: education || combined.education || [],
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

    if (applyData?.status === "needs_confirm") {
      const prompt = applyData?.message || buildNeedsInfoPrompt(missing);
      setMessages((prev) => [...prev, {
        sender: "ai",
        text: prompt,
        confirmQuestion: firstQ,
        suggestedAnswer: applyData?.suggestedAnswer,
        applicationId: applyData.applicationId,
      }]);
      setPendingApplication({
        applicationId: applyData.applicationId,
        missing,
        awaitingCheckbox: false,
        awaitingConfirm: true,
        suggestedAnswer: applyData?.suggestedAnswer,
      });
      return;
    }

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
        awaitingConfirm: false,
        suggestedAnswer: null,
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

  const handleConfirmSuggested = async () => {
    if (!pendingApplication?.applicationId) return;

    const currentQ = (pendingApplication.missing || [])[0];
    const label = currentQ?.label;
    const suggested = pendingApplication.suggestedAnswer;
    const display = suggested ? String(suggested) : "(confirmed)";

    setMessages((prev) => [...prev, { sender: "user", text: `Confirmed: ${display}` }]);
    setIsTyping(true);

    const answers = label ? { [label]: suggested } : { default: suggested };

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

  const handleEditSuggested = () => {
    if (!pendingApplication?.applicationId) return;

    const missing = pendingApplication.missing || [];
    const firstQ = missing[0] || null;
    const isCheckbox = (firstQ?.input_type || "").toLowerCase() === "checkbox";
    const prompt = buildNeedsInfoPrompt(missing);

    setMessages((prev) => [...prev, {
      sender: "ai",
      text: `Okay, please provide your answer.\n${prompt}`,
      checkboxQuestion: isCheckbox ? firstQ : null,
      applicationId: pendingApplication.applicationId,
    }]);

    setPendingApplication((prev) => ({
      ...(prev || {}),
      awaitingConfirm: false,
      awaitingCheckbox: isCheckbox,
      suggestedAnswer: null,
    }));
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
        setMessages((prev) => [...prev, { sender: "ai", text: "🔐 Opening Gmail login window... Please log in to continue the application." }]);
        const profile = await buildUserProfileForApply();

        // Step 1: Open Gmail login browser
        let loginData;
        try {
          const loginResp = await fetch("http://localhost:5001/api/apply/gmail-login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ applyUrl: data.applyUrl, profile }),
          });
          loginData = await loginResp.json();
        } catch {
          setMessages((prev) => [...prev, { sender: "ai", text: "❌ Could not open Gmail login. Please make sure the backend is running." }]);
          setIsTyping(false);
          return;
        }

        if (!loginData?.success) {
          setMessages((prev) => [...prev, { sender: "ai", text: `❌ ${loginData?.message || "Could not open Gmail login."}` }]);
          setIsTyping(false);
          return;
        }

        // Step 2: Show modal and start polling
        startGmailLoginPolling(loginData.applicationId);
        // isTyping stays true while polling — modal provides UI feedback
      } else if (data?.success && data?.applyUrl && !data?.isGoogleForm) {
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: "We are in the demo version. We are now able to automate the Google Form ONLY.",
          },
        ]);
      }
    } catch {
      stopGmailPoll();
      setGmailModal({ show: false, applicationId: null, polling: false });
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

      {/* ── Gmail Login Modal ── */}
      {gmailModal.show && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="bg-[#161b22] border border-gray-700 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl text-center">
            <div className="flex justify-center mb-4">
              <svg viewBox="0 0 48 48" width="52" height="52">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Sign in to Google</h2>
            <p className="text-gray-400 text-sm mb-6 leading-relaxed">
              A browser window has opened.<br/>
              Please sign in with your Gmail account to continue the application.
            </p>
            <div className="flex items-center justify-center gap-2 mb-6">
              <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></span>
              <span className="text-sm text-gray-400 ml-2">Waiting for login...</span>
            </div>
            <div className="bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 mb-6 text-left">
              <p className="text-xs text-gray-500 mb-1">Instructions</p>
              <ol className="text-sm text-gray-300 space-y-1 list-decimal list-inside">
                <li>Enter your Gmail address in the browser</li>
                <li>Enter your password when prompted</li>
                <li>Complete any 2FA if required</li>
                <li>This modal will close automatically once signed in</li>
              </ol>
            </div>
            <button
              type="button"
              onClick={handleGmailLoginCancel}
              className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-semibold transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

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
                {msg.confirmQuestion &&
                  pendingApplication?.awaitingConfirm &&
                  pendingApplication?.applicationId === msg.applicationId && (
                    <ConfirmPrompt
                      suggestedAnswer={msg.suggestedAnswer}
                      onConfirm={handleConfirmSuggested}
                      onEdit={handleEditSuggested}
                    />
                  )}
                {msg.checkboxQuestion &&
                  msg.checkboxQuestion.options?.length > 0 &&
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
              : pendingApplication?.awaitingConfirm
              ? "Confirm or edit above, or type your answer..."
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
