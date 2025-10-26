import React, { useState } from "react";
import { FaUserCircle, FaBell, FaBars, FaTimes } from "react-icons/fa";
import { AiFillProject } from "react-icons/ai";

const Header = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <header
            className="flex items-center justify-between px-6 md:px-8 py-4 bg-transparent mb-6 relative"
            style={{ borderBottom: "1px solid var(--color-border)" }}
        >
            {/* Logo Section */}
            <div className="flex items-center space-x-2">
                <a href="/" className="text-white px-3 py-1 rounded hover:text-gray-300">
                    <AiFillProject className="w-6 h-6 text-[#1173d4]" />
                    <span className="font-semibold text-lg text-white">JobCore</span>
                </a>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:block" aria-label="Main navigation">
                <ul className="flex items-center space-x-4">
                    <li>
                        <a href="/" className="text-white px-3 py-1 rounded hover:text-gray-300">
                            Home
                        </a>
                    </li>
                    <li>
                        <a href="/dashboard" className="text-white px-3 py-1 rounded hover:text-gray-300">
                            Dashboard
                        </a>
                    </li>
                    <li>
                        <a href="/job-agent" className="text-white px-3 py-1 rounded hover:text-gray-300">
                            Job Agent
                        </a>
                    </li>
                    <li>
                        <a href="/resume-checker" className="text-white px-3 py-1 rounded hover:text-gray-300">
                            Resume Checker
                        </a>
                    </li>
                    <li>
                        <a href="/mock-interview" className="text-white px-3 py-1 rounded hover:text-gray-300">
                            Mock Interviews
                        </a>
                    </li>
                </ul>
            </nav>

            {/* Right Icons */}
            <div className="flex items-center space-x-4">
                <FaBell className="w-5 h-5 text-white hover:text-gray-200 transition cursor-pointer" />
                <a
                    href="/profile"
                    className="flex items-center justify-center w-8 h-8 bg-gray-600 rounded-full hover:bg-gray-500 transition"
                >
                    <FaUserCircle className="w-5 h-5 text-white" />
                </a>

                {/* Mobile Menu Button */}
                <button
                    className="md:hidden text-white text-xl"
                    onClick={() => setIsOpen(!isOpen)}
                    aria-label="Toggle navigation"
                >
                    {isOpen ? <FaTimes /> : <FaBars />}
                </button>
            </div>

            {/* Mobile Navigation Menu */}
            {isOpen && (
                <div className="absolute top-full left-0 w-full bg-gray-800 border-t border-gray-700 md:hidden z-50">
                    <ul className="flex flex-col items-start p-4 space-y-3">
                        <li>
                            <a
                                href="/"
                                className="block w-full text-white py-2 px-2 rounded hover:bg-gray-700"
                                onClick={() => setIsOpen(false)}
                            >
                                Home
                            </a>
                        </li>
                        <li>
                            <a
                                href="/dashboard"
                                className="block w-full text-white py-2 px-2 rounded hover:bg-gray-700"
                                onClick={() => setIsOpen(false)}
                            >
                                Dashboard
                            </a>
                        </li>
                        <li>
                            <a
                                href="#"
                                className="block w-full text-white py-2 px-2 rounded hover:bg-gray-700"
                                onClick={() => setIsOpen(false)}
                            >
                                Job Agent
                            </a>
                        </li>
                        <li>
                            <a
                                href="#"
                                className="block w-full text-white py-2 px-2 rounded hover:bg-gray-700"
                                onClick={() => setIsOpen(false)}
                            >
                                Resume Checker
                            </a>
                        </li>
                        <li>
                            <a
                                href="#"
                                className="block w-full text-white py-2 px-2 rounded hover:bg-gray-700"
                                onClick={() => setIsOpen(false)}
                            >
                                Mock Interviews
                            </a>
                        </li>
                    </ul>
                </div>
            )}
        </header>
    );
};

export default Header;
