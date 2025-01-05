import React from 'react';
import { Link } from 'react-router-dom';  // Import Link from react-router-dom
import './navbar.css';

const Navbar = () => {
  return (
    <div className="navbar">
      <div className="logo">
        <Link to="/">
          LLM Analyzer
        </Link>
      </div>
    </div>
  );
}

export default Navbar;
