import { Outlet } from 'react-router';
import Header from '../components/Header';

const Main = () => {
    return (
        <div className="w-[80%] mx-auto text-white">
            <Header></Header>
            <Outlet></Outlet>
        </div>
    );
};

export default Main;