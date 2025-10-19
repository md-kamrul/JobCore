import {
  createBrowserRouter,
} from "react-router-dom";
import Main from "../layout/Main";
import Home from "../pages/Home";
import Dashboard from "../pages/Dashboard";
import Login from "../pages/Login";
import Signup from "../pages/Signup";
import Profile from "../pages/Profile";

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
    ],
  },
]);