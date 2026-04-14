import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div className="min-h-screen bg-slate-100">

            {/* Navbar */}
            <nav className="bg-blue-700 sticky top-0 z-10 flex items-center justify-between px-10 py-4">
                <div className="flex items-center gap-2 text-white font-semibold text-lg">
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
                            <circle cx="12" cy="8" r="4" fill="#1d4ed8" />
                            <path d="M5 20c0-4 3.1-7 7-7s7 3 7 7" stroke="#1d4ed8" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                    </div>
                    Interview AI
                </div>
                <div className="flex items-center gap-8">
                    <a href="#" className="text-white text-sm border-b-2 border-white pb-0.5">Home</a>
                </div>
            </nav>

            {/* Hero Section */}
            <section
                className="relative flex items-end gap-10 px-10 pt-14 overflow-hidden"
                style={{
                    background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 40%, #3b82f6 70%, #60a5fa 100%)',
                    minHeight: '340px',
                }}
            >
                {/* Hero Text */}
                <div className="flex-1 pb-16 z-10">
                    <h1 className="text-4xl font-bold text-white leading-tight mb-2">
                        Ace Your Career Goals!
                    </h1>
                    <h2 className="text-xl font-medium text-blue-100 mb-3">
                        AI Mock Interviews &amp; Resume Checker
                    </h2>
                    <p className="text-blue-200 text-sm mb-7">
                        Practice for your dream job and get instant resume feedback
                    </p>
                    <div className="flex gap-4">
                        <Link
                            to="/mock-interview"
                            className="border-2 border-white text-white px-6 py-2.5 rounded-lg text-sm hover:bg-white hover:text-blue-700 transition"
                        >
                            Start Mock Interview
                        </Link>
                        <Link
                            to="/resume"
                            className="bg-white text-blue-700 font-medium px-6 py-2.5 rounded-lg text-sm hover:bg-blue-50 transition"
                        >
                            Upload Resume
                        </Link>
                    </div>
                </div>

                {/* Hero Robot Illustration */}
                <div className="w-72 flex-shrink-0 flex items-end justify-center relative pb-0">
                    {/* Decorative circles */}
                    <div className="absolute w-52 h-52 rounded-full bg-white/10 top-4 left-4" />
                    <div className="absolute w-36 h-36 rounded-full bg-white/15 top-12 left-12" />
                    {/* Chat bubbles */}
                    <div className="absolute top-6 right-2 bg-white rounded-xl px-3 py-1.5 text-xs font-medium text-blue-700 shadow-sm">
                        Hi! Ready?
                    </div>
                    <div className="absolute top-16 right-0 bg-blue-100 rounded-xl px-3 py-1.5 text-xs text-blue-600">
                        Let's practice!
                    </div>
                    {/* Simple Robot SVG */}
                    <svg width="160" height="180" viewBox="0 0 160 180" className="relative z-10">
                        {/* Headphone arc */}
                        <path d="M30 70 Q30 20 80 20 Q130 20 130 70" stroke="#1e40af" strokeWidth="8" fill="none" strokeLinecap="round" />
                        <rect x="20" y="62" width="16" height="22" rx="8" fill="#1e40af" />
                        <rect x="124" y="62" width="16" height="22" rx="8" fill="#1e40af" />
                        {/* Head */}
                        <rect x="38" y="55" width="84" height="66" rx="22" fill="#dbeafe" />
                        {/* Eyes */}
                        <circle cx="62" cy="84" r="10" fill="#1d4ed8" />
                        <circle cx="98" cy="84" r="10" fill="#1d4ed8" />
                        <circle cx="65" cy="81" r="4" fill="#93c5fd" />
                        <circle cx="101" cy="81" r="4" fill="#93c5fd" />
                        {/* Torso */}
                        <rect x="45" y="124" width="70" height="52" rx="14" fill="#dbeafe" />
                        {/* Badge */}
                        <circle cx="80" cy="148" r="12" fill="#1d4ed8" />
                        <circle cx="80" cy="143" r="4" fill="#fff" />
                        <path d="M73 156 c0-4 3-6 7-6 s7 2 7 6" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round" />
                    </svg>
                </div>

                {/* Wave bottom */}
                <svg
                    className="absolute bottom-0 left-0 w-full"
                    viewBox="0 0 1440 50"
                    preserveAspectRatio="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path d="M0,20 C400,60 1000,10 1440,30 L1440,50 L0,50 Z" fill="#f1f5f9" />
                </svg>
            </section>

            {/* Feature Cards */}
            <section className="px-10 py-10 bg-slate-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-5xl mx-auto">

                    {/* AI Mock Interviews */}
                    <div className="bg-white rounded-2xl p-6 flex items-center justify-between border border-slate-200 gap-4">
                        <div>
                            <h3 className="text-lg font-semibold text-slate-800 mb-2">AI Mock Interviews</h3>
                            <p className="text-sm text-slate-500 mb-5">Simulate real interviews with AI.<br />Get instant feedback &amp; tips.</p>
                            <Link to="/mock-interview" className="bg-blue-700 text-white text-sm px-5 py-2.5 rounded-lg hover:bg-blue-600 transition inline-flex items-center gap-1">
                                Practice Now ›
                            </Link>
                        </div>
                        <div className="w-24 h-20 bg-blue-50 rounded-xl flex items-center justify-center flex-shrink-0 text-4xl">
                            🤖
                        </div>
                    </div>

                    {/* Resume Checker */}
                    <div className="bg-white rounded-2xl p-6 flex items-center justify-between border border-slate-200 gap-4">
                        <div>
                            <h3 className="text-lg font-semibold text-slate-800 mb-2">Resume Checker</h3>
                            <p className="text-sm text-slate-500 mb-5">Upload your resume. Get detailed analysis &amp; improvements.</p>
                            <Link to="/resume" className="bg-blue-700 text-white text-sm px-5 py-2.5 rounded-lg hover:bg-blue-600 transition inline-block">
                                Check Resume
                            </Link>
                        </div>
                        <div className="w-24 h-20 bg-blue-50 rounded-xl flex items-center justify-center flex-shrink-0 text-4xl">
                            📋
                        </div>
                    </div>

                    {/* AI Voice Interviews */}
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 flex items-center justify-between border border-blue-100 gap-4">
                        <div>
                            <h3 className="text-lg font-semibold text-slate-800 mb-2">AI Voice Interviews</h3>
                            <p className="text-sm text-slate-500 mb-5">Practice with voice-based<br />AI interviews.</p>
                            <Link to="/voice-interview" className="bg-blue-700 text-white text-sm px-5 py-2.5 rounded-lg hover:bg-blue-600 transition inline-flex items-center gap-1">
                                Start Voice Interview ›
                            </Link>
                        </div>
                        <div className="w-24 h-20 rounded-xl flex items-center justify-center flex-shrink-0 text-4xl">
                            🎙️
                        </div>
                    </div>

                    {/* Upload Resume */}
                    <div className="bg-white rounded-2xl p-6 flex items-center justify-between border border-slate-200 gap-4">
                        <div>
                            <h3 className="text-lg font-semibold text-slate-800 mb-2">Upload Your Resume</h3>
                            <p className="text-sm text-slate-500 mb-5">Upload your CV for instant analysis.</p>
                            <Link to="/upload" className="bg-blue-700 text-white text-sm px-5 py-2.5 rounded-lg hover:bg-blue-600 transition inline-flex items-center gap-1">
                                Upload Now ›
                            </Link>
                        </div>
                        <div className="w-24 h-20 bg-blue-50 rounded-xl flex items-center justify-center flex-shrink-0 text-4xl">
                            📤
                        </div>
                    </div>
                </div>
            </section>

            {/* Why Choose Us */}
            <section className="px-10 py-12 bg-slate-100 text-center">
                <h2 className="text-2xl font-semibold text-slate-800 mb-8">Why Choose Us?</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl mx-auto">
                    <div className="bg-white rounded-2xl p-8 border border-slate-200">
                        <div className="w-20 h-16 bg-blue-50 rounded-t-full mx-auto mb-5 flex items-end justify-center pb-2 text-3xl">
                            💡
                        </div>
                        <h4 className="text-base font-semibold text-slate-800 mb-2">Realistic Practice</h4>
                        <p className="text-sm text-slate-500">Job-specific interview simulations.</p>
                    </div>
                    <div className="bg-white rounded-2xl p-8 border border-slate-200">
                        <div className="w-20 h-16 bg-blue-50 rounded-t-full mx-auto mb-5 flex items-end justify-center pb-2 text-3xl">
                            🔍
                        </div>
                        <h4 className="text-base font-semibold text-slate-800 mb-2">Resume Optimization</h4>
                        <p className="text-sm text-slate-500">AI-powered resume insights.</p>
                    </div>
                    <div className="bg-white rounded-2xl p-8 border border-slate-200">
                        <div className="w-20 h-16 bg-blue-50 rounded-t-full mx-auto mb-5 flex items-end justify-center pb-2 text-3xl">
                            📈
                        </div>
                        <h4 className="text-base font-semibold text-slate-800 mb-2">Career Growth</h4>
                        <p className="text-sm text-slate-500">Improve your hiring chances.</p>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-blue-700 text-blue-200 text-center py-5 text-sm">
                © 2026 Interview AI · All rights reserved
            </footer>
        </div>
    );
};

export default Home;
