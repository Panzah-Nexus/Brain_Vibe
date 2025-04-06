import { Link } from 'react-router-dom';

const CLIDocsPage = () => {
  return (
    <div className="cli-docs-page">
      <header>
        <h1>BrainVibe CLI Documentation</h1>
        <Link to="/projects">← Back to Projects</Link>
      </header>
      
      <section className="cli-section">
        <h2>Overview</h2>
        <p>The BrainVibe CLI allows you to track code changes in your projects and automatically extract learning topics in real-time. It uses a "shadow Git" approach to monitor changes and analyze them.</p>
      </section>
      
      <section className="cli-section">
        <h2>Installation</h2>
        <div className="code-block">
          <pre><code>
            cd cli<br/>
            pip install -e .
          </code></pre>
        </div>
      </section>
      
      <section className="cli-section">
        <h2>Getting Started</h2>
        <ol className="steps">
          <li>
            <h3>Create a project in the web interface</h3>
            <p>Go to the <Link to="/projects">Projects page</Link> and create a new project.</p>
          </li>
          <li>
            <h3>Find your Project ID</h3>
            <p>After creating a project, the Project ID is displayed prominently on the project details page.</p>
            <div className="note-box">
              <strong>Note:</strong> The Project ID is a unique identifier (e.g., <code>3f7a9d2b</code>) that connects your local repository to the web interface.
            </div>
          </li>
          <li>
            <h3>Initialize BrainVibe in your project</h3>
            <div className="code-block">
              <pre><code>
                cd /path/to/your/project<br/>
                brainvibe init --project-id {'<project_id>'}
              </code></pre>
            </div>
            <p>This will:</p>
            <ul>
              <li>Create a <code>.brainvibe</code> directory with configuration</li>
              <li>Initialize Git if not already present</li>
              <li>Create an initial commit if needed</li>
            </ul>
          </li>
          <li>
            <h3>Start tracking changes</h3>
            <div className="code-block">
              <pre><code>
                brainvibe track --watch
              </code></pre>
            </div>
            <p>This will continuously track changes in your project and analyze them with BrainVibe.</p>
          </li>
        </ol>
      </section>
      
      <section className="cli-section">
        <h2>Commands</h2>
        <div className="command">
          <h3>init</h3>
          <p>Initialize BrainVibe in a project directory.</p>
          <div className="code-block">
            <pre><code>
              brainvibe init --project-id {'<project_id>'} [--api-url {'<api_url>'}]
            </code></pre>
          </div>
          <h4>Options:</h4>
          <ul>
            <li><code>--project-id</code>: Required. The project ID from the web interface.</li>
            <li><code>--api-url</code>: Optional. The URL of the BrainVibe API. Default: http://localhost:8000/api</li>
          </ul>
        </div>
        
        <div className="command">
          <h3>track</h3>
          <p>Track code changes in a project and analyze them.</p>
          <div className="code-block">
            <pre><code>
              brainvibe track [--watch] [--one-shot]
            </code></pre>
          </div>
          <h4>Options:</h4>
          <ul>
            <li><code>--watch</code>: Watch for file changes continuously.</li>
            <li><code>--one-shot</code>: Run analysis once and exit.</li>
          </ul>
        </div>
      </section>
      
      <section className="cli-section">
        <h2>How It Works</h2>
        <p>The BrainVibe CLI uses the following approach:</p>
        <ol>
          <li>When you run <code>brainvibe track</code>, it monitors your project directory for changes.</li>
          <li>When changes are detected, it stages them using Git and creates temporary commits.</li>
          <li>It extracts diffs from these commits and sends them to the BrainVibe API.</li>
          <li>The API analyzes the diffs using the Gemini API to identify programming topics.</li>
          <li>Topics are added to your project and visible in the web interface.</li>
        </ol>
      </section>
      
      <section className="cli-section">
        <h2>Workflow</h2>
        <ol>
          <li>Create a project in the web UI to get a project_id</li>
          <li>Run the CLI tool in your code folder with that project_id</li>
          <li>The CLI sends code changes to the backend for analysis</li>
          <li>Topics appear in the web interface for that project</li>
          <li>Mark topics as learned as you progress</li>
        </ol>
      </section>
    </div>
  );
};

export default CLIDocsPage; 