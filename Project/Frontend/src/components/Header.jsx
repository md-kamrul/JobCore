import React from "react";
import { FaUserCircle, FaBell } from "react-icons/fa";
import { AiFillProject } from "react-icons/ai";

const Header = () => {
    return (
        <header
            className="flex items-center justify-between px-8 py-4 bg-transparent mb-6"
            style={{ borderBottom: "1px solid var(--color-border)" }}
        >
            {/* Logo Section */}
            <div className="flex items-center space-x-2">
                <AiFillProject className="w-6 h-6 text-[#1173d4]" />
                <span className="font-semibold text-lg text-white">JobCore</span>
            </div>

            {/* Navigation Links - simplified */}
            <nav aria-label="Main navigation">
                <ul className="flex items-center space-x-4">
                    <li>
                        <a href="/" className="text-white px-3 py-1 rounded">
                            Home
                        </a>
                    </li>
                    <li>
                        <a href="/dashboard" className="text-white px-3 py-1 rounded">
                            Dashboard
                        </a>
                    </li>
                    <li>
                        <a href="#" className="text-white px-3 py-1 rounded">
                            Job Agent
                        </a>
                    </li>
                    <li>
                        <a href="#" className="text-white px-3 py-1 rounded">
                            Resume Checker
                        </a>
                    </li>
                    <li>
                        <a href="#" className="text-white px-3 py-1 rounded">
                            Mock Interviews
                        </a>
                    </li>
                </ul>
            </nav>

            {/* Icons (Notification + User) */}
            <div className="flex items-center space-x-4">
                <FaBell className="w-5 h-5 text-white hover:text-gray-200 transition pointer" />
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <a href="/profile" className="text-white px-3 py-1 rounded">
                        <FaUserCircle className="w-5 h-5 text-white pointer" />
                    </a>
                </div>
            </div>
        </header>
    );
};

export default Header;