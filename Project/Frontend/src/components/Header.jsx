import React, { useState } from "react";
import { FaUserCircle, FaBell, FaBars, FaTimes } from "react-icons/fa";
import { AiFillProject } from "react-icons/ai";
import { NavLink } from "react-router-dom"; // Import from react-router-dom

const Header = () => {
    const [isOpen, setIsOpen] = useState(false);

    // Function to generate class names for NavLink (active and hover states)
    const getNavLinkClass = ({ isActive }) =>
        `text-white px-3 py-1 rounded transition ${
            isActive ? "bg-blue-500" : "hover:text-gray-300"
        }`;

    // For mobile: separate class to handle block-level styling
    const getMobileNavLinkClass = ({ isActive }) =>
        `block w-full text-white py-2 px-2 rounded transition ${
            isActive ? "bg-[#1e2938]" : "hover:bg-gray-700"
        }`;

    return (
        <header
            className="flex items-center justify-between px-6 md:px-8 py-4 bg-transparent mb-6 relative"
            style={{ borderBottom: "1px solid var(--color-border)" }}
        >
            {/* Logo Section */}
            <NavLink to="/" className="text-white px-3 py-1 rounded hover:text-gray-300">
                <div className="flex items-center space-x-2">
                    <AiFillProject className="w-6 h-6 text-[#1173d4]" />
                    <span className="font-semibold text-lg text-white">JobCore</span>
                </div>
            </NavLink>

            {/* Desktop Navigation */}
            <nav className="hidden md:block" aria-label="Main navigation">
                <ul className="flex items-center space-x-4">
                    <li>
                        <NavLink to="/" className={getNavLinkClass}>
                            Home
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/dashboard" className={getNavLinkClass}>
                            Dashboard
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/job-agent" className={getNavLinkClass}>
                            Job Agent
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/resume-checker" className={getNavLinkClass}>
                            Resume Checker
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/mock-interview" className={getNavLinkClass}>
                            Mock Interviews
                        </NavLink>
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
                            <NavLink
                                to="/"
                                className={getMobileNavLinkClass}
                                onClick={() => setIsOpen(false)}
                            >
                                Home
                            </NavLink>
                        </li>
                        <li>
                            <NavLink
                                to="/dashboard"
                                className={getMobileNavLinkClass}
                                onClick={() => setIsOpen(false)}
                            >
                                Dashboard
                            </NavLink>
                        </li>
                        <li>
                            <NavLink
                                to="/job-agent"
                                className={getMobileNavLinkClass}
                                onClick={() => setIsOpen(false)}
                            >
                                Job Agent
                            </NavLink>
                        </li>
                        <li>
                            <NavLink
                                to="/resume-checker"
                                className={getMobileNavLinkClass}
                                onClick={() => setIsOpen(false)}
                            >
                                Resume Checker
                            </NavLink>
                        </li>
                        <li>
                            <NavLink
                                to="/mock-interview"
                                className={getMobileNavLinkClass}
                                onClick={() => setIsOpen(false)}
                            >
                                Mock Interviews
                            </NavLink>
                        </li>
                    </ul>
                </div>
            )}
        </header>
    );
};

export default Header;