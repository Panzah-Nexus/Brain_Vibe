import React, { useState } from 'react';
import { analyzeDiff } from '../services/api';

const CodeDiffAnalyzer = ({ projectId, onAnalysisComplete }) => {
  const [formData, setFormData] = useState({
    git_diff: '',
    prompt: '',
    ai_output: ''
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
      
      const response = await analyzeDiff(projectId, formData);
      
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