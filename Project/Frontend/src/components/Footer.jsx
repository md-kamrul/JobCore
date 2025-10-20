import React from "react";

const Footer = () => {
    const currentYear = new Date().getFullYear();
    return (
        <footer className="text-center text-gray-500 text-sm py-6 border-t border-gray-700 mt-6">
            © {currentYear} JobCore. All rights reserved. ·{" "}
            <a href="#" className="hover:text-white">
                Support
            </a>{" "}
            ·{" "}
            <a href="#" className="hover:text-white">
                Privacy Policy
            </a>{" "}
            ·{" "}
            <a href="#" className="hover:text-white">
                Terms of Service
            </a>
        </footer>
    );
};

export default Footer;
