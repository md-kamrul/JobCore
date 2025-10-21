import React, { useState } from "react";
import { FaEye, FaEyeSlash, FaGoogle } from "react-icons/fa";

const Signup = () => {
  const [showPassword, setShowPassword] = useState(false);

  const togglePassword = () => setShowPassword(!showPassword);

  const handleSignup = (e) => {
    e.preventDefault();
    alert("Signup form submitted!");
  };

  const handleGoogleSignup = () => {
    alert("Connect with Google clicked!");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d1117] text-white">
      <div className="w-full max-w-md bg-[#161b22] p-8 rounded-2xl shadow-lg">
        {/* Title */}
        <h1 className="text-4xl font-bold text-center text-blue-500 mb-2">
          JobCore
        </h1>
        <h2 className="text-2xl font-semibold text-center mb-8 text-gray-300">
          Create an Account
        </h2>

        <form onSubmit={handleSignup} className="space-y-5">
          {/* Full Name */}
          <div>
            <label className="block mb-1 text-sm text-gray-400">Full Name</label>
            <input
              type="text"
              placeholder="Enter your full name"
              required
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block mb-1 text-sm text-gray-400">Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              required
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Date of Birth */}
          <div>
            <label className="block mb-1 text-sm text-gray-400">Date of Birth</label>
            <input
              type="date"
              required
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Password */}
          <div className="relative">
            <label className="block mb-1 text-sm text-gray-400">Password</label>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Create a password"
              required
              className="w-full px-4 py-2 pr-10 rounded-lg bg-[#0d1117] border border-gray-600 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            <span
              onClick={togglePassword}
              className="absolute right-3 top-9 cursor-pointer text-gray-400 hover:text-blue-500"
            >
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </span>
          </div>

          {/* Sign Up Button */}
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-semibold transition"
          >
            Sign Up
          </button>
        </form>

        {/* Divider */}
        <div className="flex items-center my-6">
          <hr className="flex-grow border-gray-600" />
          <span className="mx-2 text-gray-400 text-sm">or</span>
          <hr className="flex-grow border-gray-600" />
        </div>

        {/* Google Signup */}
        <button
          type="button"
          onClick={handleGoogleSignup}
          className="w-full flex items-center justify-center gap-2 bg-[#0d1117] border border-gray-600 py-2 rounded-lg hover:bg-gray-800 transition"
        >
          <FaGoogle className="text-red-500" /> Continue with Google
        </button>

        {/* Login Redirect */}
        <p className="text-center text-sm text-gray-400 mt-6">
          Already have an account?{" "}
          <a href="/login" className="text-blue-400 hover:underline">
            Log in
          </a>
        </p>
      </div>
    </div>
  );
};

export default Signup;
