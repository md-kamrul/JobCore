import React from "react";
import { FaBell, FaUser, FaBriefcase } from "react-icons/fa";

const ProfileSection = () => {
    return (
        <main className="flex flex-col md:flex-row p-8 gap-6 text-white min-h-screen">
            {/* Left Sidebar */}
            <div className="w-full md:w-1/4 flex flex-col gap-6">

                <div className="bg-gray-800 rounded-2xl p-6 space-y-6">
                    <div className="text-center">
                        <div className="w-24 h-24 bg-gray-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                            <FaUser className="text-3xl text-gray-300" />
                        </div>
                        <h2 className="text-lg font-semibold">Farhan Ishraque</h2>
                        <p className="text-gray-400 text-sm mb-2">farhan.ishraque@email.com</p>
                        <p className="text-gray-400 text-sm">
                            Passionate product designer with a knack for creating intuitive and
                            delightful user experiences.
                        </p>
                        <button className="mt-4 w-full py-2 rounded-lg text-sm font-medium">
                            Edit Profile
                        </button>
                    </div>
                </div>
                {/* Preferences */}
                <div className="bg-gray-700 p-4 rounded-xl space-y-4">
                    <h3 className="font-semibold">Preferences</h3>
                    <div>
                        <p className="text-gray-400 text-xs">Desired Role</p>
                        <div className="bg-gray-800 py-1 px-2 rounded-md text-sm mt-1">
                            Product Designer
                        </div>
                    </div>
                    <div>
                        <p className="text-gray-400 text-xs">Location</p>
                        <div className="bg-gray-800 py-1 px-2 rounded-md text-sm mt-1">
                            Remote, San Francisco
                        </div>
                    </div>
                    <div>
                        <p className="text-gray-400 text-xs">Salary Expectation</p>
                        <div className="bg-gray-800 py-1 px-2 rounded-md text-sm mt-1">
                            $120,000 - $150,000
                        </div>
                    </div>
                    <div className="flex items-center justify-between mt-2">
                        <p className="text-gray-400 text-sm">Open to new opportunities</p>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" className="sr-only peer" defaultChecked />
                            <div className="w-9 h-5 bg-gray-600 rounded-full peer-checked:bg-blue-600 transition-all"></div>
                            <div className="absolute left-1 top-0.5 w-4 h-4 bg-white rounded-full peer-checked:translate-x-4 transition-transform"></div>
                        </label>
                    </div>
                </div>
            </div>

            {/* Right Content */}
            <div className="flex-1 space-y-6">
                {/* Activity Summary */}
                <div className="bg-gray-800 p-6 rounded-2xl">
                    <h3 className="font-semibold mb-4">Activity Summary</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center mb-6">
                        <div className="bg-[#1173d4a1] p-6 rounded-2xl">
                            <p className="text-2xl font-bold text-blue-400">10</p>
                            <p className="text-sm">Total Job Result</p>
                        </div>
                        <div className="bg-[#1173d4a1] p-6 rounded-2xl">
                            <p className="text-2xl font-bold text-blue-400">8</p>
                            <p className="text-sm">Applications Sent</p>
                        </div>
                        <div className="bg-[#1173d4a1] p-6 rounded-2xl">
                            <p className="text-2xl font-bold text-blue-400">2</p>
                            <p className="text-sm">Mock Interview</p>
                        </div>
                    </div>

                    <div className="w-full h-auto bg-[#0c1927] rounded-xl flex items-center justify-center text-gray-500">
                        <img src="./33c047a9-675d-44e7-af4e-85d07b88bc2b.jpeg" alt="Graph" />
                    </div>
                </div>

                {/* Notifications */}
                <div className="bg-gray-800 p-6 rounded-2xl">
                    <h3 className="font-semibold mb-4">Recent Notifications</h3>
                    <div className="space-y-4">
                        {[
                            {
                                title: "New job match: Senior Product Designer at TechCorp",
                                time: "Just now",
                            },
                            {
                                title: "Interview reminder: Innovate LLC tomorrow at 10:00 AM",
                                time: "1 day ago",
                            },
                            {
                                title:
                                    "Your application for UI/UX Designer at CreativeMinds was viewed.",
                                time: "3 days ago",
                            },
                        ].map((item, i) => (
                            <div
                                key={i}
                                className="bg-gray-700 p-4 rounded-xl flex items-start space-x-3"
                            >
                                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                                    <FaBriefcase className="text-white text-sm" />
                                </div>
                                <div>
                                    <p className="text-sm">{item.title}</p>
                                    <p className="text-xs text-gray-400">{item.time}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </main>
    );
};

export default ProfileSection;
