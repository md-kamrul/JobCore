import {
  createBrowserRouter,
} from "react-router-dom";
import Main from "../layout/Main";
import Home from "../pages/Home";
import Dashboard from "../pages/Dashboard";
import Login from "../pages/Login";
import Signup from "../pages/Signup";
import Profile from "../pages/Profile";
import JobAgent from "../pages/JobAgent";
import MockInterview from "../pages/MockInterview";
import VoiceMockInterview from "../pages/VoiceMockInterview";
import TextMockInterview from "../components/TextMockInterview";
import ResumeChecker from "../pages/ResumeChecker";
import ProtectedRoute from "./ProtectedRoute";

export const router = createBrowserRouter([
  {
    path: "/",
        element: <Main />,
    children: [
        { path: "/", element: <Home></Home> },
        { path: "/dashboard", element: <Dashboard></Dashboard> },
        { path: "/login", element: <Login></Login> },
        { path: "/signup", element: <Signup></Signup> },
        { path: "/profile", element: <Profile></Profile>},
        {
          path: "/job-agent",
          element: (
            <ProtectedRoute>
              <JobAgent></JobAgent>
            </ProtectedRoute>
          ),
        },
        {
          path: "/mock-interview",
          element: (
            <ProtectedRoute>
              <MockInterview></MockInterview>
            </ProtectedRoute>
          ),
        },
        {
          path: "/mock-interview/voice",
          element: (
            <ProtectedRoute>
              <VoiceMockInterview></VoiceMockInterview>
            </ProtectedRoute>
          ),
        },
        {
          path: "/mock-interview/text",
          element: (
            <ProtectedRoute>
              <TextMockInterview></TextMockInterview>
            </ProtectedRoute>
          ),
        },
        {
          path: "/resume-checker",
          element: (
            <ProtectedRoute>
              <ResumeChecker></ResumeChecker>
            </ProtectedRoute>
          ),
        },
    ],
  },
]);