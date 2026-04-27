import React from "react";
import { useNavigate } from "react-router-dom";
import { FaKeyboard, FaMicrophone } from "react-icons/fa";

function InterviewModeCard({ title, subtitle, icon, iconClassName, onClick }) {
  return (
    <button
      onClick={onClick}
      className="group w-full max-w-[360px] bg-blue-600 hover:bg-blue-500 rounded-2xl px-7 py-6 text-center transition-all duration-200 border border-blue-500/70 shadow-lg shadow-blue-950/20"
    >
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-700/80 ring-1 ring-slate-500/40 transition-transform duration-200 group-hover:scale-105">
        {React.cloneElement(icon, { className: iconClassName })}
      </div>
      <h2 className="text-white text-3xl sm:text-4xl leading-none font-semibold tracking-tight">{title}</h2>
      <p className="mt-2 text-slate-300 text-base sm:text-lg leading-tight font-medium">{subtitle}</p>
    </button>
  );
}

export default function App() {
  const navigate = useNavigate();

  const handleVoice = () => {
    navigate("/mock-interview/voice");
  };

  const handleText = () => {
    navigate("/mock-interview/text");
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Page Title */}
      <div className="text-center pt-12 pb-10 px-4">
        <h1 className="text-3xl font-bold">AI Mock Interview</h1>
        <p className="mt-2 text-gray-400 text-sm sm:text-base">
          Practice and sharpen your interview skills. Choose a mode to begin.
        </p>
      </div>

      <div className="mx-auto flex w-full max-w-5xl flex-col items-center gap-5 px-5 pb-14 sm:flex-row sm:items-stretch sm:justify-center sm:gap-8">
        <InterviewModeCard
          title="Text"
          subtitle="Type your answers"
          icon={<FaKeyboard />}
          iconClassName="h-7 w-7 text-blue-400"
          onClick={handleText}
        />
        <InterviewModeCard
          title="Voice"
          subtitle="Speak your answers"
          icon={<FaMicrophone />}
          iconClassName="h-7 w-7 text-fuchsia-400"
          onClick={handleVoice}
        />
      </div>
    </div>
  );
}