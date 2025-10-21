export default function Signup() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d1117] text-white">
      <div className="w-full max-w-md bg-[#161b22] p-8 rounded-2xl shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-8">Create an Account</h1>

        <form className="space-y-5">
          <div>
            <label className="block mb-1 text-sm">Full Name</label>
            <input
              type="text"
              placeholder="Enter your full name"
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block mb-1 text-sm">Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block mb-1 text-sm">Password</label>
            <input
              type="password"
              placeholder="Create a password"
              className="w-full px-4 py-2 rounded-lg bg-[#0d1117] border border-gray-600 focus:outline-none focus:border-blue-500"
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
      </div>
    </div>
  );
}
