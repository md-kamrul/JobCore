import { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from "../provider/AuthProvider";

export default function Signup() {

  const { createUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [registerError, setRegisterError] = useState("");
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignup = (e) => {
    e.preventDefault();

    console.log({
      fullName,
      email,
      password
    });

    setRegisterError("");
    createUser(email, password)
      .then(result => {
        console.log(result.user);
        navigate(
          location?.state ?
            location.state
            :
            "/"
        )
      })
    .catch(error => {
                if (error.message.indexOf("(auth/email-already-in-use).")) {
                    setRegisterError("This email already have an account...");
                }
            })

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
            placeholder="Create a password"
            className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-semibold transition"
        >
          Sign Up
        </button>
      </form>

      <div className="flex items-center my-6">
        <hr className="flex-grow border-gray-600" />
        <span className="mx-2 text-gray-400">or</span>
        <hr className="flex-grow border-gray-600" />
      </div>

      {/* Google Login Button */}
      <button className="w-full flex items-center justify-center gap-2 bg-[#0d1117] border border-gray-600 py-2 rounded-lg hover:bg-gray-800 transition">
        <i className="fa fa-google"></i> Continue with Google
      </button>

      <p className="text-center text-sm text-gray-400 mt-6">
        Have an account?{" "}
        <a href="/login" className="text-blue-400 hover:underline">
          Log In
        </a>
      </p>
    </div>
  </div>
);
}