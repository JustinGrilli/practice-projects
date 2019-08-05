import React from "react";
import { NavLink, Link } from "react-router-dom";

// Stateless Functional Component -- sfc
const Navbar = ({ totalCounters }) => {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      {/* <div className="collapse navbar-collapse" id="navbarNavAltMarkup"> */}
      <div className="navbar-nav">
        <Link to="/" className="nav-item nav-link">
          Vidly
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#nacbarNavAltMarkup"
          aria-controls="nacbarNavAltMarkup"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>
        <NavLink to="/movies" className="nav-item nav-link">
          Movies
        </NavLink>
        <NavLink to="/customers" className="nav-item nav-link">
          Customers
        </NavLink>
        <NavLink to="/rentals" className="nav-item nav-link">
          Rentals
        </NavLink>
        <NavLink to="/login" className="nav-item nav-link">
          Login
        </NavLink>
        <NavLink to="/register" className="nav-item nav-link">
          Register
        </NavLink>
      </div>
      {/* </div> */}
    </nav>
  );
};

export default Navbar;
