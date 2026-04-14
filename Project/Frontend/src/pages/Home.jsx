import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    const quickActions = [
        {
            title: 'AI Mock Interview',
            description: 'Practice realistic interview questions and get instant feedback.',
            cta: 'Start Practice',
            to: '/mock-interview',
            badge: 'MI',
            image: '/mock-interview.png',
        },
        {
            title: 'Resume Checker',
            description: 'Upload your resume and receive AI-powered improvement suggestions.',
            cta: 'Analyze Resume',
            to: '/resume-checker',
            badge: 'RC',
            image: '/resume-checker.png',
        },
        {
            title: 'Job Agent',
            description: 'Discover roles and streamline applications with AI assistance.',
            cta: 'Explore Jobs',
            to: '/job-agent',
            badge: 'JA',
            image: '/job-agent.png',
        },
        {
            title: 'Profile Setup',
            description: 'Keep your profile up to date for better personalization.',
            cta: 'Update Profile',
            to: '/profile',
            badge: 'PF',
            image: '/profile.png',
        },
    ];

    const howItWorks = [
        'Choose a module: Mock Interview, Resume Checker, or Job Agent.',
        'Complete a short guided flow powered by AI prompts.',
        'Apply improvements immediately and track your progress.',
    ];

    return (
        <div className="min-h-screen pb-6" style={{ backgroundColor: 'var(--color-bg)', color: 'var(--color-text)' }}>

            <section
                className="relative overflow-hidden rounded-3xl border px-6 md:px-10 py-10 md:py-14"
                style={{
                    borderColor: 'var(--color-border)',
                    background: 'radial-gradient(circle at 85% 20%, rgba(59, 130, 246, 0.35), transparent 45%), linear-gradient(135deg, #0f172a 0%, #111827 40%, #0f1115 100%)',
                }}
            >
                <div className="absolute -top-16 -right-10 w-56 h-56 rounded-full blur-3xl" style={{ backgroundColor: 'rgba(59, 130, 246, 0.22)' }} />
                <div className="absolute -bottom-20 left-0 w-64 h-64 rounded-full blur-3xl" style={{ backgroundColor: 'rgba(17, 115, 212, 0.18)' }} />

                <div className="relative z-10 flex flex-col lg:flex-row items-center gap-10">
                    <div className="flex-1">
                        <p className="text-sm uppercase tracking-[0.24em] mb-4" style={{ color: 'rgba(156, 163, 175, 0.95)' }}>
                            Career AI Workspace
                        </p>
                        <h1 className="text-3xl md:text-5xl font-bold leading-tight mb-4">
                            Prepare smarter. Apply faster. Get hired with confidence.
                        </h1>
                        <p className="text-base md:text-lg max-w-2xl mb-8" style={{ color: 'var(--color-subtext)' }}>
                            JobCore combines mock interviews, resume analysis, and job discovery in one focused dashboard.
                        </p>

                        <div className="flex flex-wrap gap-3">
                            <Link
                                to="/mock-interview"
                                className="px-6 py-2.5 rounded-lg font-medium transition"
                                style={{ backgroundColor: 'var(--color-accent)', color: '#ffffff' }}
                            >
                                Start Mock Interview
                            </Link>
                            <Link
                                to="/resume-checker"
                                className="px-6 py-2.5 rounded-lg font-medium transition border"
                                style={{ borderColor: 'var(--color-border)', color: 'var(--color-text)', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}
                            >
                                Check Resume
                            </Link>
                        </div>
                    </div>

                    <div className="w-full max-w-sm rounded-2xl border p-6" style={{ borderColor: 'var(--color-border)', backgroundColor: 'rgba(32, 36, 44, 0.8)' }}>
                        <div className="flex items-center justify-between mb-5">
                            <p className="text-sm" style={{ color: 'var(--color-subtext)' }}>Interview Assistant</p>
                            <span className="text-xs px-2 py-1 rounded-md" style={{ backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd' }}>Online</span>
                        </div>

                        <div className="space-y-3 text-sm">
                            <div className="rounded-lg px-3 py-2" style={{ backgroundColor: 'rgba(59, 130, 246, 0.12)', color: '#bfdbfe' }}>
                                Tell me about yourself in 60 seconds.
                            </div>
                            <div className="rounded-lg px-3 py-2 border" style={{ borderColor: 'var(--color-border)', color: 'var(--color-subtext)' }}>
                                Tip: Use STAR format for your project examples.
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section className="mt-10 grid grid-cols-1 xl:grid-cols-[1.35fr_1fr] gap-5">
                <div className="rounded-2xl border p-4 md:p-5" style={{ backgroundColor: 'var(--color-card)', borderColor: 'var(--color-border)' }}>
                    <div className="flex items-start justify-between gap-4 mb-4">
                        <div>
                            <h2 className="text-2xl font-semibold">Project Overview</h2>
                            <p className="text-sm mt-1" style={{ color: 'var(--color-subtext)' }}>
                                Watch how JobCore works from preparation to application.
                            </p>
                        </div>
                        <span className="text-xs px-2.5 py-1 rounded-md" style={{ backgroundColor: 'rgba(59, 130, 246, 0.14)', color: '#93c5fd' }}>
                            2-3 min demo
                        </span>
                    </div>

                    <div className="overflow-hidden rounded-xl border" style={{ borderColor: 'var(--color-border)' }}>
                        <video
                            className="w-full h-[220px] md:h-[360px] object-cover"
                            controls
                            preload="metadata"
                            poster="/media/homepage-preview.png"
                        >
                            <source src="/CSE499-Final-Demo.mp4" type="video/mp4" />
                            Your browser does not support the project overview video.
                        </video>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-3">
                        <a
                            href="/CSE499-Final-Demo.mp4"
                            target="_blank"
                            rel="noreferrer"
                            className="px-4 py-2 rounded-lg text-sm font-medium transition"
                            style={{ backgroundColor: 'var(--color-accent)', color: '#fff' }}
                        >
                            Watch Full Video
                        </a>
                        <Link
                            to="/dashboard"
                            className="px-4 py-2 rounded-lg text-sm font-medium border transition"
                            style={{ borderColor: 'var(--color-border)', color: 'var(--color-text)' }}
                        >
                            Go to Dashboard
                        </Link>
                    </div>
                </div>

                <div className="rounded-2xl border p-6" style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
                    <h3 className="text-xl font-semibold mb-4">How It Works</h3>
                    <div className="space-y-3">
                        {howItWorks.map((step, index) => (
                            <div
                                key={step}
                                className="rounded-xl border px-4 py-3 flex gap-3 items-start"
                                style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-card)' }}
                            >
                                <span
                                    className="w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center mt-0.5"
                                    style={{ backgroundColor: 'rgba(59, 130, 246, 0.16)', color: '#bfdbfe' }}
                                >
                                    {index + 1}
                                </span>
                                <p className="text-sm leading-6" style={{ color: 'var(--color-subtext)' }}>
                                    {step}
                                </p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-5 rounded-xl p-4" style={{ backgroundColor: 'rgba(59, 130, 246, 0.08)' }}>
                        <p className="text-sm mb-3" style={{ color: '#bfdbfe' }}>
                            Ready to improve your interview confidence today?
                        </p>
                        <Link
                            to="/mock-interview"
                            className="inline-block px-4 py-2 rounded-lg text-sm font-medium transition"
                            style={{ backgroundColor: 'var(--color-accent)', color: '#fff' }}
                        >
                            Start Now
                        </Link>
                    </div>
                </div>
            </section>

            <section className="mt-10">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {quickActions.map((action) => (
                        <div
                            key={action.title}
                            className="rounded-2xl border overflow-hidden"
                            style={{ backgroundColor: 'var(--color-card)', borderColor: 'var(--color-border)' }}
                        >
                            <div className="relative h-40">
                                <img src={action.image} alt={`${action.title} preview`} className="w-full h-full object-cover" />
                                <div
                                    className="absolute inset-0"
                                    style={{ background: 'linear-gradient(180deg, rgba(15,17,21,0.1) 0%, rgba(15,17,21,0.78) 100%)' }}
                                />
                                <div className="absolute top-3 right-3 w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold" style={{ backgroundColor: 'rgba(59,130,246,0.2)', color: '#bfdbfe' }}>
                                    {action.badge}
                                </div>
                            </div>

                            <div className="p-6">
                                <h3 className="text-xl font-semibold mb-2">{action.title}</h3>
                                <p className="text-sm mb-5 max-w-md" style={{ color: 'var(--color-subtext)' }}>
                                    {action.description}
                                </p>
                                <Link
                                    to={action.to}
                                    className="inline-block text-sm px-4 py-2 rounded-lg font-medium transition"
                                    style={{ backgroundColor: 'var(--color-accent)', color: '#ffffff' }}
                                >
                                    {action.cta}
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            <section className="mt-10 rounded-2xl border p-6 md:p-8" style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
                <h2 className="text-2xl font-semibold mb-6">Why JobCore</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="rounded-xl border p-5" style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-card)' }}>
                        <p className="text-sm mb-2" style={{ color: '#93c5fd' }}>Realistic Practice</p>
                        <p className="text-sm" style={{ color: 'var(--color-subtext)' }}>
                            Get role-specific interview prompts that mirror real hiring conversations.
                        </p>
                    </div>
                    <div className="rounded-xl border p-5" style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-card)' }}>
                        <p className="text-sm mb-2" style={{ color: '#93c5fd' }}>Resume Intelligence</p>
                        <p className="text-sm" style={{ color: 'var(--color-subtext)' }}>
                            Identify weak sections quickly and receive practical improvements.
                        </p>
                    </div>
                    <div className="rounded-xl border p-5" style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-card)' }}>
                        <p className="text-sm mb-2" style={{ color: '#93c5fd' }}>Faster Job Search</p>
                        <p className="text-sm" style={{ color: 'var(--color-subtext)' }}>
                            Use AI job matching and one place to manage career growth tasks.
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Home;