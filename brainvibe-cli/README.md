# BrainVibe CLI

A command-line tool for tracking learning progress and visualizing your knowledge graph.

## Installation

```bash
npm install -g brainvibe-cli
```

## Usage

### Initialize a Project

```bash
brainvibe init [--path <path>] [--name <name>]
```

This command initializes a new BrainVibe project. If no path is specified, it uses the current directory. If no name is specified, it prompts for one.

### Track Changes

```bash
brainvibe track [--path <path>]
```

Starts tracking changes in your project. The tool will monitor file changes and update the learning graph accordingly.

### View Learning Graph

```bash
brainvibe graph [--path <path>]
```

Displays your current learning graph, showing commit history and topic progress.

### Mark Topic as Learned

```bash
brainvibe learn <topic> [--path <path>]
```

Marks a topic as learned and updates its progress in the learning graph. You'll be prompted to enter the percentage of completion.

## Project Structure

- `.brainvibe/` - Directory containing project configuration and learning graph data
  - `config.json` - Project configuration
  - `graph.json` - Learning graph data
- `.git/` - Git repository (created if not exists)
  - `hooks/` - Git hooks
    - `post-commit` - Hook that updates the learning graph after each commit

## Development

### Prerequisites

- Node.js >= 14.0.0
- npm >= 6.0.0

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/brainvibe/brainvibe-cli.git
   cd brainvibe-cli
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Available Scripts

- `npm run dev` - Start development environment with a test project
- `npm run build` - Build the project
- `npm test` - Run tests
- `npm run lint` - Run linter
- `npm run format` - Format code
- `npm run clean` - Clean build artifacts
- `npm run prepare` - Prepare project for publishing
- `npm run install-global` - Install CLI tool globally
- `npm run uninstall-global` - Uninstall CLI tool globally

### Development Workflow

1. Make your changes in the `src` directory
2. Run tests: `npm test`
3. Format code: `npm run format`
4. Run linter: `npm run lint`
5. Build project: `npm run build`
6. Test locally: `npm run dev`

### Publishing

1. Update version in `package.json`
2. Run: `npm run publish`

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

MIT 