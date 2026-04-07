import React, { useState, useContext } from "react";
import { getResumeCheckerRecommendation } from "../components/ResumeCheckerAgent";
import ProgressiveJobMessages from "../components/ProgressiveJobMessages";
import { AuthContext } from "../provider/AuthProvider";

const JobAgent = () => {
  const { user } = useContext(AuthContext);
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hi there! 👋 How can I help you find a job today?" },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [allJobMessages, setAllJobMessages] = useState([]); // Store all job searches
  const [pendingApplication, setPendingApplication] = useState(null); // { applicationId, missing: [] }

  const buildUserProfileForApply = () => {
    // Best-effort: use auth email + anything the app might have stored.
    const stored = (() => {
      try {
        return JSON.parse(localStorage.getItem("jobcore_profile") || "null");
      } catch {
        return null;
      }
    })();

    return {
      ...(stored || {}),
      email: stored?.email || user?.email || "",
      name: stored?.name || user?.displayName || "",
    };
  };

  const handleApplyClick = async (job) => {
    const detailsUrl = job?.url;
    if (!detailsUrl) return;

    const placeholderId = `${Date.now()}-${Math.random()}`;
    setMessages((prev) => [
      ...prev,
      { id: placeholderId, sender: "ai", text: "🔗 Finding the application link..." },
    ]);

    try {
      const response = await fetch("http://localhost:5001/api/extract-apply-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ detailsUrl }),
      });

      const data = await response.json();

      const messageText =
        data && data.success
          ? data.message
          : `❌ Error: ${data?.message || "Could not extract the apply link."}`;

      setMessages((prev) =>
        prev.map((m) => (m.id === placeholderId ? { ...m, text: messageText } : m))
      );

      // If it's a Google Form, trigger Agent-B auto-apply
      if (data?.success && data?.applyUrl && data?.isGoogleForm) {
        const applyUrl = data.applyUrl;
        setMessages((prev) => [...prev, { sender: "ai", text: "I am starting to apply the job. Please bear with me..." }]);

        const profile = buildUserProfileForApply();
        const applyResp = await fetch("http://localhost:5001/api/apply/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ applyUrl, profile, headless: false }),
        });

        const applyData = await applyResp.json();
        if (applyData?.success) {
          setMessages((prev) => [...prev, { sender: "ai", text: applyData.message }]);
          if (applyData?.status === "needs_info" && applyData?.applicationId) {
            setPendingApplication({ applicationId: applyData.applicationId, missing: applyData.missing || [] });
          } else {
            setPendingApplication(null);
          }
        } else {
          setMessages((prev) => [...prev, { sender: "ai", text: `❌ ${applyData?.message || "Auto-apply failed."}` }]);
        }
      }
    } catch (error) {
      console.error("Error extracting apply URL:", error);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === placeholderId
            ? {
                ...m,
                text: "❌ Unable to extract the apply link right now. Please try again.",
              }
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

    // If we're mid application, treat this message as missing-info answer
    if (pendingApplication?.applicationId) {
      try {
        const missing = pendingApplication.missing || [];
        const first = missing[0];
        const label = first?.label;
        const answers = label ? { [label]: userQuery } : { default: userQuery };

        const resp = await fetch("http://localhost:5001/api/apply/continue", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ applicationId: pendingApplication.applicationId, answers, headless: false }),
        });
        const data = await resp.json();

        if (data?.success) {
          setMessages((prev) => [...prev, { sender: "ai", text: data.message }]);
          if (data?.status === "needs_info") {
            setPendingApplication({ applicationId: pendingApplication.applicationId, missing: data.missing || [] });
          } else {
            setPendingApplication(null);
          }
        } else {
          setMessages((prev) => [...prev, { sender: "ai", text: `❌ ${data?.message || "Auto-apply failed."}` }]);
          setPendingApplication(null);
        }
      } catch (err) {
        console.error("Error continuing auto-apply:", err);
        setMessages((prev) => [...prev, { sender: "ai", text: "❌ Unable to continue the auto-apply right now. Please try again." }]);
        setPendingApplication(null);
      } finally {
        setIsTyping(false);
      }
      return;
    }

    // Step 1: Agent 'understands' the query
    setMessages((prev) => [
      ...prev,
      { sender: "ai", text: "🤔 Understanding your query..." },
    ]);

    try {
      // Step 2: Decide which agent to call
      const recommendation = getResumeCheckerRecommendation(userQuery);
      if (recommendation) {
        await new Promise((resolve) => setTimeout(resolve, 800));
        setMessages((prev) => {
          const newMessages = prev.slice(0, -1);
          return [
            ...newMessages,
            { sender: "ai", text: recommendation },
          ];
        });
        setIsTyping(false);
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 800));
      setMessages((prev) => {
        const newMessages = prev.slice(0, -1);
        return [
          ...newMessages,
          {
            sender: "ai",
            text: `🔍 Searching for "${userQuery}"...\n\nThis may take 30-60 seconds as I:\n1. Understand your requirements\n2. Generate search criteria\n3. Find relevant jobs\n4. Format results`,
          },
        ];
      });
      // Call the backend API as usual
      const response = await fetch("http://localhost:5001/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userQuery }),
      });

      const data = await response.json();

      if (data.success) {
        if (Array.isArray(data.message)) {
          setMessages((prev) => {
            // Remove the last 'searching' message, then add a placeholder for jobs
            const newMessages = prev.slice(0, -1);
            return [
              ...newMessages,
              { sender: "ai", text: `Job results for "${userQuery}":`, jobIndex: allJobMessages.length },
            ];
          });
          setAllJobMessages((prev) => [...prev, data.message]); // Append new job search results
        } else {
          setMessages((prev) => {
            const newMessages = prev.slice(0, -1);
            return [
              ...newMessages,
              { sender: "ai", text: data.message },
            ];
          });
        }
      } else {
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: `❌ Error: ${data.message || "Something went wrong. Please try again."}`,
          },
        ]);
      }
    } catch (error) {
      console.error("Error calling API:", error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: "❌ Unable to connect to the job search service. Please make sure the backend server is running and try again.",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0d1117] text-white">
      {/* Chat Section */}
      <main className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => {
          // If this message is a job result placeholder, render ProgressiveJobMessages for that search
          if (msg.jobIndex !== undefined) {
            return (
              <div key={index}>
                <div className="flex justify-start">
                  <div className="max-w-[90%] break-normal whitespace-pre-line p-4 rounded-2xl bg-[#161b22] text-gray-200 rounded-bl-none">
                    {msg.text}
                  </div>
                </div>
                <ProgressiveJobMessages
                  jobMessages={allJobMessages[msg.jobIndex]}
                  onApply={handleApplyClick}
                />
              </div>
            );
          }
          return (
            <div
              key={index}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[90%] break-normal whitespace-pre-line p-4 rounded-2xl ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-[#161b22] text-gray-200 rounded-bl-none"
                }`}
              >
                {msg.text}
              </div>
            </div>
          );
        })}
        {/* Typing Indicator */}
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
      </main>

      {/* Input Section */}
      <form
        onSubmit={handleSend}
        className="p-4 bg-[#161b22] flex items-center gap-2 border-t border-gray-700"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
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
