import React, { useState } from 'react';
import { analyzeDiff } from '../services/api';

const CodeDiffAnalyzer = ({ projectId, onAnalysisComplete }) => {
  const [formData, setFormData] = useState({
    git_diff: '',
    prompt: '',
    ai_output: '',
    exclude_patterns: 'node_modules,package-lock.json,yarn.lock,.git'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Clear error when user types
    if (error) setError('');
  };

  const handlePaste = (e) => {
    const { name } = e.target;
    const pastedText = e.clipboardData.getData('text');
    setFormData({ ...formData, [name]: pastedText });
    e.preventDefault(); // Prevent the default paste behavior
    
    // Clear error when user pastes
    if (error) setError('');
  };

  const filterGitDiff = (diff, excludePatterns) => {
    if (!diff || !excludePatterns) return diff;
    
    const patterns = excludePatterns.split(',').map(p => p.trim()).filter(p => p);
    if (patterns.length === 0) return diff;
    
    // Split diff by file sections
    const lines = diff.split('\n');
    const filteredLines = [];
    let includeCurrentFile = true;
    let currentFilePath = '';
    
    for (let line of lines) {
      // Check if this is a file header line
      if (line.startsWith('diff --git')) {
        currentFilePath = line.split(' ')[2].substring(2); // Extract file path
        
        // Check if this file should be excluded
        includeCurrentFile = !patterns.some(pattern => 
          currentFilePath.includes(pattern)
        );
        
        // Only add this line if we're including the file
        if (includeCurrentFile) {
          filteredLines.push(line);
        }
      } 
      // Only add lines for files we're including
      else if (includeCurrentFile || line.startsWith('diff --git')) {
        filteredLines.push(line);
      }
    }
    
    return filteredLines.join('\n');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate git_diff
    if (!formData.git_diff.trim()) {
      setError('Git diff is required.');
      return;
    }
    
    try {
      setIsLoading(true);
      setResult(null);
      
      // Filter git diff before sending
      const filteredDiff = filterGitDiff(formData.git_diff, formData.exclude_patterns);
      
      const dataToSend = {
        git_diff: filteredDiff,
        prompt: formData.prompt,
        ai_output: formData.ai_output
      };
      
      const response = await analyzeDiff(projectId, dataToSend);
      
      setResult(response);
      
      // Call callback if provided
      if (onAnalysisComplete) {
        onAnalysisComplete(response);
      }
    } catch (error) {
      console.error('Error analyzing diff:', error);
      setError('Failed to analyze diff. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Analyze Code Diff</h2>
      <p>Submit a Git diff to analyze for new programming concepts.</p>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label 
            htmlFor="git_diff"
            style={{ 
              display: 'block', 
              marginBottom: '5px',
              fontWeight: 'bold'
            }}
          >
            Git Diff*:
          </label>
          <textarea
            id="git_diff"
            name="git_diff"
            value={formData.git_diff}
            onChange={handleInputChange}
            onPaste={handlePaste}
            rows={10}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ced4da',
              fontFamily: 'monospace'
            }}
            placeholder="Paste your git diff here..."
            required
          />
          <p style={{ fontSize: '0.8rem', color: '#6c757d', marginTop: '5px' }}>
            You can use <code>git diff</code> or <code>git show</code> commands to get diff output, then copy and paste it here.
          </p>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label 
            htmlFor="exclude_patterns"
            style={{ 
              display: 'block', 
              marginBottom: '5px',
              fontWeight: 'bold'
            }}
          >
            Exclude Patterns (comma-separated):
          </label>
          <input
            type="text"
            id="exclude_patterns"
            name="exclude_patterns"
            value={formData.exclude_patterns}
            onChange={handleInputChange}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ced4da'
            }}
            placeholder="node_modules,package-lock.json,etc."
          />
          <p style={{ fontSize: '0.8rem', color: '#6c757d', marginTop: '5px' }}>
            Files containing these patterns will be excluded from analysis. Separate patterns with commas.
          </p>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label 
            htmlFor="prompt"
            style={{ 
              display: 'block', 
              marginBottom: '5px',
              fontWeight: 'bold'
            }}
          >
            User Prompt (optional):
          </label>
          <textarea
            id="prompt"
            name="prompt"
            value={formData.prompt}
            onChange={handleInputChange}
            onPaste={handlePaste}
            rows={3}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ced4da'
            }}
            placeholder="What was your prompt to the AI?"
          />
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label 
            htmlFor="ai_output"
            style={{ 
              display: 'block', 
              marginBottom: '5px',
              fontWeight: 'bold'
            }}
          >
            AI Output (optional):
          </label>
          <textarea
            id="ai_output"
            name="ai_output"
            value={formData.ai_output}
            onChange={handleInputChange}
            onPaste={handlePaste}
            rows={5}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ced4da',
              fontFamily: 'monospace'
            }}
            placeholder="What was the AI's response?"
          />
        </div>
        
        {error && (
          <div style={{
            padding: '10px',
            backgroundColor: '#f8d7da',
            color: '#721c24',
            borderRadius: '4px',
            marginBottom: '15px'
          }}>
            {error}
          </div>
        )}
        
        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: '10px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1
          }}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Diff'}
        </button>
      </form>
      
      {result && (
        <div style={{
          marginTop: '30px',
          padding: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px'
        }}>
          <h3 style={{ marginTop: 0 }}>Analysis Results</h3>
          
          {result.new_topics && result.new_topics.length > 0 ? (
            <div>
              <p>Found {result.new_topics.length} new topics:</p>
              <ul style={{
                padding: '0',
                margin: '0',
                listStylePosition: 'inside'
              }}>
                {result.new_topics.map((topic, index) => (
                  <li key={topic.topic_id} style={{
                    padding: '10px',
                    margin: '10px 0',
                    backgroundColor: 'white',
                    borderRadius: '4px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                  }}>
                    <strong>{topic.display_name}</strong>
                    {topic.short_description && (
                      <p style={{ margin: '5px 0' }}>{topic.short_description}</p>
                    )}
                    {topic.prerequisites && topic.prerequisites.length > 0 && (
                      <div style={{ fontSize: '0.9rem' }}>
                        <strong>Prerequisites:</strong> {topic.prerequisites.join(', ')}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p>No new topics were identified in this code diff.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default CodeDiffAnalyzer; 