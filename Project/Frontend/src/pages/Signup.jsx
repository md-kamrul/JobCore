import { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from "../provider/AuthProvider";

export default function Signup() {
  const { createUser, loginWithGoogle } = useContext(AuthContext);
  const navigate = useNavigate();
  const [registerError, setRegisterError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setRegisterError("");
    setSuccessMsg("");
    setLoading(true);

    const { data, error } = await createUser(email, password, fullName);

    setLoading(false);

    if (error) {
      if (error.message.includes("already registered")) {
        setRegisterError("This email already has an account.");
      } else {
        setRegisterError(error.message);
      }
      return;
    }

    // Supabase may require email confirmation depending on your settings.
    // If email confirmation is OFF, user is logged in immediately.
    if (data.session) {
      navigate('/');
    } else {
      setSuccessMsg("Account created! Please check your email to confirm your account.");
    }
  };

  const handleGoogle = async () => {
    const { error } = await loginWithGoogle();
    if (error) setRegisterError(error.message);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d1117] text-white">
      <div className="w-full max-w-md bg-[#161b22] p-8 rounded-2xl shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-8">Create an Account</h1>

        <form className="space-y-5" onSubmit={handleSignup}>
          <div>
            <label className="block mb-1 text-sm">Full Name</label>
            <input
              type="text"
              placeholder="Enter your full name"
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block mb-1 text-sm">Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block mb-1 text-sm">Password</label>
            <input
              type="password"
              placeholder="Create a password (min. 6 characters)"
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {registerError && (
            <p className="text-red-400 text-sm bg-red-900/20 border border-red-800 rounded-lg px-3 py-2">
              {registerError}
            </p>
          )}

          {successMsg && (
            <p className="text-green-400 text-sm bg-green-900/20 border border-green-800 rounded-lg px-3 py-2">
              {successMsg}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 rounded-lg font-semibold transition"
          >
            {loading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <div className="flex items-center my-6">
          <hr className="flex-grow border-gray-600" />
          <span className="mx-2 text-gray-400">or</span>
          <hr className="flex-grow border-gray-600" />
        </div>

        <button
          onClick={handleGoogle}
          className="w-full flex items-center justify-center gap-2 bg-[#0d1117] border border-gray-600 py-2 rounded-lg hover:bg-gray-800 transition"
        >
          <i className="fa fa-google"></i> Continue with Google
        </button>

        <p className="text-center text-sm text-gray-400 mt-6">
          Have an account?{" "}
          <a href="/login" className="text-blue-400 hover:underline">Log In</a>
        </p>
      </div>
    </div>
  );
}