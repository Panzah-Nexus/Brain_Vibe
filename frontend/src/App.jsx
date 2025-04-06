import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProjectsList from './pages/ProjectsList';
import ProjectDetails from './pages/ProjectDetails';
import MasterBrainPage from './pages/MasterBrainPage';
import CLIDocsPage from './pages/CLIDocsPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="content">
          <Routes>
            <Route path="/" element={<Navigate to="/projects" replace />} />
            <Route path="/projects" element={<ProjectsList />} />
            <Route path="/projects/:projectId" element={<ProjectDetails />} />
            <Route path="/master-brain" element={<MasterBrainPage />} />
            <Route path="/cli-docs" element={<CLIDocsPage />} />
            {/* Future routes will go here */}
          </Routes>
        </div>
        <footer className="app-footer">
          <p>Brain Vibe - Learning Topic Tracking for AI-Generated Code</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
