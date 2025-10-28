import { Outlet, useLocation } from 'react-router';
import Header from '../components/Header';
import Footer from '../components/Footer';

const Main = () => {

    const location = useLocation();
    // console.log(location);

    return (
        <div className="w-[80%] mx-auto text-white">
            <Header></Header>
            <Outlet></Outlet>
            <Footer></Footer>
        </div>
    );
};

export default Main;