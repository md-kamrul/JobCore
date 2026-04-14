import React, { useState } from "react";
import { FaPlus, FaCode, FaServer, FaBrain, FaArrowLeft } from "react-icons/fa";

function InterviewCard({ title, description, icon, onStart }) {
  return (
    <div className="bg-gray-800 hover:bg-gray-700 transition p-6 rounded-2xl text-white flex flex-col justify-between shadow-md">
      <div>
        <div className="text-blue-400 text-3xl mb-4">{icon}</div>
        <h2 className="text-xl font-semibold mb-2">{title}</h2>
        <p className="text-gray-400">{description}</p>
      </div>
      <button 
        onClick={() => onStart(title)}
        className="mt-6 bg-blue-500 hover:bg-blue-600 py-2 rounded-lg transition"
      >
        Start Interview
      </button>
    </div>
  );
}

function InterviewSession({ role, onBack }) {
  const apiBaseUrl = (import.meta.env.VITE_MOCK_INTERVIEW_API_URL || "http://localhost:5002").replace(/\/$/, "");
  const [step, setStep] = useState("level");
  const [level, setLevel] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentQData, setCurrentQData] = useState(null);

  // Marksheet stats
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [totalScore, setTotalScore] = useState(0);

  const fetchQuestion = async (selectedLevel) => {
    setLoading(true);
    setError("");
    
    try {
      const response = await fetch(`${apiBaseUrl}/api/interview/question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role, level: selectedLevel }),
      });

      if (!response.ok) throw new Error("Failed to fetch question");

      const data = await response.json();
      setCurrentQData(data.questionData);
      setQuestion(data.question);
      setStep("question");
    } catch (err) {
      setError(`Failed to load question. Make sure backend is running on ${apiBaseUrl}.`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim()) {
      setError("Please provide an answer before submitting.");
      return;
    }

    if (!currentQData) {
      setError("Question data is missing. Please reload.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${apiBaseUrl}/api/interview/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: question, 
          answer: answer,
          correct_answer: currentQData.Answer || "",
          category: currentQData.Category || "",
          difficulty: currentQData.Difficulty || ""
        }),
      });

      if (!response.ok) throw new Error("Failed to evaluate answer");

      const data = await response.json();
      setEvaluation(data.evaluation);
      setQuestionsAnswered((prev) => prev + 1);
      setTotalScore((prev) => prev + (data.score || 0));
      setStep("evaluation");
    } catch (err) {
      setError("Failed to evaluate answer. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const nextQuestion = () => {
    setAnswer("");
    setEvaluation("");
    setCurrentQData(null);
    fetchQuestion(level);
  };

  const endInterview = () => {
    setStep("marksheet");
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white px-6 py-12">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <button onClick={onBack} className="p-2 hover:bg-gray-800 rounded-lg transition">
            <FaArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">{role} Interview</h1>
            <p className="text-gray-400 text-sm">Powered by AI</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {step === "level" && (
          <div className="bg-gray-800 p-8 rounded-2xl">
            <h2 className="text-xl font-semibold mb-6">Select Your Level</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {["junior", "mid-level", "senior"].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => {
                    setLevel(lvl);
                    fetchQuestion(lvl);
                  }}
                  disabled={loading}
                  className="bg-gray-700 hover:bg-blue-600 p-6 rounded-xl transition capitalize disabled:opacity-50"
                >
                  {lvl}
                </button>
              ))}
            </div>
            {loading && <div className="text-center mt-6 text-blue-400">Loading question...</div>}
          </div>
        )}

        {step === "question" && (
          <div className="bg-gray-800 p-8 rounded-2xl">
            <div className="mb-6">
              <span className="bg-blue-600 text-xs px-3 py-1 rounded-full uppercase">{level}</span>
            </div>
            <h2 className="text-xl font-semibold mb-4">Interview Question:</h2>
            <div className="bg-gray-900 p-6 rounded-lg mb-6">
              <p className="text-gray-300 leading-relaxed">{question}</p>
            </div>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              className="w-full bg-gray-900 text-white p-4 rounded-lg border border-gray-700 focus:border-blue-500 outline-none min-h-[200px]"
            />
            <button
              onClick={submitAnswer}
              disabled={loading || !answer.trim()}
              className="mt-4 w-full bg-blue-500 hover:bg-blue-600 py-3 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Evaluating..." : "Submit Answer"}
            </button>
          </div>
        )}

        {step === "evaluation" && (
          <div className="bg-gray-800 p-8 rounded-2xl">
            <h2 className="text-xl font-semibold mb-6">Your Evaluation</h2>
            <div className="mb-6">
              <h3 className="text-sm text-gray-400 mb-2">Question:</h3>
              <p className="text-gray-300 bg-gray-900 p-4 rounded-lg">{question}</p>
            </div>
            <div className="mb-6">
              <h3 className="text-sm text-gray-400 mb-2">Your Answer:</h3>
              <p className="text-gray-300 bg-gray-900 p-4 rounded-lg">{answer}</p>
            </div>
            <div className="mb-6">
              <h3 className="text-sm text-gray-400 mb-2">AI Feedback:</h3>
              <div className="bg-blue-900/20 border border-blue-500 p-6 rounded-lg">
                <pre className="text-gray-200 whitespace-pre-wrap font-sans">{evaluation}</pre>
              </div>
            </div>
            <div className="flex gap-4">
              <button
                onClick={nextQuestion}
                className="flex-1 bg-blue-500 hover:bg-blue-600 py-3 rounded-lg font-semibold transition"
              >
                Next Question
              </button>
              <button
                onClick={endInterview}
                className="flex-1 bg-gray-700 hover:bg-gray-600 py-3 rounded-lg font-semibold transition"
              >
                End Interview
              </button>
            </div>
          </div>
        )}

        {step === "marksheet" && (
          <div className="bg-gray-800 p-8 rounded-2xl text-center shadow-lg">
            <h2 className="text-3xl font-bold mb-6 text-blue-400">Interview Complete!</h2>
            <div className="bg-gray-900 border border-gray-700 p-8 rounded-xl shadow-inner mb-8 max-w-sm mx-auto">
              <div className="mb-4">
                <p className="text-gray-400 text-sm mb-1 uppercase tracking-wide">Questions Answered</p>
                <p className="text-4xl font-bold text-white">{questionsAnswered}</p>
              </div>
              <div className="w-full h-px bg-gray-800 my-4"></div>
              <div>
                <p className="text-gray-400 text-sm mb-1 uppercase tracking-wide">Total Score</p>
                <p className="text-4xl font-bold text-green-400">
                  {Number(totalScore).toFixed(1)} <span className="text-xl text-gray-500">/ {questionsAnswered * 10}</span>
                </p>
              </div>
            </div>
            
            <button
              onClick={onBack}
              className="bg-blue-500 hover:bg-blue-600 px-8 py-3 rounded-lg font-semibold transition w-full max-w-sm"
            >
              Back to Role Selection
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [selectedRole, setSelectedRole] = useState(null);

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

  if (selectedRole) {
    return <InterviewSession role={selectedRole} onBack={() => setSelectedRole(null)} />;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="text-center py-12">
        <h1 className="text-3xl font-bold mb-2">AI Mock Interview</h1>
        <p className="text-gray-400">
          Practice and sharpen your interview skills. Select a role to start.
        </p>
      </div>
      <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 px-6 pb-16">
        <div className="border-2 border-dashed border-gray-600 rounded-2xl flex flex-col items-center justify-center text-gray-400 hover:border-blue-500 transition min-h-[250px]">
          <FaPlus className="w-10 h-10 mb-2" />
          <p className="text-center">Add Interview</p>
        </div>
        {cards.map((c, i) => (
          <InterviewCard key={i} {...c} onStart={setSelectedRole} />
        ))}
      </div>
    </div>
  );
}

