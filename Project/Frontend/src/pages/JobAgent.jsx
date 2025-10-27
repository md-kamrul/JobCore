import React, { useState } from "react";

const JobAgent = () => {
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hi there! 👋 How can I help you find a job today?" },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    // Simulate multi-step AI response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: `Sure! Let me search for "${input}" jobs near you... 🔍` },
      ]);
    }, 1000);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text:
            "Here are a few matches I found:\n" +
            "• Product Designer – Google (San Francisco)\n" +
            "• UX/UI Designer – Airbnb (Remote)\n" +
            "• Visual Designer – Meta (Menlo Park)",
        },
      ]);
    }, 2500);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: "Would you like me to filter by salary, experience level, or company?",
        },
      ]);
      setIsTyping(false);
    }, 4000);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0d1117] text-white">
      {/* Header */}
      <header className="bg-[#161b22] p-4 shadow-md flex items-center justify-between">
        <h1 className="text-xl font-bold">JobCore AI</h1>
        <nav className="space-x-4 text-gray-400">
          <a href="#" className="hover:text-white">Dashboard</a>
          <a href="#" className="hover:text-white">Job Search</a>
          <a href="#" className="hover:text-white">Applications</a>
        </nav>
      </header>

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
              className={`max-w-md whitespace-pre-line p-3 rounded-2xl ${
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
