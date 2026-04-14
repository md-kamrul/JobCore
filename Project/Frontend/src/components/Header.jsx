import React, { useContext, useState } from "react";
import { FaUserCircle, FaBars, FaTimes } from "react-icons/fa";
import { IoMdLogOut } from "react-icons/io";
import { AiFillProject } from "react-icons/ai";
import { NavLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../provider/AuthProvider";

const Header = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    const navigate = useNavigate();
    const { user, logoutUser } = useContext(AuthContext);

    const getNavLinkClass = ({ isActive }) =>
        `text-white px-3 py-1 rounded transition ${
            isActive ? "bg-blue-500" : "hover:text-gray-300"
        }`;

    const getMobileNavLinkClass = ({ isActive }) =>
        `block w-full text-white py-2 px-2 rounded transition ${
            isActive ? "bg-[#1e2938]" : "hover:bg-gray-700"
        }`;

    const handleLogout = async () => {
        if (isLoggingOut) return;

        setIsLoggingOut(true);
        const { error } = await logoutUser();
        setIsLoggingOut(false);

        if (error) {
            console.error("Logout failed:", error.message);
            return;
        }

        setIsOpen(false);
        navigate("/login", { replace: true });
    };

    return (
        <header
            className="flex items-center justify-between px-6 md:px-8 py-4 bg-transparent mb-6 relative"
            style={{ borderBottom: "1px solid var(--color-border)" }}
        >
            <NavLink to="/" className="text-white px-3 py-1 rounded hover:text-gray-300">
                <div className="flex items-center space-x-2">
                    <AiFillProject className="w-6 h-6 text-[#1173d4]" />
                    <span className="font-semibold text-lg text-white">JobCore</span>
                </div>
            </NavLink>

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

            <div className="flex items-center space-x-4">
                {user ? (
                    <div className="flex items-center gap-2">
                        <NavLink
                            to="/profile"
                            className="flex items-center justify-center w-8 h-8 bg-gray-600 rounded-full hover:bg-gray-500 transition"
                            aria-label="Go to profile"
                        >
                            <FaUserCircle className="w-5 h-5 text-white" />
                        </NavLink>
                        <button
                            onClick={handleLogout}
                            disabled={isLoggingOut}
                            className=""
                            aria-label="Logout"
                            title="Logout"
                        >
                            <IoMdLogOut  className="w-5 h-5 text-white" />
                        </button>
                    </div>
                ) : (
                    <div className="hidden md:flex items-center gap-2">
                        <NavLink to="/login" className="text-white px-3 py-1 rounded hover:text-gray-300">
                            Login
                        </NavLink>
                        <NavLink to="/signup" className="text-white px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 transition">
                            Sign Up
                        </NavLink>
                    </div>
                )}

                <button
                    className="md:hidden text-white text-xl"
                    onClick={() => setIsOpen(!isOpen)}
                    aria-label="Toggle navigation"
                >
                    {isOpen ? <FaTimes /> : <FaBars />}
                </button>
            </div>

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
                        {user ? (
                            <>
                                <li className="w-full">
                                    <NavLink
                                        to="/profile"
                                        className={getMobileNavLinkClass}
                                        onClick={() => setIsOpen(false)}
                                    >
                                        Profile
                                    </NavLink>
                                </li>
                                <li className="w-full">
                                    <button
                                        onClick={handleLogout}
                                        disabled={isLoggingOut}
                                        className="block w-full text-left text-red-300 py-2 px-2 rounded transition hover:bg-gray-700 disabled:opacity-60"
                                    >
                                        {isLoggingOut ? "Logging out..." : "Logout"}
                                    </button>
                                </li>
                            </>
                        ) : (
                            <>
                                <li className="w-full">
                                    <NavLink
                                        to="/login"
                                        className={getMobileNavLinkClass}
                                        onClick={() => setIsOpen(false)}
                                    >
                                        Login
                                    </NavLink>
                                </li>
                                <li className="w-full">
                                    <NavLink
                                        to="/signup"
                                        className={getMobileNavLinkClass}
                                        onClick={() => setIsOpen(false)}
                                    >
                                        Sign Up
                                    </NavLink>
                                </li>
                            </>
                        )}
                    </ul>
                </div>
            )}
        </header>
    );
};

export default Header;