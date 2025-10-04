import React from "react";
import { Link } from "react-router-dom";
import "./Header.css"; 
import ailogo from '../assets/img/ai-logo.png';
const Header = () => {
  return (
    <header className="header">
      <div className="header-left">
        <img
          src={ailogo}
          alt="AI Logo"
          className="ai-logo"
        />
        <h1 className="project-title">CompanionAI</h1>
      </div>

      <div className="header-right">
        <Link to="/" className="login-button">
          Login
        </Link>
      </div>
    </header>
  );
};

export default Header;