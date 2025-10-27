import React from "react";
import { FaPlus, FaCode, FaServer, FaBrain } from "react-icons/fa";

function InterviewCard({ title, description, icon }) {
  return (
    <div className="bg-gray-800 hover:bg-gray-700 transition p-6 rounded-2xl text-white flex flex-col justify-between shadow-md">
      <div>
        <div className="text-blue-400 text-3xl mb-4">{icon}</div>
        <h2 className="text-xl font-semibold mb-2">{title}</h2>
        <p className="text-gray-400">{description}</p>
      </div>
      <button className="mt-6 bg-blue-500 hover:bg-blue-600 py-2 rounded-lg">
        Start Interview
      </button>
    </div>
  );
}

export default function App() {
  const cards = [
    {
      title: "Frontend Developer",
      description: "Prepare for questions on HTML, CSS, JavaScript, and frameworks.",
      icon: <FaCode className="w-8 h-8" />,
    },
    {
      title: "Backend Developer",
      description: "Focus on server-side logic, databases, APIs, and architecture.",
      icon: <FaServer className="w-8 h-8" />,
    },
    {
      title: "Full Stack Developer",
      description: "Cover topics from front-end to back-end technologies.",
      icon: <FaCode className="w-8 h-8" />,
    },
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
      <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 px-6 pb-16">
        {/* Add Interview Card */}
        <div className="border-2 border-dashed border-gray-600 rounded-2xl flex flex-col items-center justify-center text-gray-400 hover:border-blue-500 transition">
          <FaPlus className="w-10 h-10 mb-2" />
          <p className="text-center">Add Interview</p>
        </div>

        {/* Interview Cards */}
        {cards.map((c, i) => (
          <InterviewCard key={i} {...c} />
        ))}
      </div>
    </div>
  );
}
