import React from 'react';
import { FaFileAlt, FaEnvelope, FaSearch, FaList, FaComments, FaUser } from 'react-icons/fa';

export default function JobCoreDashboard() {
  const features = [
    {
      icon: <FaFileAlt className="w-8 h-8" />,
      title: "Resume Checker",
      description: "Create and manage your professional resumes to stand out to employers.",
      color: "bg-blue-500"
    },
    {
      icon: <FaEnvelope className="w-8 h-8" />,
      title: "Cover Letter Generator",
      description: "Generate tailored cover letters for each job application in seconds.",
      color: "bg-blue-500"
    },
    {
      icon: <FaSearch className="w-8 h-8" />,
      title: "AI Job Search",
      description: "Let our AI find the best job opportunities based on your profile.",
      color: "bg-blue-500"
    },
    {
      icon: <FaList className="w-8 h-8" />,
      title: "Application Tracker",
      description: "Keep track of all your job applications from one central place.",
      color: "bg-blue-500"
    },
    {
      icon: <FaComments className="w-8 h-8" />,
      title: "AI Mock Interview",
      description: "Practice common interview questions and get AI-powered feedback.",
      color: "bg-blue-500"
    },
    {
      icon: <FaUser className="w-8 h-8" />,
      title: "Profile & Preferences",
      description: "Manage your personal information and job search preferences.",
      color: "bg-blue-500"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-3">Welcome back, Farhan!</h1>
          <p className="text-gray-400 text-lg">What would you like to do today?</p>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-all duration-300 cursor-pointer group border border-gray-700 hover:border-gray-600"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`${feature.color} bg-opacity-20 p-3 rounded-lg`}>
                  <div className="text-blue-400">
                    {feature.icon}
                  </div>
                </div>
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}