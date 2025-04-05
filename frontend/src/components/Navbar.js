import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();
  
  // Helper function to check if a link is active
  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') {
      return true;
    }
    
    if (path !== '/' && location.pathname.startsWith(path)) {
      return true;
    }
    
    return false;
  };

  return (
    <nav style={{ 
      backgroundColor: '#343a40',
      color: 'white',
      padding: '15px 20px',
      marginBottom: '30px'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div>
          <Link 
            to="/"
            style={{ 
              color: 'white', 
              textDecoration: 'none',
              fontSize: '1.5rem',
              fontWeight: 'bold'
            }}
          >
            Brain Vibe
          </Link>
        </div>
        
        <div style={{ display: 'flex' }}>
          <Link 
            to="/"
            style={{ 
              color: 'white', 
              textDecoration: 'none',
              padding: '8px 12px',
              borderRadius: '4px',
              backgroundColor: isActive('/') ? '#6c757d' : 'transparent',
              marginRight: '10px'
            }}
          >
            Projects
          </Link>
          
          <Link 
            to="/master-brain"
            style={{ 
              color: 'white', 
              textDecoration: 'none',
              padding: '8px 12px',
              borderRadius: '4px',
              backgroundColor: isActive('/master-brain') ? '#6c757d' : 'transparent'
            }}
          >
            Master Brain
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 