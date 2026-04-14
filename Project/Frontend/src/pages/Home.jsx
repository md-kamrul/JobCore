import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div className="min-h-screen py-10">
            <section className="text-center space-y-6 pt-10">
                <h1 className="text-5xl font-extrabold tracking-tight text-white">
                    Welcome to JobCore
                </h1>
                <p className="mx-auto max-w-2xl text-lg text-slate-300">
                    Search jobs, practice interview questions, and improve your resume all from one dashboard.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link
                        to="/job-agent"
                        className="rounded-full bg-cyan-500 px-8 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
                    >
                        Find Jobs
                    </Link>
                    <Link
                        to="/mock-interview"
                        className="rounded-full border border-slate-500 px-8 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
                    >
                        Practice Interview
                    </Link>
                </div>
            </section>

            <section className="mt-16 grid gap-6 md:grid-cols-3">
                <div className="rounded-3xl border border-slate-700 bg-slate-900/80 p-6 shadow-xl shadow-slate-900/30">
                    <h2 className="text-2xl font-bold text-white">Job Agent</h2>
                    <p className="mt-3 text-slate-300">
                        Quickly search for open positions and explore recommended roles that match your profile.
                    </p>
                </div>
                <div className="rounded-3xl border border-slate-700 bg-slate-900/80 p-6 shadow-xl shadow-slate-900/30">
                    <h2 className="text-2xl font-bold text-white">Mock Interview</h2>
                    <p className="mt-3 text-slate-300">
                        Practice answers, get feedback, and prepare for real interviews with confidence.
                    </p>
                </div>
                <div className="rounded-3xl border border-slate-700 bg-slate-900/80 p-6 shadow-xl shadow-slate-900/30">
                    <h2 className="text-2xl font-bold text-white">Resume Checker</h2>
                    <p className="mt-3 text-slate-300">
                        Upload your resume and receive suggestions for improvement in structure and keywords.
                    </p>
                </div>
            </section>
        </div>
    );
};

export default Home;
