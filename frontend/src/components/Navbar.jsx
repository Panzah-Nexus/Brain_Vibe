import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <Link to="/">Brain Vibe</Link>
      </div>
      <ul className="navbar-links">
        <li>
          <Link to="/projects">Projects</Link>
        </li>
        <li>
          <Link to="/master-brain">Master Brain</Link>
        </li>
        {/* Placeholder for future nav items */}
        <li className="disabled">
          <span>Analytics</span>
        </li>
        <li className="disabled">
          <span>Settings</span>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar; 