import React from "react";
import { FaUserCircle, FaBell } from "react-icons/fa";
import { AiFillProject } from "react-icons/ai";

const Header = () => {
    return (
        <header
            className="flex items-center justify-between px-8 py-4 bg-transparent"
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
                            Job Search
                        </a>
                    </li>
                    <li>
                        <a href="#" className="text-white px-3 py-1 rounded">
                            Applications
                        </a>
                    </li>
                    <li>
                        <a href="#" className="text-white px-3 py-1 rounded">
                            Interviews
                        </a>
                    </li>
                </ul>
            </nav>

            {/* Icons (Notification + User) */}
            <div className="flex items-center space-x-4">
                <FaBell className="w-5 h-5 text-white hover:text-gray-200 transition" />
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <FaUserCircle className="w-5 h-5 text-white" />
                </div>
            </div>
        </header>
    );
};

export default Header;