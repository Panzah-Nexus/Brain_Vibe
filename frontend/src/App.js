import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ProjectPage from './pages/ProjectPage';
import AnalyzePage from './pages/AnalyzePage';
import MasterBrainPage from './pages/MasterBrainPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/projects/:projectId" element={<ProjectPage />} />
          <Route path="/projects/:projectId/analyze" element={<AnalyzePage />} />
          <Route path="/master-brain" element={<MasterBrainPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
