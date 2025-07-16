import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [sticky, setSticky] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setSticky(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className={`navbar ${sticky ? 'dark-nav' : ''}`}>
      <div className="nav-logo">
        <p>African <span>Research Hub</span></p>
      </div>

      <ul className="nav-menu">
        <li>
          <Link to="/" onClick={() => setMenuOpen(false)} style={{ textDecoration: 'none' }}>
            Home
          </Link>
        </li>
         <li>
          <Link to="/" onClick={() => setMenuOpen(false)} style={{ textDecoration: 'none' }}>
            About 
          </Link>
        </li>
        <li>
          <Link to="/Payment" onClick={() => setMenuOpen(false)} style={{ textDecoration: 'none' }}>
            Payment
          </Link>
        </li>
         <li>
          <Link to="/" onClick={() => setMenuOpen(false)} style={{ textDecoration: 'none' }}>
            Student 
          </Link>
        </li>
        <li>
          <Link to="/AdminDashboard" onClick={() => setMenuOpen(false)} style={{ textDecoration: 'none' }}>
            Admin 
          </Link>
        </li>
        <li>
          <Link to="/Impacts" onClick={() => setMenuOpen(false)} style={{ textDecoration: 'none' }}>
            Blog
          </Link>
        </li>
        <li>
          <button className="sign-in-button">Sign In</button>
        </li>
      </ul>
    </div>
  );
};

export default Navbar;
