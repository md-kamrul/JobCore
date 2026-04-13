import React, { useState } from "react";
import { FaPlus, FaBrain, FaTimes, FaKeyboard, FaMicrophone } from "react-icons/fa";

const VAPI_LINK = "https://vapi.ai?demo=true&shareKey=bb3ea19b-a496-45e1-9458-4522adbcaec5&assistantId=882fdf3c-f3be-454e-b579-d322ce19d825";

function ModeModal({ card, onClose }) {
  const handleVoice = () => {
    window.open(VAPI_LINK, "_blank", "noopener,noreferrer");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.65)", backdropFilter: "blur(4px)" }}
      onClick={onClose}
    >
      <div
        className="relative bg-gray-900 border border-gray-700 rounded-2xl p-8 w-full max-w-md mx-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        style={{ animation: "modalIn 0.22s cubic-bezier(0.34,1.56,0.64,1)" }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-white transition"
        >
          <FaTimes className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-2">
          <div className="text-blue-400 text-2xl">{card.icon}</div>
          <div>
            <h2 className="text-white font-semibold text-lg leading-tight">{card.title}</h2>
            <p className="text-gray-400 text-sm">Choose your interview mode</p>
          </div>
        </div>

        <div className="border-t border-gray-700 my-5" />

        {/* Mode Options */}
        <div className="grid grid-cols-2 gap-4">
          {/* Text Generation */}
          <button
            className="group flex flex-col items-center gap-3 bg-gray-800 hover:bg-blue-600 border border-gray-700 hover:border-blue-500 rounded-xl p-5 transition-all duration-200"
            onClick={() => alert("Text interview coming soon!")}
          >
            <div className="w-12 h-12 rounded-full bg-gray-700 group-hover:bg-blue-500 flex items-center justify-center transition-all duration-200">
              <FaKeyboard className="w-5 h-5 text-blue-400 group-hover:text-white transition-colors" />
            </div>
            <div className="text-center">
              <p className="text-white font-medium text-sm">Text</p>
              <p className="text-gray-400 group-hover:text-blue-100 text-xs mt-0.5 transition-colors">Type your answers</p>
            </div>
          </button>

          {/* Voice Generation */}
          <button
            className="group flex flex-col items-center gap-3 bg-gray-800 hover:bg-purple-600 border border-gray-700 hover:border-purple-500 rounded-xl p-5 transition-all duration-200"
            onClick={handleVoice}
          >
            <div className="w-12 h-12 rounded-full bg-gray-700 group-hover:bg-purple-500 flex items-center justify-center transition-all duration-200">
              <FaMicrophone className="w-5 h-5 text-purple-400 group-hover:text-white transition-colors" />
            </div>
            <div className="text-center">
              <p className="text-white font-medium text-sm">Voice</p>
              <p className="text-gray-400 group-hover:text-purple-100 text-xs mt-0.5 transition-colors">Speak your answers</p>
            </div>
          </button>
        </div>

        <p className="text-gray-500 text-xs text-center mt-5">
          Voice interviews are powered by Vapi AI and open in a new tab.
        </p>
      </div>

      <style>{`
        @keyframes modalIn {
          from { opacity: 0; transform: scale(0.88) translateY(16px); }
          to   { opacity: 1; transform: scale(1) translateY(0); }
        }
      `}</style>
    </div>
  );
}

function InterviewCard({ title, description, icon, onStart }) {
  return (
    <div className="bg-gray-800 hover:bg-gray-750 transition p-6 rounded-2xl text-white flex flex-col justify-between shadow-md border border-gray-700 hover:border-gray-600">
      <div>
        <div className="text-blue-400 text-3xl mb-4">{icon}</div>
        <h2 className="text-xl font-semibold mb-2">{title}</h2>
        <p className="text-gray-400 text-sm">{description}</p>
      </div>
      <button
        onClick={onStart}
        className="mt-6 bg-blue-500 hover:bg-blue-600 active:scale-95 py-2 rounded-lg font-medium text-sm transition-all duration-150"
      >
        Start Interview
      </button>
    </div>
  );
}

export default function App() {
  const [selectedCard, setSelectedCard] = useState(null);

  const cards = [
    {
      title: "AI Engineer",
      description: "Test your knowledge on ML, algorithms, and data structures.",
      icon: <FaBrain className="w-8 h-8" />,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Page Title */}
      <div className="text-center py-12">
        <h1 className="text-3xl font-bold mb-2">AI Mock Interview</h1>
        <p className="text-gray-400">
          Practice and sharpen your interview skills. Select a role to start.
        </p>
      </div>

      {/* Cards Grid */}
      <div className="max-w-2xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-6 px-6 pb-16">
        {/* Add Interview Card */}
        <div className="border-2 border-dashed border-gray-600 rounded-2xl flex flex-col items-center justify-center text-gray-400 hover:border-blue-500 hover:text-blue-400 transition cursor-pointer min-h-[200px] gap-2">
          <FaPlus className="w-10 h-10 mb-2" />
          <p className="text-center">Add Interview</p>
        </div>

        {/* Interview Cards */}
        {cards.map((c, i) => (
          <InterviewCard
            key={i}
            {...c}
            onStart={() => setSelectedCard(c)}
          />
        ))}
      </div>

      {/* Mode Selection Modal */}
      {selectedCard && (
        <ModeModal card={selectedCard} onClose={() => setSelectedCard(null)} />
      )}
    </div>
  );
}
