import React, { useState } from "react";
import { getResumeCheckerRecommendation } from "../components/ResumeCheckerAgent";

const JobAgent = () => {
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hi there! 👋 How can I help you find a job today?" },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

    const handleSend = async (e) => {
      e.preventDefault();
      if (!input.trim() || isTyping) return;

      const userMessage = { sender: "user", text: input };
      const userQuery = input;
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsTyping(true);

      // Step 1: Agent 'understands' the query
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "🤔 Understanding your query..." },
      ]);

      try {
        // Step 2: Decide which agent to call
        const recommendation = getResumeCheckerRecommendation(userQuery);
        if (recommendation) {
          // ResumeCheckerAgent handles this (dynamic routing)
          await new Promise(resolve => setTimeout(resolve, 800));
          setMessages((prev) => {
            // Remove 'understanding' message and add recommendation
            const newMessages = prev.slice(0, -1);
            return [
              ...newMessages,
              { sender: "ai", text: recommendation },
            ];
          });
          return; // Do not proceed to job search
        }
        // JobSearchAgent handles this
        await new Promise(resolve => setTimeout(resolve, 800));
        setMessages((prev) => {
          // Remove 'understanding' message and add searching progress
          const newMessages = prev.slice(0, -1);
          return [
            ...newMessages,
            { sender: "ai", text: `🔍 Searching LinkedIn for "${userQuery}"...\n\nThis may take 30-60 seconds as I:\n1. Understand your requirements\n2. Generate search criteria\n3. Find relevant jobs\n4. Format results` },
          ];
        });
        // Call the backend API as usual
        const response = await fetch('http://localhost:5001/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userQuery }),
        });

        const data = await response.json();

        if (data.success) {
          setMessages((prev) => {
            // Remove searching progress and add results
            const newMessages = prev.slice(0, -1);
            return [
              ...newMessages,
              { sender: "ai", text: data.message },
            ];
          });
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
        console.error('Error calling API:', error);
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
        {messages.map((msg, index) => (
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
        ))}

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
